"""
Test Script for Content Transformation System
Demonstrates the multi-agent system capabilities
"""

import os
import sys
from pathlib import Path

# Add the task_b directory to the path
sys.path.append(str(Path(__file__).parent))

from content_transformation_system import ContentTransformationSystem

def test_basic_transformation():
    """Test basic content transformation"""
    print("Testing Basic Content Transformation")
    print("=" * 60)
    
    # Initialize the system
    system = ContentTransformationSystem()
    
    # Sample content to transform
    sample_content = """
    Building an Emergency Fund: A Financial Safety Net Planning Guide
    
    An emergency fund is a dedicated reserve of money set aside to cover unexpected financial emergencies or expenses, such as job loss, medical emergencies, major car repairs, or urgent home maintenance. It acts as a financial safety net, enabling individuals and households to manage unforeseen situations without resorting to high-interest debt or compromising long-term financial goals.
    
    Financial experts typically recommend saving between three to six months' worth of essential living expenses. The U.S. Federal Reserve's latest Report on the Economic Well-Being of U.S. Households (2023) notes that about 28% of adults would struggle to cover an unexpected $400 expense without borrowing or selling something.
    
    The concept of an emergency fund is a fundamental aspect of personal financial planning and risk management. It provides liquidity and peace of mind by buffering against the financial impact of unpredictable events.
    """
    
    # Test transformation: Blog Post → Twitter Thread, Casual → Gen Z, Expert → Newbie
    print("Transforming: Blog Post → Twitter Thread")
    print("   Style: Casual Conversational → Gen Z")
    print("   Complexity: Expert → Newbie")
    print()
    
    result = system.transform_content(
        content=sample_content,
        target_format="twitter_thread",
        target_style="gen_z",
        target_complexity="newbie"
    )
    
    # Display results
    if result['success']:
        print("Transformation Successful!")
        print(f"Quality Score: {result['quality_metrics']['overall_quality_score']:.2f}/1.0")
        print(f"Iterations: {result['iterations']}")
        print(f"RAG Used: {result['rag_context_used']}")
        print()
        print("Transformed Content:")
        print("-" * 50)
        print(result['transformed_content'])
        print("-" * 50)
        
        # Show quality breakdown
        print("\nQuality Metrics Breakdown:")
        metrics = result['quality_metrics']
        print(f"   Factual Accuracy: {metrics['factual_accuracy_score']:.2f}")
        print(f"   Style Adherence: {metrics['style_adherence_score']:.2f}")
        print(f"   Format Compliance: {metrics['format_compliance_score']:.2f}")
        print(f"   Complexity Match: {metrics['complexity_match_score']:.2f}")
        print(f"   Readability: {metrics['readability_score']:.2f}")
        print(f"   Engagement: {metrics['engagement_score']:.2f}")
        
        if metrics['issues_found']:
            print(f"\nIssues Found: {len(metrics['issues_found'])}")
            for issue in metrics['issues_found'][:3]:  # Show first 3 issues
                print(f"   - {issue}")
        
        if metrics['suggestions']:
            print(f"\nSuggestions: {len(metrics['suggestions'])}")
            for suggestion in metrics['suggestions'][:3]:  # Show first 3 suggestions
                print(f"   - {suggestion}")
    else:
        print(f"Transformation Failed: {result['error']}")

