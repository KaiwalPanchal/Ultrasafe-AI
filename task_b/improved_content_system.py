"""
Improved Content Transformation System
Follows the pattern: Master Content Generation → Style Transformation → Human Verification
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Configuration
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

@dataclass
class MasterContent:
    """Master content with factual verification"""
    title: str
    content: str
    facts: List[str]
    sources: List[str]
    verified: bool = False
    verification_notes: str = ""

class ImprovedContentSystem:
    """Improved system following the master content → style transformation pattern"""
    
    def __init__(self):
        self.llm = llm
        
        # Master content generation prompt (following your pattern)
        self.master_content_prompt = PromptTemplate(
            input_variables=["topic_title"],
            template="""
You are an expert content creator tasked with generating comprehensive, factually accurate master content.

TOPIC: {topic_title}

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

Provide the content in this JSON format:
{{
    "content": "The full master content...",
    "facts": [
        "Fact 1 with source",
        "Fact 2 with source",
        "Fact 3 with source"
    ],
    "sources": [
        "Source 1",
        "Source 2",
        "Source 3"
    ]
}}

MASTER CONTENT:
"""
        )
    
    def generate_master_content(self, title: str) -> MasterContent:
        """Generate factual master content from title"""
        print(f"Generating master content for: '{title}'")
        
        try:
            # Create the prompt
            prompt = self.master_content_prompt.format(topic_title=title)
            
            # Generate content
            messages = [
                SystemMessage(content="You are an expert content creator focused on accuracy and comprehensiveness."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            try:
                data = json.loads(response.content)
                master_content = MasterContent(
                    title=title,
                    content=data.get('content', ''),
                    facts=data.get('facts', []),
                    sources=data.get('sources', [])
                )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                master_content = MasterContent(
                    title=title,
                    content=response.content,
                    facts=[],
                    sources=[]
                )
            
            return master_content
            
        except Exception as e:
            print(f"Error generating master content: {e}")
            return MasterContent(
                title=title,
                content=f"Error generating content: {str(e)}",
                facts=[],
                sources=[]
            )
    
    def human_verify_facts(self, master_content: MasterContent) -> MasterContent:
        """Human-in-the-loop factual verification"""
        print(f"\nHUMAN VERIFICATION REQUIRED")
        print("="*50)
        print(f"Title: {master_content.title}")
        print(f"Content Length: {len(master_content.content)} characters")
        
        if master_content.facts:
            print(f"\nFACTS TO VERIFY:")
            for i, fact in enumerate(master_content.facts, 1):
                print(f"{i}. {fact}")
        
        if master_content.sources:
            print(f"\nSOURCES:")
            for i, source in enumerate(master_content.sources, 1):
                print(f"{i}. {source}")
        
        print(f"\nGENERATED CONTENT:")
        print("-"*40)
        print(master_content.content[:500] + "..." if len(master_content.content) > 500 else master_content.content)
        print("-"*40)
        
        # Human verification
        while True:
            choice = input("\nIs this content factually accurate? (y/n/edit): ").strip().lower()
            
            if choice in ['y', 'yes']:
                master_content.verified = True
                master_content.verification_notes = "Human verified as accurate"
                print("Content verified as factually accurate!")
                break
                
            elif choice in ['n', 'no']:
                master_content.verified = False
                notes = input("Please provide verification notes: ").strip()
                master_content.verification_notes = notes
                print("Content marked as needing revision")
                break
                
            elif choice == 'edit':
                print("EDIT MODE - Enter corrections:")
                corrections = input("Corrections: ").strip()
                master_content.verification_notes = f"Edited: {corrections}"
                master_content.verified = True
                print("Content edited and verified!")
                break
                
            else:
                print("Invalid choice. Please enter 'y', 'n', or 'edit'")
        
        return master_content
    
    def transform_master_content(self, master_content: MasterContent, target_format: str, 
                               target_style: str, target_complexity: str) -> Dict[str, Any]:
        """Transform verified master content using the transformation system, passing topic for stricter RAG retrieval"""
        if not master_content.verified:
            print("Cannot transform unverified content. Please verify facts first.")
            return {'success': False, 'error': 'Content not verified'}
        
        print(f"\nTransforming verified master content...")
        print(f"   Format: {target_format}")
        print(f"   Style: {target_style}")
        print(f"   Complexity: {target_complexity}")
        
        # Extract topic from title (normalize: lowercase, replace spaces with underscores)
        topic = master_content.title.strip().lower().replace(' ', '_')
        
        # Import here to avoid circular imports
        from content_transformation_system import ContentTransformationSystem
        transformation_system = ContentTransformationSystem()
        
        # Use the transformation system, now passing topic for stricter RAG retrieval
        result = transformation_system.transform_content(
            content=master_content.content,
            target_format=target_format,
            target_style=target_style,
            target_complexity=target_complexity,
            target_topic=topic
        )
        
        # Add master content metadata to result
        if result['success']:
            result['master_content'] = {
                'title': master_content.title,
                'verified': master_content.verified,
                'verification_notes': master_content.verification_notes,
                'facts': master_content.facts,
                'sources': master_content.sources
            }
        
        return result
    
    def generate_and_transform(self, title: str, target_format: str, target_style: str, 
                             target_complexity: str, skip_verification: bool = False) -> Dict[str, Any]:
        """Complete workflow: Generate → Verify → Transform"""
        
        # Step 1: Generate master content
        print("🚀 STEP 1: Generating Master Content")
        master_content = self.generate_master_content(title)
        
        if not master_content.content or "Error" in master_content.content:
            return {'success': False, 'error': 'Failed to generate master content'}
        
        # Step 2: Human verification (unless skipped)
        if not skip_verification:
            print("\n🚀 STEP 2: Human Factual Verification")
            master_content = self.human_verify_facts(master_content)
            
            if not master_content.verified:
                return {
                    'success': False, 
                    'error': 'Content verification failed',
                    'master_content': asdict(master_content)
                }
        else:
            print("\n⏭️ SKIPPING: Human verification (auto-verified)")
            master_content.verified = True
            master_content.verification_notes = "Auto-verified (skipped)"
        
        # Step 3: Transform to target style/format
        print("\n🚀 STEP 3: Style Transformation")
        result = self.transform_master_content(master_content, target_format, target_style, target_complexity)
        
        return result

class ImprovedInteractiveCLI:
    """Improved interactive CLI with human verification"""
    
    def __init__(self):
        self.system = ImprovedContentSystem()
        self.formats = {
            '1': 'blog_post', '2': 'linkedin_post', '3': 'twitter_thread',
            '4': 'email_newsletter', '5': 'podcast_script'
        }
        self.styles = {
            '1': 'gen_z', '2': 'millennial', '3': 'enthusiastic_and_motivational',
            '4': 'formal_professional', '5': 'casual_conversational',
            '6': 'yoda_star_wars', '7': 'sherlock_holmes', '8': 'tony_stark_iron_man'
        }
        self.complexities = {
            '1': 'newbie', '2': 'knows_a_little', '3': 'expert'
        }
        
        self.format_names = {
            'blog_post': 'Blog Post', 'linkedin_post': 'LinkedIn Post',
            'twitter_thread': 'Twitter Thread', 'email_newsletter': 'Email Newsletter',
            'podcast_script': 'Podcast Script'
        }
        
        self.style_names = {
            'gen_z': 'Gen Z', 'millennial': 'Millennial',
            'enthusiastic_and_motivational': 'Enthusiastic & Motivational',
            'formal_professional': 'Formal Professional',
            'casual_conversational': 'Casual Conversational',
            'yoda_star_wars': 'Yoda (Star Wars)', 'sherlock_holmes': 'Sherlock Holmes',
            'tony_stark_iron_man': 'Tony Stark (Iron Man)'
        }
        
        self.complexity_names = {
            'newbie': 'Newbie', 'knows_a_little': 'Knows a Little', 'expert': 'Expert'
        }
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🎭 IMPROVED CONTENT TRANSFORMATION SYSTEM")
        print("="*60)
        print("1. Generate & Transform (with human verification)")
        print("2. Generate & Transform (auto-verified)")
        print("3. Transform existing master content")
        print("4. Exit")
        print("-"*60)
    
    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """Get user choice with validation"""
        while True:
            choice = input(prompt).strip()
            if choice in valid_choices:
                return choice
            print(f"❌ Invalid choice. Please enter one of: {', '.join(valid_choices)}")
    
    def select_format(self) -> str:
        """Let user select output format"""
        print("\n📝 SELECT OUTPUT FORMAT:")
        print("-"*30)
        for key, format_name in self.format_names.items():
            print(f"{list(self.formats.keys())[list(self.formats.values()).index(key)]}. {format_name}")
        
        choice = self.get_user_choice("\nEnter format choice (1-5): ", list(self.formats.keys()))
        selected_format = self.formats[choice]
        print(f"✅ Selected: {self.format_names[selected_format]}")
        return selected_format
    
    def select_style(self) -> str:
        """Let user select style"""
        print("\n🎨 SELECT STYLE:")
        print("-"*30)
        for key, style_name in self.style_names.items():
            print(f"{list(self.styles.keys())[list(self.styles.values()).index(key)]}. {style_name}")
        
        choice = self.get_user_choice("\nEnter style choice (1-8): ", list(self.styles.keys()))
        selected_style = self.styles[choice]
        print(f"✅ Selected: {self.style_names[selected_style]}")
        return selected_style
    
    def select_complexity(self) -> str:
        """Let user select complexity level"""
        print("\n🧠 SELECT COMPLEXITY LEVEL:")
        print("-"*30)
        for key, complexity_name in self.complexity_names.items():
            print(f"{list(self.complexities.keys())[list(self.complexities.values()).index(key)]}. {complexity_name}")
        
        choice = self.get_user_choice("\nEnter complexity choice (1-3): ", list(self.complexities.keys()))
        selected_complexity = self.complexities[choice]
        print(f"✅ Selected: {self.complexity_names[selected_complexity]}")
        return selected_complexity
    
    def get_title_input(self) -> str:
        """Get title from user"""
        print("\n📝 ENTER TITLE:")
        print("-"*30)
        title = input("Title: ").strip()
        return title
    
    def handle_generate_and_transform(self, skip_verification: bool = False):
        """Handle generate and transform workflow"""
        print(f"\n🎯 GENERATE & TRANSFORM {'(AUTO-VERIFIED)' if skip_verification else '(WITH VERIFICATION)'}")
        print("="*60)
        
        # Get inputs
        title = self.get_title_input()
        if not title:
            print("❌ No title provided")
            return
        
        target_format = self.select_format()
        target_style = self.select_style()
        target_complexity = self.select_complexity()
        
        # Execute workflow
        result = self.system.generate_and_transform(
            title=title,
            target_format=target_format,
            target_style=target_style,
            target_complexity=target_complexity,
            skip_verification=skip_verification
        )
        
        # Display results
        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"📊 Quality Score: {result['quality_metrics']['overall_quality_score']:.2f}/1.0")
            print(f"🔄 Iterations: {result['iterations']}")
            
            if 'master_content' in result:
                mc = result['master_content']
                print(f"📝 Master Content: {mc['title']}")
                print(f"✅ Verified: {mc['verified']}")
                if mc['facts']:
                    print(f"📊 Facts: {len(mc['facts'])} verified")
            
            print(f"\n📝 TRANSFORMED CONTENT:")
            print("="*60)
            print(result['transformed_content'])
            print("="*60)
            
            # Show quality breakdown
            metrics = result['quality_metrics']
            print(f"\n📊 Quality Breakdown:")
            print(f"   Factual Accuracy: {metrics['factual_accuracy_score']:.2f}")
            print(f"   Style Adherence: {metrics['style_adherence_score']:.2f}")
            print(f"   Format Compliance: {metrics['format_compliance_score']:.2f}")
            print(f"   Complexity Match: {metrics['complexity_match_score']:.2f}")
            print(f"   Readability: {metrics['readability_score']:.2f}")
            print(f"   Engagement: {metrics['engagement_score']:.2f}")
        else:
            print(f"❌ Failed: {result['error']}")
            if 'master_content' in result:
                print(f"📝 Master content generated but not verified")
    
    def run(self):
        """Run the improved interactive CLI"""
        print("🚀 Welcome to the Improved Content Transformation System!")
        print("This system follows the pattern: Master Content → Human Verification → Style Transformation")
        
        # Check environment
        if not os.getenv("ULTRASAFE_API_KEY"):
            print("❌ ULTRASAFE_API_KEY environment variable not set")
            return
        
        # Main loop
        while True:
            self.display_menu()
            choice = self.get_user_choice("Enter your choice (1-4): ", ['1', '2', '3', '4'])
            
            if choice == '1':
                self.handle_generate_and_transform(skip_verification=False)
            elif choice == '2':
                self.handle_generate_and_transform(skip_verification=True)
            elif choice == '3':
                print("🔄 Transform existing master content - Not implemented yet")
            elif choice == '4':
                print("👋 Thank you for using the Improved Content Transformation System!")
                break
            
            # Ask if user wants to continue
            if choice in ['1', '2', '3']:
                continue_choice = input("\nWould you like to perform another operation? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Thank you for using the Improved Content Transformation System!")
                    break

def main():
    """Main function"""
    cli = ImprovedInteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main() 