# -*- coding: utf-8 -*-
"""
Task A Runner Script
===================

This script helps you run and test your Task A FastAPI application.

Usage:
    python run_task_a.py

This will:
1. Check if required dependencies are installed
2. Verify environment variables
3. Start the FastAPI server
4. Provide testing instructions
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'langchain-openai',
        'httpx',
        'langchain-core',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment():
    """Check if environment variables are set"""
    load_dotenv()
    
    api_key = os.getenv("ULTRASAFE_API_KEY")
    if not api_key:
        print("❌ ULTRASAFE_API_KEY environment variable is not set")
        print("\nPlease set it in your .env file or environment:")
        print("ULTRASAFE_API_KEY=your-api-key-here")
        return False
    
    print("✅ ULTRASAFE_API_KEY is set")
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Task A FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "Task_A:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")

def show_testing_instructions():
    """Show instructions for testing"""
    print("\n" + "=" * 60)
    print("🧪 TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Start the server (if not already running):")
    print("   python run_task_a.py")
    
    print("\n2. Run the automated tests:")
    print("   python simple_test_task_a.py")
    
    print("\n3. Manual testing:")
    print("   - Open http://localhost:8000 in your browser")
    print("   - View API docs at http://localhost:8000/docs")
    print("   - Test endpoints using the interactive docs")
    
    print("\n4. Example API calls:")
    print("   curl -X POST http://localhost:8000/classify \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"texts\": [\"AI is amazing!\"]}'")
    
    print("\n5. Performance monitoring:")
    print("   - http://localhost:8000/performance")
    print("   - http://localhost:8000/cache/stats")
    
    print("\n" + "=" * 60)

def main():
    """Main function"""
    print("🎯 Task A FastAPI Application Runner")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check environment
    if not check_environment():
        return False
    
    # Show testing instructions
    show_testing_instructions()
    
    # Ask user what they want to do
    print("\nWhat would you like to do?")
    print("1. Start the server")
    print("2. Run tests only")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        start_server()
    elif choice == "2":
        print("\nRunning tests...")
        subprocess.run([sys.executable, "simple_test_task_a.py"])
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")
    
    return True

if __name__ == "__main__":
    main() 