def test_multiple_transformations():
    """Test multiple transformation scenarios"""
    print("\nTesting Multiple Transformation Scenarios")
    print("=" * 60)
    
    # Initialize the system
    system = ContentTransformationSystem()
    
    # Sample content
    sample_content = """
    Machine Learning for Beginners: Understanding the Basics
    
    Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed. It involves algorithms that can identify patterns in data and use those patterns to make predictions or decisions.
    
    There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled training data to learn the relationship between inputs and outputs. Unsupervised learning finds hidden patterns in unlabeled data. Reinforcement learning learns through trial and error with rewards and penalties.
    
    Common applications include recommendation systems, image recognition, natural language processing, and predictive analytics. The field continues to evolve rapidly with new algorithms and applications emerging regularly.
    """
    
    # Test scenarios
    scenarios = [
        {
            "name": "Blog → LinkedIn (Formal Professional, Expert)",
            "target_format": "linkedin_post",
            "target_style": "formal_professional",
            "target_complexity": "expert"
        },
        {
            "name": "Blog → Email Newsletter (Enthusiastic, Knows a Little)",
            "target_format": "email_newsletter",
            "target_style": "enthusiastic_and_motivational",
            "target_complexity": "knows_a_little"
        },
        {
            "name": "Blog → Podcast Script (Yoda Style, Newbie)",
            "target_format": "podcast_script",
            "target_style": "yoda_star_wars",
            "target_complexity": "newbie"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 40)
        
        result = system.transform_content(
            content=sample_content,
            target_format=scenario['target_format'],
            target_style=scenario['target_style'],
            target_complexity=scenario['target_complexity']
        )
        
        if result['success']:
            print(f"Success! Quality: {result['quality_metrics']['overall_quality_score']:.2f}")
            print(f"Preview: {result['transformed_content'][:100]}...")
        else:
            print(f"Failed: {result['error']}")

def test_user_feedback():
    """Test system with user feedback for iteration"""
    print("\nTesting User Feedback Integration")
    print("=" * 60)
    
    # Initialize the system
    system = ContentTransformationSystem()
    
    # Sample content
    sample_content = """
    Sustainable Living: Reducing Your Environmental Impact
    
    Sustainable living involves making conscious choices to reduce your environmental footprint. This includes reducing energy consumption, minimizing waste, choosing eco-friendly products, and supporting sustainable practices.
    
    Key areas to focus on include energy efficiency in your home, reducing single-use plastics, choosing local and seasonal food, using public transportation or carpooling, and supporting businesses with sustainable practices.
    
    Small changes can add up to significant impact when adopted by many people. Start with one area and gradually expand your sustainable practices.
    """
    
    # Initial transformation
    print("Initial Transformation: Blog → Twitter Thread (Millennial, Expert)")
    result = system.transform_content(
        content=sample_content,
        target_format="twitter_thread",
        target_style="millennial",
        target_complexity="expert"
    )
    
    if result['success']:
        print(f"Initial Quality: {result['quality_metrics']['overall_quality_score']:.2f}")
        print("Initial Result Preview:")
        print(result['transformed_content'][:200] + "...")
        
        # Simulate user feedback
        user_feedback = {
            'issues': ['Too formal for millennial style', 'Needs more emojis and casual language'],
            'suggestions': ['Make it more conversational', 'Add relevant hashtags'],
            'target_improvements': ['Improve style adherence', 'Increase engagement']
        }
        
        print(f"\nApplying User Feedback...")
        
        # Transform with feedback
        result_with_feedback = system.transform_content(
            content=sample_content,
            target_format="twitter_thread",
            target_style="millennial",
            target_complexity="expert",
            user_feedback=user_feedback
        )
        
        if result_with_feedback['success']:
            print(f"Feedback Applied! Quality: {result_with_feedback['quality_metrics']['overall_quality_score']:.2f}")
            print("Improved Result Preview:")
            print(result_with_feedback['transformed_content'][:200] + "...")
            
            # Compare quality scores
            improvement = result_with_feedback['quality_metrics']['overall_quality_score'] - result['quality_metrics']['overall_quality_score']
            print(f"\nQuality Improvement: {improvement:+.2f}")
        else:
            print(f"Feedback application failed: {result_with_feedback['error']}")
    else:
        print(f"Initial transformation failed: {result['error']}")

def main():
    """Run all tests"""
    print("🚀 Content Transformation System - Test Suite")
    print("=" * 80)
    
    try:
        # Test 1: Basic transformation
        test_basic_transformation()
        
        # Test 2: Multiple scenarios
        test_multiple_transformations()
        
        # Test 3: User feedback
        test_user_feedback()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 