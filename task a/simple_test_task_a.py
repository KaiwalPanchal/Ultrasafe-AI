# -*- coding: utf-8 -*-
"""
Simple Test Script for Task A FastAPI NLP Application
====================================================

This script tests the core functionality of your Task A application:
- All NLP endpoints
- Batch processing
- Caching
- Performance monitoring

Usage:
    python simple_test_task_a.py

Make sure your Task A server is running:
    uvicorn task\ a.Task_A:app --reload
"""

import requests
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("ULTRASAFE_API_KEY")

def test_endpoint(endpoint, data, expected_keys=None):
    """Test a single endpoint"""
    print(f"Testing {endpoint}...")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"  Success. Processed {result.get('total_processed', 'N/A')} texts.")
        
        if expected_keys:
            for key in expected_keys:
                if key not in result:
                    print(f"  Warning: Missing expected key: {key}")
        
        return result
    except Exception as e:
        print(f"  Failed: {str(e)}")
        return None

def test_get_endpoint(endpoint, expected_keys=None):
    """Test a GET endpoint"""
    print(f"Testing GET {endpoint}...")
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print(f"  Success.")
        
        if expected_keys:
            for key in expected_keys:
                if key not in result:
                    print(f"  Warning: Missing expected key: {key}")
        
        return result
    except Exception as e:
        print(f"  Failed: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("Task A Simple Test Suite")
    print("=" * 40)
    
    # Check if server is running
    print("Checking server health...")
    try:
        health = test_get_endpoint("/health", ["status", "llm_model"])
        if not health:
            print("Server is not responding. Make sure it's running with:")
            print("   uvicorn task a.Task_A:app --reload")
            return False
        print(f"Server is healthy. Using model: {health.get('llm_model', 'unknown')}")
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("Testing NLP Endpoints")
    print("=" * 40)
    
    # Test data
    test_texts = [
        "Artificial intelligence is transforming technology.",
        "The stock market reached new highs today.",
        "I love this amazing product!",
        "This is terrible and disappointing.",
        "Apple CEO Tim Cook announced new products in San Francisco."
    ]
    
    # Test classification
    classification_result = test_endpoint("/classify", {
        "texts": test_texts
    }, ["results", "total_processed"])
    
    # Test sentiment analysis
    sentiment_result = test_endpoint("/sentiment", {
        "texts": test_texts
    }, ["results", "total_processed"])
    
    # Test entity extraction
    ner_result = test_endpoint("/extract", {
        "texts": test_texts
    }, ["results", "total_processed"])
    
    # Test summarization
    long_text = """
    Artificial intelligence has become one of the most transformative technologies of our time. 
    From machine learning algorithms that power recommendation systems to natural language 
    processing that enables chatbots and virtual assistants, AI is reshaping how we interact 
    with technology. Companies across industries are investing heavily in AI research and 
    development, recognizing its potential to drive innovation and competitive advantage.
    """
    
    summary_result = test_endpoint("/summarize", {
        "texts": [long_text]
    }, ["results", "total_processed"])
    
    print("\n" + "=" * 40)
    print("Testing Batch Processing")
    print("=" * 40)
    
    # Test single text
    single_result = test_endpoint("/classify", {
        "texts": "Single text test"
    }, ["results", "total_processed"])
    
    # Test large batch
    large_batch = [f"Batch text {i}" for i in range(10)]
    large_batch_result = test_endpoint("/classify", {
        "texts": large_batch
    }, ["results", "total_processed"])
    
    print("\n" + "=" * 40)
    print("Testing Caching System")
    print("=" * 40)
    
    # Test cache stats
    cache_stats = test_get_endpoint("/cache/stats", ["cache_size", "max_size", "ttl_seconds"])
    
    # Test cache hit/miss
    print("Testing cache performance...")
    test_text = "Cache performance test text"
    
    # First request (should miss cache)
    start_time = time.time()
    first_response = requests.post(f"{BASE_URL}/classify", json={"texts": [test_text]})
    first_duration = time.time() - start_time
    
    # Second request (should hit cache)
    start_time = time.time()
    second_response = requests.post(f"{BASE_URL}/classify", json={"texts": [test_text]})
    second_duration = time.time() - start_time
    
    print(f"  First request: {first_duration:.3f}s")
    print(f"  Second request: {second_duration:.3f}s")
    print(f"  Speedup: {first_duration/second_duration:.1f}x" if second_duration > 0 else "  Speedup: Instant cache hit")
    
    # Test cache clear
    print("Testing cache clear...")
    clear_result = requests.post(f"{BASE_URL}/cache/clear")
    if clear_result.status_code == 200:
        print("  Cache cleared successfully.")
    else:
        print("  Failed to clear cache.")
    
    print("\n" + "=" * 40)
    print("Testing Performance Monitoring")
    print("=" * 40)
    
    # Test performance metrics
    performance = test_get_endpoint("/performance", ["cache", "task_queue", "system"])
    
    # Test updated cache stats
    updated_cache_stats = test_get_endpoint("/cache/stats", ["cache_size", "max_size"])
    
    print("\n" + "=" * 40)
    print("Testing API Documentation")
    print("=" * 40)
    
    # Test API docs
    try:
        docs_response = requests.get(f"{BASE_URL}/docs")
        if docs_response.status_code == 200:
            print("Swagger UI available at /docs.")
        else:
            print("Swagger UI not available.")
    except Exception as e:
        print(f"Cannot access Swagger UI: {e}")
    
    try:
        redoc_response = requests.get(f"{BASE_URL}/redoc")
        if redoc_response.status_code == 200:
            print("ReDoc available at /redoc.")
        else:
            print("ReDoc not available.")
    except Exception as e:
        print(f"Cannot access ReDoc: {e}")
    
    print("\n" + "=" * 40)
    print("Test Summary")
    print("=" * 40)
    
    # Count successful tests
    successful_tests = sum([
        classification_result is not None,
        sentiment_result is not None,
        ner_result is not None,
        summary_result is not None,
        single_result is not None,
        large_batch_result is not None,
        cache_stats is not None,
        performance is not None,
        updated_cache_stats is not None
    ])
    
    total_tests = 9
    
    print(f"Successful tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\nAll tests passed. Your Task A application is working correctly.")
        print("\nYou can now:")
        print("  - Access the API at http://localhost:8000")
        print("  - View documentation at http://localhost:8000/docs")
        print("  - Monitor performance at http://localhost:8000/performance")
        return True
    else:
        print(f"\n{total_tests - successful_tests} tests failed.")
        print("Check the error messages above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 