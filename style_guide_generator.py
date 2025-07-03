from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import json
from typing import List, Optional
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel as LCBaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

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
    temperature=0.0,
    max_tokens=1000,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

# ---------------------------------------------------------------------------
# Style Guide Generation Configuration
# ---------------------------------------------------------------------------

FORMATS = [
    "Blog Post",
    "LinkedIn Post",
    "Twitter Thread",
    "Email Newsletter",
    "Podcast Script",
]

STYLES = [
    "Gen Z",
    "Millennial",
    "Enthusiastic & Motivational",
    "Formal Professional",
    "Casual Conversational",
    "Yoda (Star Wars)",
    "Sherlock Holmes",
    "Tony Stark (Iron Man)",
]

COMPLEXITY_LEVELS = ["Newbie", "Knows a Little", "Expert"]

# ---------------------------------------------------------------------------
# Style Guide Generation Prompt Template
# ---------------------------------------------------------------------------

STYLE_GUIDE_PROMPT = PromptTemplate(
    template="""
You are an expert content strategist tasked with creating a comprehensive style guide for content transformation.

Create a detailed style guide for the following combination:
- Format: {format}
- Style: {style}
- Complexity Level: {complexity}

Your style guide should include:

1. **Overview**: Brief description of this specific combination
2. **Key Characteristics**: 
   - Tone and voice
   - Language patterns
   - Sentence structure
   - Vocabulary level
   - Specific style elements

3. **Format-Specific Guidelines**:
   - Structure requirements
   - Length considerations
   - Visual elements (if applicable)
   - Platform-specific considerations

4. **Complexity Adaptations**:
   - How to adjust technical depth
   - Vocabulary considerations
   - Explanation strategies

5. **Style-Specific Elements**:
   - Unique phrases or expressions
   - Character-specific mannerisms (if applicable)
   - Generational references (if applicable)

6. **Example Phrases**: 5-10 example phrases that exemplify this style
7. **Transformation Tips**: Specific advice for converting content to this style
8. **Quality Indicators**: How to measure if content matches this style

Make this comprehensive but practical for AI agents to use during content transformation.
""",
    input_variables=["format", "style", "complexity"],
)

# ---------------------------------------------------------------------------
# Style Guide Generator Class
# ---------------------------------------------------------------------------


class StyleGuideGenerator:
    def __init__(self, llm: ChatOpenAI, output_dir: str = "style_guides"):
        self.llm = llm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_filename(self, format_name: str, style: str, complexity: str) -> str:
        """Generate a clean filename for the style guide"""
        clean_format = format_name.replace(" ", "_").lower()
        clean_style = (
            style.replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("&", "and")
            .lower()
        )
        clean_complexity = complexity.replace(" ", "_").lower()
        return f"{clean_format}_{clean_style}_{clean_complexity}.txt"

    def generate_single_guide(
        self, format_name: str, style: str, complexity: str
    ) -> str:
        """Generate a single style guide"""
        try:
            prompt = STYLE_GUIDE_PROMPT.format(
                format=format_name, style=style, complexity=complexity
            )

            messages = [
                SystemMessage(
                    content="You are an expert content strategist and style guide creator."
                ),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            print(
                f"Error generating guide for {format_name}-{style}-{complexity}: {str(e)}"
            )
            return f"Error generating style guide: {str(e)}"

    def save_guide(self, content: str, filename: str):
        """Save style guide to file"""
        filepath = self.output_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Saved: {filename}")
        except Exception as e:
            print(f"✗ Error saving {filename}: {str(e)}")

    def generate_all_guides(self):
        """Generate all 120 style guides"""
        total_combinations = len(FORMATS) * len(STYLES) * len(COMPLEXITY_LEVELS)
        current = 0

        print(f"Generating {total_combinations} style guides...")
        print("=" * 50)

        for format_name in FORMATS:
            for style in STYLES:
                for complexity in COMPLEXITY_LEVELS:
                    current += 1
                    print(
                        f"[{current}/{total_combinations}] Generating: {format_name} - {style} - {complexity}"
                    )

                    # Generate the style guide content
                    content = self.generate_single_guide(format_name, style, complexity)

                    # Create filename and save
                    filename = self.generate_filename(format_name, style, complexity)
                    self.save_guide(content, filename)

                    print(f"   → Saved as: {filename}")
                    print()

        print("=" * 50)
        print(f"✓ All {total_combinations} style guides generated successfully!")
        print(f"✓ Files saved in: {self.output_dir.absolute()}")

    def generate_index_file(self):
        """Generate an index file listing all combinations"""
        index_content = "# Style Guide Index\n\n"
        index_content += f"Total Combinations: {len(FORMATS) * len(STYLES) * len(COMPLEXITY_LEVELS)}\n\n"

        index_content += "## All Combinations:\n\n"

        for format_name in FORMATS:
            for style in STYLES:
                for complexity in COMPLEXITY_LEVELS:
                    filename = self.generate_filename(format_name, style, complexity)
                    index_content += f"- **{format_name}** | **{style}** | **{complexity}** → `{filename}`\n"

        index_path = self.output_dir / "index.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        print(f"✓ Index file created: {index_path}")


# ---------------------------------------------------------------------------
# Main execution function
# ---------------------------------------------------------------------------


def generate_style_guides():
    """Main function to generate all style guides"""
    generator = StyleGuideGenerator(llm)

    # Generate all style guides
    generator.generate_all_guides()

    # Generate index file
    generator.generate_index_file()


# ---------------------------------------------------------------------------
# CLI execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Style Guide Generator for Content Transformation RAG System")
    print("=" * 60)

    # Verify LLM connection
    try:
        test_response = llm.invoke([HumanMessage(content="Test connection")])
        print("✓ LLM connection verified")
    except Exception as e:
        print(f"✗ LLM connection failed: {str(e)}")
        exit(1)

    # Generate all style guides
    generate_style_guides()

    print("\n" + "=" * 60)
    print("Style guide generation complete!")
    print("These files can now be used to build your RAG knowledge base.")
