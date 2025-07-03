from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
from typing import List, Dict
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
    temperature=0.2,  # Low temperature for factual consistency
    max_tokens=2000,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

class MasterContentGenerator:
    def __init__(self):
        self.llm = llm
        self.master_content_dir = Path("master_content")
        self.master_content_dir.mkdir(exist_ok=True)
        
        # Master content generation prompt
        self.master_content_prompt = PromptTemplate(
            input_variables=["topic_title", "topic_description"],
            template="""
You are an expert content creator tasked with generating comprehensive, factually accurate master content.

TOPIC: {topic_title}
DESCRIPTION: {topic_description}

Create comprehensive master content that includes:
1. **Overview**: Clear definition and context
2. **Key Facts**: Important, verifiable information and statistics
3. **Core Concepts**: Essential ideas that must be understood
4. **Practical Applications**: Real-world examples and use cases
5. **Common Misconceptions**: Myths to debunk
6. **Expert Insights**: Professional perspectives and tips
7. **Current Trends**: Recent developments (if applicable)
8. **Action Steps**: Practical recommendations

REQUIREMENTS:
- Be factually accurate and cite specific data where possible
- Write 800-1200 words
- Use neutral, informative tone
- Structure content clearly with sections
- Include specific examples and case studies
- Ensure all facts can be verified
- Avoid opinions, focus on established information

MASTER CONTENT:
            """
        )
    
    def parse_topics_from_md(self, md_file_path: str) -> List[Dict[str, str]]:
        """Parse topics from the markdown file"""
        topics = []
        
        with open(md_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all topics (numbered items with ** bold formatting)
        topic_pattern = r'\d+\.\s+\*\*(.+?)\*\*\s+-\s+(.+?)(?=\n\d+\.|\n##|\n---|\Z)'
        matches = re.findall(topic_pattern, content, re.DOTALL)
        
        for match in matches:
            title = match[0].strip()
            description = match[1].strip()
            
            # Create a clean filename
            filename = re.sub(r'[^\w\s-]', '', title.lower())
            filename = re.sub(r'[-\s]+', '_', filename)
            
            topics.append({
                'title': title,
                'description': description,
                'filename': filename
            })
        
        return topics
    
    def generate_master_content(self, topic: Dict[str, str]) -> str:
        """Generate master content for a single topic"""
        try:
            # Create the prompt
            prompt = self.master_content_prompt.format(
                topic_title=topic['title'],
                topic_description=topic['description']
            )
            
            # Generate content
            messages = [
                SystemMessage(content="You are an expert content creator focused on accuracy and comprehensiveness."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"Error generating content for {topic['title']}: {str(e)}")
            return f"Error generating content: {str(e)}"
    
    def save_master_content(self, topic: Dict[str, str], content: str):
        """Save master content to file"""
        filepath = self.master_content_dir / f"{topic['filename']}.txt"
        
        # Create metadata header
        metadata = f"""TOPIC: {topic['title']}
DESCRIPTION: {topic['description']}
GENERATED: {Path(__file__).name}
{'='*80}

"""
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(metadata + content)
        
        print(f"Saved master content: {filepath}")
    
    def generate_all_master_content(self, md_file_path: str):
        """Generate master content for all topics"""
        print("Starting Master Content Generation...")
        
        # Parse topics
        topics = self.parse_topics_from_md(md_file_path)
        print(f"Found {len(topics)} topics to process")
        
        # Generate content for each topic
        for i, topic in enumerate(topics, 1):
            print(f"\nProcessing {i}/{len(topics)}: {topic['title']}")
            
            # Check if already exists
            filepath = self.master_content_dir / f"{topic['filename']}.txt"
            if filepath.exists():
                print(f"Skipping (already exists): {topic['title']}")
                continue
            
            try:
                # Generate master content
                content = self.generate_master_content(topic)
                
                # Save to file
                self.save_master_content(topic, content)
                
            except Exception as e:
                print(f"Failed to process {topic['title']}: {str(e)}")
                continue
        
        print(f"\nMaster Content Generation Complete!")
        print(f"Content saved in: {self.master_content_dir}")
    
    def list_generated_content(self):
        """List all generated master content files"""
        files = list(self.master_content_dir.glob("*.txt"))
        print(f"\nGenerated Master Content Files ({len(files)}):")
        for file in sorted(files):
            print(f"  - {file.name}")
        return files

def main():
    """Main function to run the master content generator"""
    generator = MasterContentGenerator()
    
    # Path to the topics markdown file
    md_file_path = "example_topics_list.md"  # Update this path as needed
    
    if not Path(md_file_path).exists():
        print(f"Error: {md_file_path} not found!")
        print("Please ensure the topics markdown file exists.")
        return
    
    try:
        # Generate all master content
        generator.generate_all_master_content(md_file_path)
        
        # List generated files
        generator.list_generated_content()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()