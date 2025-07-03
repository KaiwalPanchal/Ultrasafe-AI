from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

from langchain_openai import ChatOpenAI
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
    temperature=0.3,  # Slightly higher for style variation
    max_tokens=1500,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

class StyleTransformer:
    def __init__(self):
        self.llm = llm
        self.master_content_dir = Path("master_content")
        self.style_guides_dir = Path("style_guides")
        self.output_dir = Path("generated_stylized_content")
        self.output_dir.mkdir(exist_ok=True)
        
        # Style transformation prompt
        self.transformation_prompt = PromptTemplate(
            input_variables=["master_content", "style_guide", "format_type", "style_name", "complexity_level"],
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
            """
        )
    
    def load_master_content_files(self) -> List[Dict[str, str]]:
        """Load all master content files"""
        master_files = []
        
        if not self.master_content_dir.exists():
            print(f"Master content directory not found: {self.master_content_dir}")
            return []
        
        for file_path in self.master_content_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Extract topic from filename
                topic_filename = file_path.stem
                
                # Extract topic title from content (first line after TOPIC:)
                topic_match = re.search(r'TOPIC:\s*(.+)', content)
                topic_title = topic_match.group(1).strip() if topic_match else topic_filename
                
                # Extract actual content (after the separator line)
                content_parts = content.split('='*80)
                actual_content = content_parts[1].strip() if len(content_parts) > 1 else content
                
                master_files.append({
                    'filename': topic_filename,
                    'title': topic_title,
                    'content': actual_content,
                    'file_path': str(file_path)
                })
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {str(e)}")
                continue
        
        return master_files
    
    def load_style_guides(self) -> List[Dict[str, str]]:
        """Load all style guide files"""
        style_guides = []
        
        if not self.style_guides_dir.exists():
            print(f"Style guides directory not found: {self.style_guides_dir}")
            return []
        
        for file_path in self.style_guides_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Parse filename to extract format, style, and complexity
                filename = file_path.stem
                parts = self.parse_style_filename(filename)
                
                if parts:
                    style_guides.append({
                        'filename': filename,
                        'format': parts['format'],
                        'style': parts['style'],
                        'complexity': parts['complexity'],
                        'content': content,
                        'file_path': str(file_path)
                    })
                
            except Exception as e:
                print(f"❌ Error loading style guide {file_path}: {str(e)}")
                continue
        
        return style_guides
    
    def parse_style_filename(self, filename: str) -> Dict[str, str]:
        """Parse style guide filename to extract components"""
        # Expected format: format_style_complexity
        # e.g., blog_post_gen_z_newbie, linkedin_post_formal_professional_expert
        
        filename_lower = filename.lower()
        
        # Define mappings
        formats = {
            'blog_post': 'Blog Post',
            'linkedin_post': 'LinkedIn Post', 
            'twitter_thread': 'Twitter Thread',
            'email_newsletter': 'Email Newsletter',
            'podcast_script': 'Podcast Script'
        }
        
        styles = {
            'gen_z': 'Gen Z',
            'millennial': 'Millennial',
            'enthusiastic_and_motivational': 'Enthusiastic & Motivational',
            'formal_professional': 'Formal Professional',
            'casual_conversational': 'Casual Conversational',
            'yoda_star_wars': 'Yoda (Star Wars)',
            'sherlock_holmes': 'Sherlock Holmes',
            'tony_stark_iron_man': 'Tony Stark (Iron Man)'
        }
        
        complexities = {
            'newbie': 'Newbie',
            'knows_a_little': 'Knows a Little',
            'expert': 'Expert'
        }
        
        # Find format
        format_found = None
        for key, value in formats.items():
            if filename_lower.startswith(key):
                format_found = value
                filename_lower = filename_lower[len(key):].lstrip('_')
                break
        
        if not format_found:
            return None
        
        # Find complexity (from the end)
        complexity_found = None
        for key, value in complexities.items():
            if filename_lower.endswith(key):
                complexity_found = value
                filename_lower = filename_lower[:-len(key)].rstrip('_')
                break
        
        if not complexity_found:
            return None
        
        # Remaining should be style
        style_found = None
        for key, value in styles.items():
            if key in filename_lower:
                style_found = value
                break
        
        if not style_found:
            return None
        
        return {
            'format': format_found,
            'style': style_found,
            'complexity': complexity_found
        }
    
    def transform_content(self, master_content: Dict[str, str], style_guide: Dict[str, str]) -> str:
        """Transform master content according to style guide"""
        try:
            prompt = self.transformation_prompt.format(
                master_content=master_content['content'],
                style_guide=style_guide['content'],
                format_type=style_guide['format'],
                style_name=style_guide['style'],
                complexity_level=style_guide['complexity']
            )
            
            messages = [
                SystemMessage(content="You are an expert content transformer who maintains factual accuracy while adapting style and format."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"❌ Error transforming content: {str(e)}")
            return f"Error: {str(e)}"
    
    def create_output_filename(self, topic_filename: str, style_guide: Dict[str, str]) -> str:
        """Create output filename for transformed content"""
        # Convert to lowercase and replace spaces/special chars
        format_clean = re.sub(r'[^\w]', '_', style_guide['format'].lower())
        style_clean = re.sub(r'[^\w]', '_', style_guide['style'].lower())
        complexity_clean = re.sub(r'[^\w]', '_', style_guide['complexity'].lower())
        
        return f"{format_clean}_{style_clean}_{complexity_clean}.txt"
    
    def save_transformed_content(self, topic: Dict[str, str], style_guide: Dict[str, str], transformed_content: str):
        """Save transformed content to organized folder structure"""
        # Create topic folder
        topic_folder = self.output_dir / topic['filename']
        topic_folder.mkdir(exist_ok=True)
        
        # Create filename
        output_filename = self.create_output_filename(topic['filename'], style_guide)
        output_path = topic_folder / output_filename
        
        # Create metadata header
        metadata = f"""TOPIC: {topic['title']}
FORMAT: {style_guide['format']}
STYLE: {style_guide['style']}
COMPLEXITY: {style_guide['complexity']}
GENERATED FROM: {topic['file_path']}
STYLE GUIDE: {style_guide['file_path']}
{'='*80}

"""
        
        # Save file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(metadata + transformed_content)
        
        print(f"Saved: {output_path}")
    
    def transform_all_content(self):
        """Transform all master content with all style guides"""
        print("Starting Style Transformation...")
        
        # Load master content and style guides
        master_contents = self.load_master_content_files()
        style_guides = self.load_style_guides()
        
        print(f"Loaded {len(master_contents)} master content files")
        print(f"Loaded {len(style_guides)} style guides")
        
        if not master_contents or not style_guides:
            print("No content to transform. Ensure master content and style guides exist.")
            return
        
        total_combinations = len(master_contents) * len(style_guides)
        current = 0
        
        print(f"Total transformations to perform: {total_combinations}")
        
        # Transform each master content with each style guide
        for master_content in master_contents:
            print(f"\nProcessing topic: {master_content['title']}")
            
            for style_guide in style_guides:
                current += 1
                style_name = f"{style_guide['format']} - {style_guide['style']} - {style_guide['complexity']}"
                
                print(f"  [{current}/{total_combinations}] Applying: {style_name}")
                
                # Check if already exists
                topic_folder = self.output_dir / master_content['filename']
                output_filename = self.create_output_filename(master_content['filename'], style_guide)
                output_path = topic_folder / output_filename
                
                if output_path.exists():
                    print(f"    Skipping (already exists)")
                    continue
                
                try:
                    # Transform content
                    transformed_content = self.transform_content(master_content, style_guide)
                    
                    # Save transformed content
                    self.save_transformed_content(master_content, style_guide, transformed_content)
                    
                except Exception as e:
                    print(f"    Failed: {str(e)}")
                    continue
        
        print(f"\nStyle Transformation Complete!")
        print(f"Content saved in: {self.output_dir}")
    
    def get_transformation_stats(self):
        """Get statistics about transformed content"""
        if not self.output_dir.exists():
            print("No transformed content found.")
            return
        
        topic_folders = [f for f in self.output_dir.iterdir() if f.is_dir()]
        
        print(f"\nTransformation Statistics:")
        print(f"  Topics processed: {len(topic_folders)}")
        
        total_files = 0
        for folder in topic_folders:
            files_count = len(list(folder.glob("*.txt")))
            total_files += files_count
            print(f"    {folder.name}: {files_count} variations")
        
        print(f"  Total transformed files: {total_files}")

def main():
    """Main function to run the style transformer"""
    transformer = StyleTransformer()
    
    try:
        # Transform all content
        transformer.transform_all_content()
        
        # Show statistics
        transformer.get_transformation_stats()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()