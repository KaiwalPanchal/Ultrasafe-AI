"""
Interactive CLI for Content Transformation System
User-friendly interface that asks for format, style, and complexity separately
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add the task_b directory to the path
sys.path.append(str(Path(__file__).parent))

from content_transformation_system import ContentTransformationSystem
from langchain_core.messages import HumanMessage

load_dotenv()

class InteractiveCLI:
    """Interactive CLI for content transformation"""
    
    def __init__(self):
        self.system = None
        self.formats = {
            '1': 'blog_post',
            '2': 'linkedin_post', 
            '3': 'twitter_thread',
            '4': 'email_newsletter',
            '5': 'podcast_script'
        }
        
        self.styles = {
            '1': 'gen_z',
            '2': 'millennial',
            '3': 'enthusiastic_and_motivational',
            '4': 'formal_professional',
            '5': 'casual_conversational',
            '6': 'yoda_star_wars',
            '7': 'sherlock_holmes',
            '8': 'tony_stark_iron_man'
        }
        
        self.complexities = {
            '1': 'newbie',
            '2': 'knows_a_little',
            '3': 'expert'
        }
        
        self.format_names = {
            'blog_post': 'Blog Post',
            'linkedin_post': 'LinkedIn Post',
            'twitter_thread': 'Twitter Thread',
            'email_newsletter': 'Email Newsletter',
            'podcast_script': 'Podcast Script'
        }
        
        self.style_names = {
            'gen_z': 'Gen Z',
            'millennial': 'Millennial',
            'enthusiastic_and_motivational': 'Enthusiastic & Motivational',
            'formal_professional': 'Formal Professional',
            'casual_conversational': 'Casual Conversational',
            'yoda_star_wars': 'Yoda (Star Wars)',
            'sherlock_holmes': 'Sherlock Holmes',
            'tony_stark_iron_man': 'Tony Stark (Iron Man)'
        }
        
        self.complexity_names = {
            'newbie': 'Newbie',
            'knows_a_little': 'Knows a Little',
            'expert': 'Expert'
        }
    
    def initialize_system(self):
        """Initialize the transformation system"""
        print("Initializing Content Transformation System...")
        try:
            self.system = ContentTransformationSystem()
            print("System initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize system: {e}")
            return False
        return True
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("CONTENT TRANSFORMATION SYSTEM")
        print("="*60)
        print("1. Transform existing content")
        print("2. Generate content from title")
        print("3. Convert between styles")
        print("4. Exit")
        print("-"*60)
    
    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """Get user choice with validation"""
        while True:
            choice = input(prompt).strip()
            if choice in valid_choices:
                return choice
            print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")
    
    def select_format(self) -> str:
        """Let user select output format"""
        print("\nSELECT OUTPUT FORMAT:")
        print("-"*30)
        for key, format_name in self.format_names.items():
            print(f"{list(self.formats.keys())[list(self.formats.values()).index(key)]}. {format_name}")
        
        choice = self.get_user_choice("\nEnter format choice (1-5): ", list(self.formats.keys()))
        selected_format = self.formats[choice]
        print(f"Selected: {self.format_names[selected_format]}")
        return selected_format
    
    def select_style(self) -> str:
        """Let user select style"""
        print("\nSELECT STYLE:")
        print("-"*30)
        for key, style_name in self.style_names.items():
            print(f"{list(self.styles.keys())[list(self.styles.values()).index(key)]}. {style_name}")
        
        choice = self.get_user_choice("\nEnter style choice (1-8): ", list(self.styles.keys()))
        selected_style = self.styles[choice]
        print(f"Selected: {self.style_names[selected_style]}")
        return selected_style
    
    def select_complexity(self) -> str:
        """Let user select complexity level"""
        print("\nSELECT COMPLEXITY LEVEL:")
        print("-"*30)
        for key, complexity_name in self.complexity_names.items():
            print(f"{list(self.complexities.keys())[list(self.complexities.values()).index(key)]}. {complexity_name}")
        
        choice = self.get_user_choice("\nEnter complexity choice (1-3): ", list(self.complexities.keys()))
        selected_complexity = self.complexities[choice]
        print(f"Selected: {self.complexity_names[selected_complexity]}")
        return selected_complexity
    
    def get_content_input(self) -> str:
        """Get content from user"""
        print("\nENTER YOUR CONTENT:")
        print("-"*30)
        print("(Type your content below. Press Enter twice when finished)")
        
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        content = "\n".join(lines[:-1])  # Remove the last empty line
        return content.strip()
    
    def get_title_input(self) -> str:
        """Get title from user"""
        print("\nENTER TITLE:")
        print("-"*30)
        title = input("Title: ").strip()
        return title
    
    def generate_content_from_title(self, title: str) -> str:
        """Generate factual content from title"""
        print(f"\nGenerating factual content for: '{title}'")
        
        # Simple content generation prompt
        generation_prompt = f"""
        Generate factual, informative content about: {title}
        
        Requirements:
        - Provide accurate, factual information
        - Include relevant statistics and data where appropriate
        - Structure as a comprehensive overview
        - Include key points and important details
        - Write in a neutral, informative tone
        - Aim for 300-500 words
        
        Content:
        """
        
        try:
            # Use the system's LLM to generate content
            response = self.system.llm.invoke([HumanMessage(content=generation_prompt)])
            generated_content = response.content.strip()
            
            # Format the content nicely
            formatted_content = f"{title}\n\n{generated_content}"
            return formatted_content
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"{title}\n\n[Content generation failed. Please provide your own content.]"
    
    def transform_content(self, content: str, target_format: str, target_style: str, target_complexity: str):
        """Transform content using the system"""
        print(f"\nTransforming content...")
        print(f"   Format: {self.format_names[target_format]}")
        print(f"   Style: {self.style_names[target_style]}")
        print(f"   Complexity: {self.complexity_names[target_complexity]}")
        
        try:
            result = self.system.transform_content(
                content=content,
                target_format=target_format,
                target_style=target_style,
                target_complexity=target_complexity
            )
            
            if result['success']:
                print(f"\n✅ Transformation successful!")
                print(f"📊 Quality Score: {result['quality_metrics']['overall_quality_score']:.2f}/1.0")
                print(f"🔄 Iterations: {result['iterations']}")
                
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
                
                if metrics['issues_found']:
                    print(f"\n⚠️ Issues Found:")
                    for issue in metrics['issues_found'][:3]:
                        print(f"   - {issue}")
                
                if metrics['suggestions']:
                    print(f"\n💡 Suggestions:")
                    for suggestion in metrics['suggestions'][:3]:
                        print(f"   - {suggestion}")
                
                return result['transformed_content']
            else:
                print(f"❌ Transformation failed: {result['error']}")
                return None
                
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return None
    
    def handle_transform_existing_content(self):
        """Handle transformation of existing content"""
        print("\n🔄 TRANSFORM EXISTING CONTENT")
        print("="*40)
        
        # Get content
        content = self.get_content_input()
        if not content:
            print("❌ No content provided")
            return
        
        # Get transformation parameters
        target_format = self.select_format()
        target_style = self.select_style()
        target_complexity = self.select_complexity()
        
        # Transform
        self.transform_content(content, target_format, target_style, target_complexity)
    
    def handle_generate_from_title(self):
        """Handle content generation from title"""
        print("\n🎯 GENERATE CONTENT FROM TITLE")
        print("="*40)
        
        # Get title
        title = self.get_title_input()
        if not title:
            print("❌ No title provided")
            return
        
        # Generate content
        content = self.generate_content_from_title(title)
        
        print(f"\n📝 GENERATED CONTENT:")
        print("-"*40)
        print(content)
        print("-"*40)
        
        # Ask if user wants to transform it
        choice = input("\nWould you like to transform this content? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            # Get transformation parameters
            target_format = self.select_format()
            target_style = self.select_style()
            target_complexity = self.select_complexity()
            
            # Transform
            self.transform_content(content, target_format, target_style, target_complexity)
    
    def handle_convert_between_styles(self):
        """Handle conversion between styles"""
        print("\n🔄 CONVERT BETWEEN STYLES")
        print("="*40)
        
        # Get content
        content = self.get_content_input()
        if not content:
            print("❌ No content provided")
            return
        
        # Get current style (optional)
        print("\n📝 CURRENT STYLE (optional - press Enter to skip):")
        print("-"*40)
        for key, style_name in self.style_names.items():
            print(f"{list(self.styles.keys())[list(self.styles.values()).index(key)]}. {style_name}")
        
        current_choice = input("\nEnter current style choice (1-8) or press Enter to skip: ").strip()
        current_style = None
        if current_choice in self.styles:
            current_style = self.styles[current_choice]
            print(f"✅ Current style: {self.style_names[current_style]}")
        
        # Get target parameters
        target_format = self.select_format()
        target_style = self.select_style()
        target_complexity = self.select_complexity()
        
        # Transform
        self.transform_content(content, target_format, target_style, target_complexity)
    
    def run(self):
        """Run the interactive CLI"""
        print("🚀 Welcome to the Content Transformation System!")
        
        # Check environment
        if not os.getenv("ULTRASAFE_API_KEY"):
            print("❌ ULTRASAFE_API_KEY environment variable not set")
            print("Please set your API key before running the system")
            return
        
        # Initialize system
        if not self.initialize_system():
            return
        
        # Main loop
        while True:
            self.display_menu()
            choice = self.get_user_choice("Enter your choice (1-4): ", ['1', '2', '3', '4'])
            
            if choice == '1':
                self.handle_transform_existing_content()
            elif choice == '2':
                self.handle_generate_from_title()
            elif choice == '3':
                self.handle_convert_between_styles()
            elif choice == '4':
                print("👋 Thank you for using the Content Transformation System!")
                break
            
            # Ask if user wants to continue
            if choice in ['1', '2', '3']:
                continue_choice = input("\nWould you like to perform another transformation? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Thank you for using the Content Transformation System!")
                    break

def main():
    """Main function"""
    cli = InteractiveCLI()
    cli.run()

if __name__ == "__main__":
    main() 