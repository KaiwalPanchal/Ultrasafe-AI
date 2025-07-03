# -*- coding: utf-8 -*-
"""
Quick Test for Task A Fixes
===========================

This script quickly tests the specific issues that were failing:
1. Entity extraction
2. Cache hit/miss division by zero

Run this to verify the fixes work before running the full test suite.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_entity_extraction():
    """Test entity extraction specifically"""
    print("Testing Entity Extraction...")
    
    test_texts = [
        "Apple CEO Tim Cook announced new products in San Francisco.",
        "The United Nations meeting in New York discussed climate change."
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/extract", json={"texts": test_texts}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"  ✅ Response received: {len(data.get('results', []))} results")
        
        for i, result in enumerate(data.get('results', [])):
            print(f"  Result {i}: {type(result)} - {result}")
            
            # Test the new flexible validation
            assert isinstance(result, (list, str)), f"Result {i} is {type(result)}, expected list or str"
            
            if isinstance(result, str):
                assert len(result.strip()) > 0, f"Result {i} is empty string"
                print(f"    ✅ String result: '{result}'")
            elif isinstance(result, list):
                print(f"    ✅ List result with {len(result)} entities")
                if len(result) > 0:
                    for entity in result:
                        assert isinstance(entity, dict), f"Entity is {type(entity)}, expected dict"
        
        print("  ✅ Entity extraction test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Entity extraction test failed: {e}")
        return False

def test_cache_hit_miss():
    """Test cache hit/miss with division by zero fix"""
    print("Testing Cache Hit/Miss...")
    
    test_text = "Cache test text for hit/miss testing"
    
    try:
        # First request (should miss cache)
        start_time = time.time()
        response1 = requests.post(f"{BASE_URL}/classify", json={"texts": [test_text]}, timeout=30)
        first_duration = time.time() - start_time
        
        # Second request (should hit cache)
        start_time = time.time()
        response2 = requests.post(f"{BASE_URL}/classify", json={"texts": [test_text]}, timeout=30)
        second_duration = time.time() - start_time
        
        print(f"  First request: {first_duration:.3f}s")
        print(f"  Second request: {second_duration:.3f}s")
        
        # Test the new safe division
        assert second_duration < first_duration, "Second request should be faster"
        
        if second_duration > 0:
            speedup = first_duration / second_duration
            print(f"  Speedup: {speedup:.1f}x")
        else:
            speedup = float('inf')
            print(f"  Speedup: Infinite (instant cache hit)")
        
        print("  ✅ Cache hit/miss test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Cache hit/miss test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🧪 Quick Test for Task A Fixes")
    print("=" * 40)
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Server is not responding correctly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running with: python -m uvicorn Task_A:app --reload")
        return False
    
    print()
    
    # Run specific tests
    tests = [
        ("Entity Extraction", test_entity_extraction),
        ("Cache Hit/Miss", test_cache_hit_miss),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}")
        print("-" * 20)
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes working! You can now run the full test suite.")
        return True
    else:
        print("⚠️  Some tests still failing. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 