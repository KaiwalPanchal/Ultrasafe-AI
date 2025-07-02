import os
import re
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# IMPORTANT: Set the number of parallel workers.
# Start with a low number (e.g., 5-8) to avoid API rate limits.
# You can increase this if you have a higher-tier API plan.
MAX_WORKERS = 8

# Input and Output Directories
ORGANIZED_CONTENT_DIR = Path("organized_content")
STYLE_GUIDES_DIR = Path("style_guides")
OUTPUT_DIR = Path("generated_stylized_content")

# ---------------------------------------------------------------------------
# LangChain LLM configuration (UltraSafe backend)
# ---------------------------------------------------------------------------

ULTRASAFE_API_KEY: str | None = os.getenv("ULTRASAFE_API_KEY")
ULTRASAFE_API_BASE: str | None = os.getenv(
    "ULTRASAFE_API_BASE", "https://api.us.inc/usf/v1/hiring/chat/completions"
)

if not ULTRASAFE_API_KEY:
    raise RuntimeError("ULTRASAFE_API_KEY environment variable is not set")

llm = ChatOpenAI(
    model_name="usf1-mini",
    temperature=0.3,
    max_tokens=1500,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

# Shared prompt template for all transformations
TRANSFORMATION_PROMPT = PromptTemplate(
    input_variables=[
        "master_content",
        "style_guide",
        "format_type",
        "style_name",
        "complexity_level",
    ],
    template="""
You are an expert content transformer. Your task is to transform master content according to specific style guidelines while maintaining ALL factual accuracy.

STYLE GUIDE TO FOLLOW:
{style_guide}

FORMAT: {format_type}
STYLE: {style_name}
COMPLEXITY: {complexity_level}

MASTER CONTENT TO TRANSFORM:
{master_content}

TRANSFORMATION REQUIREMENTS:
1. **PRESERVE ALL FACTS**: Every statistic, definition, and factual claim must remain exactly accurate
2. **APPLY STYLE**: Transform tone, voice, and presentation according to the style guide
3. **MATCH FORMAT**: Adapt structure for the specified format (blog post, LinkedIn, etc.)
4. **MATCH COMPLEXITY**: Adjust technical depth for the target audience level
5. **MAINTAIN COMPLETENESS**: Include all key information from master content
6. **NATURAL FLOW**: Ensure the transformed content reads naturally in the new style

CRITICAL: Do not add new facts, change statistics, or alter any factual information. Only change HOW the information is presented.

TRANSFORMED CONTENT:
""",
)

# ---------------------------------------------------------------------------
# Helper Functions for Parsing and Loading
# ---------------------------------------------------------------------------


def parse_style_filename(filename: str) -> Dict[str, str] | None:
    """Parse style guide filename to extract components. Case-insensitive."""
    filename_lower = filename.lower()
    formats = {
        "blog_post": "Blog Post",
        "linkedin_post": "LinkedIn Post",
        "twitter_thread": "Twitter Thread",
        "email_newsletter": "Email Newsletter",
        "podcast_script": "Podcast Script",
    }
    styles = {
        "gen_z": "Gen Z",
        "millennial": "Millennial",
        "enthusiastic_and_motivational": "Enthusiastic & Motivational",
        "formal_professional": "Formal Professional",
        "casual_conversational": "Casual Conversational",
        "yoda_star_wars": "Yoda (Star Wars)",
        "sherlock_holmes": "Sherlock Holmes",
        "tony_stark_iron_man": "Tony Stark (Iron Man)",
    }
    complexities = {
        "newbie": "Newbie",
        "knows_a_little": "Knows a Little",
        "expert": "Expert",
    }

    found_format, found_style, found_complexity = None, None, None

    for key, value in formats.items():
        if filename_lower.startswith(key):
            found_format = value
            filename_lower = filename_lower[len(key) :].lstrip("_")
            break
    if not found_format:
        return None

    for key, value in complexities.items():
        if filename_lower.endswith(key):
            found_complexity = value
            filename_lower = filename_lower[: -len(key)].rstrip("_")
            break
    if not found_complexity:
        return None

    # The remainder is the style
    for key, value in styles.items():
        if key == filename_lower:
            found_style = value
            break
    if not found_style:
        return None

    return {
        "format": found_format,
        "style": found_style,
        "complexity": found_complexity,
    }


def load_style_guides() -> List[Dict[str, Any]]:
    """Load all style guides from the style guides directory."""
    style_guides = []
    if not STYLE_GUIDES_DIR.is_dir():
        print(f"❌ Style guides directory not found: {STYLE_GUIDES_DIR}")
        return []

    for file_path in STYLE_GUIDES_DIR.glob("*.txt"):
        parts = parse_style_filename(file_path.stem)
        if parts:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            parts["content"] = content
            parts["file_path"] = str(file_path)
            style_guides.append(parts)
    return style_guides


def load_source_topics() -> List[Dict[str, Any]]:
    """Load all source topic files from the organized_content directory."""
    topics = []
    if not ORGANIZED_CONTENT_DIR.is_dir():
        print(f"❌ Organized content directory not found: {ORGANIZED_CONTENT_DIR}")
        return []

    for file_path in ORGANIZED_CONTENT_DIR.glob("**/*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        topic_match = re.search(r"TOPIC:\s*(.+)", content)
        topic_title = topic_match.group(1).strip() if topic_match else file_path.stem
        content_parts = content.split("=" * 80)
        actual_content = content_parts[1].strip() if len(content_parts) > 1 else content

        topics.append(
            {
                "topic_title": topic_title,
                "source_content": actual_content,
                "source_path": file_path,
            }
        )
    return topics


# ---------------------------------------------------------------------------
# Core Transformation Logic
# ---------------------------------------------------------------------------


def perform_single_transformation(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single LLM transformation. This function is called by each worker thread.
    """
    try:
        prompt = TRANSFORMATION_PROMPT.format(
            master_content=job["topic"]["source_content"],
            style_guide=job["style_guide"]["content"],
            format_type=job["style_guide"]["format"],
            style_name=job["style_guide"]["style"],
            complexity_level=job["style_guide"]["complexity"],
        )
        messages = [
            SystemMessage(
                content="You are an expert content transformer who maintains factual accuracy while adapting style and format."
            ),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        job["transformed_content"] = response.content
        job["status"] = "success"
    except Exception as e:
        job["transformed_content"] = f"Error during transformation: {str(e)}"
        job["status"] = "failed"
    return job


def save_transformed_content(result: Dict[str, Any]):
    """Saves the result of a transformation to the correct file and folder."""
    topic_path = result["topic"]["source_path"]
    style_guide = result["style_guide"]

    # Create the nested output directory structure
    # e.g., output/technology_ai/machine_learning_for_beginners/
    category_folder = topic_path.parent.name
    topic_folder_name = topic_path.stem
    output_topic_dir = OUTPUT_DIR / category_folder / topic_folder_name
    output_topic_dir.mkdir(parents=True, exist_ok=True)

    # Create the output filename
    # e.g., blog_post_gen_z_newbie.txt
    format_clean = re.sub(r"[^\w]", "_", style_guide["format"].lower())
    style_clean = re.sub(r"[^\w]", "_", style_guide["style"].lower())
    complexity_clean = re.sub(r"[^\w]", "_", style_guide["complexity"].lower())
    output_filename = f"{format_clean}_{style_clean}_{complexity_clean}.txt"

    output_path = output_topic_dir / output_filename

    # Create metadata header
    metadata = f"""TOPIC: {result["topic"]["topic_title"]}
FORMAT: {style_guide["format"]}
STYLE: {style_guide["style"]}
COMPLEXITY: {style_guide["complexity"]}
SOURCE TOPIC: {str(topic_path)}
SOURCE STYLE GUIDE: {style_guide["file_path"]}
{"=" * 80}

"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(metadata + result["transformed_content"])


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------


def main():
    """Main function to orchestrate the parallel transformation process."""
    print("🚀 Starting Parallel Style Transformer")
    print(f"   - Max parallel workers: {MAX_WORKERS}")
    print(f"   - Input directory: {ORGANIZED_CONTENT_DIR}")
    print(f"   - Output directory: {OUTPUT_DIR}")

    # 1. Load all assets
    start_time = time.time()
    topics = load_source_topics()
    style_guides = load_style_guides()

    if not topics or not style_guides:
        print("❌ Aborting. Could not find topics or style guides.")
        return

    print(f"\n✅ Found {len(topics)} source topics.")
    print(f"✅ Found {len(style_guides)} style guides.")

    # 2. Create the full job list
    jobs_to_process = []
    for topic in topics:
        for style_guide in style_guides:
            # --- Check if the final file already exists to allow resuming ---
            category_folder = topic["source_path"].parent.name
            topic_folder_name = topic["source_path"].stem
            output_topic_dir = OUTPUT_DIR / category_folder / topic_folder_name
            format_clean = re.sub(r"[^\w]", "_", style_guide["format"].lower())
            style_clean = re.sub(r"[^\w]", "_", style_guide["style"].lower())
            complexity_clean = re.sub(r"[^\w]", "_", style_guide["complexity"].lower())
            output_filename = f"{format_clean}_{style_clean}_{complexity_clean}.txt"
            output_path = output_topic_dir / output_filename

            if output_path.exists():
                continue  # Skip this job if the output file is already there

            jobs_to_process.append({"topic": topic, "style_guide": style_guide})

    total_jobs = len(jobs_to_process)
    if total_jobs == 0:
        print("\n🎉 All transformations have already been completed. Nothing to do.")
        return

    print(f"🎯 Total new transformations to perform: {total_jobs}")
    print("-" * 50)

    # 3. Process jobs using a ThreadPoolExecutor
    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all jobs to the pool
        future_to_job = {
            executor.submit(perform_single_transformation, job): job
            for job in jobs_to_process
        }

        # Process results as they complete, with a progress bar
        pbar_desc = f"Transforming {len(topics)} topics"
        for future in tqdm(
            as_completed(future_to_job), total=total_jobs, desc=pbar_desc, unit="file"
        ):
            result = future.result()

            if result["status"] == "success":
                save_transformed_content(result)
                success_count += 1
            else:
                failure_count += 1
                topic_title = result["topic"]["topic_title"]
                style_name = result["style_guide"]["format"]
                print(f"\n❌ FAILED: Topic '{topic_title}' with style '{style_name}'")
                print(f"   Error: {result['transformed_content']}")

    end_time = time.time()

    # 4. Print final summary
    print("\n" + "=" * 50)
    print("🎉 Style Transformation Complete!")
    print(f"   - Total time: {end_time - start_time:.2f} seconds")
    print(f"   - Successful transformations: {success_count}")
    print(f"   - Failed transformations: {failure_count}")
    print(f"📁 All content saved in: {OUTPUT_DIR.resolve()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
