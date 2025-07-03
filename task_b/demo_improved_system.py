"""
Demo of Improved Content Transformation System
Shows the Master Content → Human Verification → Style Transformation pattern
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the task_b directory to the path
sys.path.append(str(Path(__file__).parent))

load_dotenv()

def demo_master_content_generation():
    """Demo the master content generation step"""
    print("DEMO: Master Content Generation")
    print("="*50)
    
    try:
        from improved_content_system import ImprovedContentSystem
        
        system = ImprovedContentSystem()
        
        # Demo title
        title = "The Benefits of Meditation"
        
        print(f"Title: {title}")
        print("Generating master content...")
        
        # Generate master content
        master_content = system.generate_master_content(title)
        
        print(f"Master content generated!")
        print(f"Content length: {len(master_content.content)} characters")
        print(f"Facts extracted: {len(master_content.facts)}")
        print(f"Sources: {len(master_content.sources)}")
        
        # Show sample content
        print(f"\nSAMPLE MASTER CONTENT:")
        print("-"*40)
        print(master_content.content[:300] + "...")
        print("-"*40)
        
        if master_content.facts:
            print(f"\nEXTRACTED FACTS:")
            for i, fact in enumerate(master_content.facts[:3], 1):
                print(f"{i}. {fact}")
        
        return master_content
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def demo_human_verification():
    """Demo the human verification step"""
    print("\nDEMO: Human Verification Process")
    print("="*50)
    
    print("""
In the real system, this step would:

1. Show all extracted facts to the human
2. Display all sources used
3. Show the full generated content
4. Ask human to verify accuracy (y/n/edit)
5. Mark content as verified or needs revision

Example interaction:
Is this content factually accurate? (y/n/edit): y
Content verified as factually accurate!

This ensures factual accuracy before style transformation.
""")

def demo_style_transformation():
    """Demo the style transformation step"""
    print("\nDEMO: Style Transformation")
    print("="*50)
    
    print("""
After human verification, the system:

1. Takes the verified master content
2. Applies the selected style guide
3. Transforms format, tone, and complexity
4. Preserves all verified facts
5. Provides quality metrics

Example transformation:
Master Content (Factual) → Twitter Thread (Gen Z Style)
- Preserves: "Meditation reduces stress by 40%"
- Changes: Tone from formal to casual
- Adapts: Format from article to thread
- Maintains: All verified facts and statistics
""")

def demo_complete_workflow():
    """Demo the complete workflow"""
    print("\nDEMO: Complete Workflow")
    print("="*50)
    
    print("""
COMPLETE WORKFLOW:

Step 1: Master Content Generation
├── Input: "The Benefits of Meditation"
├── Output: Factual, comprehensive content
└── Includes: Facts, sources, structured information

Step 2: Human Verification
├── Display: All facts and sources
├── Human: Reviews and verifies accuracy
└── Result: Verified master content

Step 3: Style Transformation
├── Input: Verified master content
├── Style: Gen Z Twitter Thread
├── Output: Stylized content
└── Quality: Metrics and verification

BENEFITS:
- Factual accuracy guaranteed by human verification
- Style transformation preserves verified facts
- Quality metrics ensure proper transformation
- Follows your established pattern
""")

def demo_factual_preservation():
    """Demo how facts are preserved across transformations"""
    print("\nDEMO: Factual Preservation Across Styles")
    print("="*50)
    
    print("""
FACTUAL PRESERVATION MECHANISM:

Original Fact: "Meditation reduces stress by 40% according to 2023 study"

Style Transformations:
├── Formal Professional: "Research indicates a 40% stress reduction through meditation"
├── Gen Z: "The tea: meditation can reduce stress by 40%"
├── Yoda Style: "Reduce stress by 40%, meditation does, studies show"
└── Sherlock Holmes: "The evidence is clear: meditation produces a 40% reduction in stress levels"

ALL PRESERVE:
- The core fact (40% reduction)
- The source (study/research)
- The accuracy of the claim

NONE ADD:
- New unverified facts
- Changed statistics
- Unsupported claims
""")

def main():
    """Run the demo"""
    print("IMPROVED CONTENT TRANSFORMATION SYSTEM - DEMO")
    print("="*80)
    print("This demo shows how the system follows your pattern:")
    print("Master Content → Human Verification → Style Transformation")
    print("="*80)
    
    # Check environment
    if not os.getenv("ULTRASAFE_API_KEY"):
        print("ULTRASAFE_API_KEY not set - some demos may not work")
    
    try:
        # Demo each step
        demo_master_content_generation()
        demo_human_verification()
        demo_style_transformation()
        demo_complete_workflow()
        demo_factual_preservation()
        
        print("\nDEMO COMPLETE!")
        print("\nTo use the improved system:")
        print("   python improved_content_system.py")
        print("\nKey improvements:")
        print("   - Human-in-the-loop factual verification")
        print("   - Master content generation pattern")
        print("   - Factual preservation across styles")
        print("   - Quality metrics and validation")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 