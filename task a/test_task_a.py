# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Task A FastAPI NLP Application
==========================================================

This script tests all functionality including:
- All NLP endpoints (classification, sentiment, NER, summarization)
- Batch processing capabilities
- Caching functionality
- Task queuing system
- Performance monitoring
- Webhook notifications (simulated)

Usage:
    python test_task_a.py

Requirements:
    - Task A server running on http://localhost:8000
    - ULTRASAFE_API_KEY environment variable set
"""

import asyncio
import json
import time
import requests
import threading
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("ULTRASAFE_API_KEY")

if not API_KEY:
    print("❌ ULTRASAFE_API_KEY environment variable not set!")
    print("Please set it before running tests.")
    exit(1)

@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    success: bool
    duration: float
    error: str = None
    data: Any = None

class TaskATestSuite:
    """Comprehensive test suite for Task A FastAPI application"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.webhook_received = False
        self.webhook_data = None
        
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        print("🚀 Starting Task A Test Suite")
        print("=" * 50)
        
        # Test categories
        test_categories = [
            ("Health & Setup", self.test_health_and_setup),
            ("NLP Endpoints", self.test_nlp_endpoints),
            ("Batch Processing", self.test_batch_processing),
            ("Caching System", self.test_caching_system),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("Webhook System", self.test_webhook_system),
            ("Concurrent Load", self.test_concurrent_load),
        ]
        
        all_passed = True
        
        for category_name, test_func in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 30)
            category_passed = test_func()
            if not category_passed:
                all_passed = False
                print(f"❌ {category_name} tests failed!")
            else:
                print(f"✅ {category_name} tests passed!")
        
        self.print_summary()
        return all_passed
    
    def test_health_and_setup(self) -> bool:
        """Test basic health and setup"""
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Check", self.test_health_check),
            ("API Documentation", self.test_api_docs),
        ]
        return self._run_test_group(tests)
    
    def test_nlp_endpoints(self) -> bool:
        """Test all NLP endpoints"""
        tests = [
            ("Text Classification", self.test_classification),
            ("Sentiment Analysis", self.test_sentiment_analysis),
            ("Entity Extraction", self.test_entity_extraction),
            ("Text Summarization", self.test_summarization),
        ]
        return self._run_test_group(tests)
    
    def test_batch_processing(self) -> bool:
        """Test batch processing capabilities"""
        tests = [
            ("Single Text Processing", self.test_single_text),
            ("Multiple Text Processing", self.test_multiple_texts),
            ("Large Batch Processing", self.test_large_batch),
        ]
        return self._run_test_group(tests)
    
    def test_caching_system(self) -> bool:
        """Test caching functionality"""
        tests = [
            ("Cache Stats", self.test_cache_stats),
            ("Cache Hit/Miss", self.test_cache_hit_miss),
            ("Cache Clear", self.test_cache_clear),
        ]
        return self._run_test_group(tests)
    
    def test_performance_monitoring(self) -> bool:
        """Test performance monitoring endpoints"""
        tests = [
            ("Performance Metrics", self.test_performance_metrics),
            ("Cache Statistics", self.test_cache_statistics),
        ]
        return self._run_test_group(tests)
    
    def test_webhook_system(self) -> bool:
        """Test webhook functionality"""
        tests = [
            ("Webhook Processing", self.test_webhook_processing),
        ]
        return self._run_test_group(tests)
    
    def test_concurrent_load(self) -> bool:
        """Test concurrent load handling"""
        tests = [
            ("Concurrent Requests", self.test_concurrent_requests),
        ]
        return self._run_test_group(tests)
    
    def _run_test_group(self, tests: List[tuple]) -> bool:
        """Run a group of tests"""
        group_passed = True
        for test_name, test_func in tests:
            result = self._run_single_test(test_name, test_func)
            self.test_results.append(result)
            if not result.success:
                group_passed = False
        return group_passed
    
    def _run_single_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test and return result"""
        start_time = time.time()
        try:
            data = test_func()
            duration = time.time() - start_time
            print(f"  ✅ {test_name} ({duration:.2f}s)")
            return TestResult(test_name, True, duration, data=data)
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            # Add more context for common errors
            if "float division by zero" in error_msg:
                error_msg = "Cache timing issue - second request was too fast"
            elif "JSONDecodeError" in error_msg:
                error_msg = "Invalid JSON response from LLM"
            elif "Connection" in error_msg:
                error_msg = "Server connection failed - make sure server is running"
            print(f"  ❌ {test_name} ({duration:.2f}s) - {error_msg}")
            return TestResult(test_name, False, duration, error=error_msg)
    
    # Individual test methods
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        data = response.json()
        assert "service" in data
        assert "endpoints" in data
        assert "features" in data
        return data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        data = response.json()
        assert data["status"] == "healthy"
        return data
    
    def test_api_docs(self):
        """Test API documentation endpoints"""
        # Test Swagger UI
        response = self.session.get(f"{self.base_url}/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = self.session.get(f"{self.base_url}/redoc")
        assert response.status_code == 200
        return {"docs": "available"}
    
    def test_classification(self):
        """Test text classification endpoint"""
        test_texts = [
            "Artificial intelligence is transforming the technology industry.",
            "The stock market reached new highs today.",
            "The football team won the championship game."
        ]
        
        response = self.session.post(f"{self.base_url}/classify", json={
            "texts": test_texts
        })
        response.raise_for_status()
        data = response.json()
        
        assert "results" in data
        assert "total_processed" in data
        assert data["total_processed"] == 3
        assert len(data["results"]) == 3
        
        # Verify classifications are valid
        valid_categories = ["technology", "finance", "sports", "politics", "entertainment", 
                          "health", "education", "travel", "food", "other"]
        for result in data["results"]:
            assert result.lower() in valid_categories
        
        return data
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis endpoint"""
        test_texts = [
            "I love this product! It's amazing!",
            "This is terrible. I hate it.",
            "The weather is sunny today."
        ]
        
        response = self.session.post(f"{self.base_url}/sentiment", json={
            "texts": test_texts
        })
        response.raise_for_status()
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) == 3
        
        # Verify sentiment scores are numbers between -100 and 100
        for result in data["results"]:
            score = int(result)
            assert -100 <= score <= 100
        
        return data
    
    def test_entity_extraction(self):
        """Test entity extraction endpoint"""
        test_texts = [
            "Apple CEO Tim Cook announced new products in San Francisco.",
            "The United Nations meeting in New York discussed climate change."
        ]
        
        response = self.session.post(f"{self.base_url}/extract", json={
            "texts": test_texts
        })
        response.raise_for_status()
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) == 2
        
        # Verify entities are extracted (can be JSON arrays or strings)
        for i, result in enumerate(data["results"]):
            # Accept both list (JSON array) and string formats
            assert isinstance(result, (list, str)), f"Result {i} is {type(result)}, expected list or str"
            # If it's a string, it should not be empty
            if isinstance(result, str):
                assert len(result.strip()) > 0, f"Result {i} is empty string"
            # If it's a list, it should contain entity objects
            elif isinstance(result, list):
                # Allow empty lists (no entities found)
                if len(result) > 0:
                    # If not empty, should contain dictionaries with entity info
                    for entity in result:
                        assert isinstance(entity, dict), f"Entity in result {i} is {type(entity)}, expected dict"
        
        return data
    
    def test_summarization(self):
        """Test text summarization endpoint"""
        test_text = """
        Artificial intelligence has become one of the most transformative technologies of our time. 
        From machine learning algorithms that power recommendation systems to natural language 
        processing that enables chatbots and virtual assistants, AI is reshaping how we interact 
        with technology. Companies across industries are investing heavily in AI research and 
        development, recognizing its potential to drive innovation and competitive advantage. 
        However, the rapid advancement of AI also raises important questions about ethics, 
        privacy, and the future of work.
        """
        
        response = self.session.post(f"{self.base_url}/summarize", json={
            "texts": [test_text]
        })
        response.raise_for_status()
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) == 1
        assert isinstance(data["results"][0], str)
        assert len(data["results"][0]) > 0
        
        return data
    
    def test_single_text(self):
        """Test single text processing"""
        response = self.session.post(f"{self.base_url}/classify", json={
            "texts": "This is a single text for testing."
        })
        response.raise_for_status()
        data = response.json()
        assert data["total_processed"] == 1
        return data
    
    def test_multiple_texts(self):
        """Test multiple text processing"""
        texts = [f"Test text number {i}" for i in range(5)]
        response = self.session.post(f"{self.base_url}/classify", json={
            "texts": texts
        })
        response.raise_for_status()
        data = response.json()
        assert data["total_processed"] == 5
        return data
    
    def test_large_batch(self):
        """Test large batch processing"""
        texts = [f"Large batch test text {i}" for i in range(20)]
        response = self.session.post(f"{self.base_url}/classify", json={
            "texts": texts
        })
        response.raise_for_status()
        data = response.json()
        assert data["total_processed"] == 20
        return data
    
    def test_cache_stats(self):
        """Test cache statistics endpoint"""
        response = self.session.get(f"{self.base_url}/cache/stats")
        response.raise_for_status()
        data = response.json()
        assert "cache_size" in data
        assert "max_size" in data
        assert "ttl_seconds" in data
        return data
    
    def test_cache_hit_miss(self):
        """Test cache hit/miss functionality"""
        test_text = "Cache test text for hit/miss testing"
        
        # First request (should miss cache)
        start_time = time.time()
        response1 = self.session.post(f"{self.base_url}/classify", json={
            "texts": [test_text]
        })
        first_duration = time.time() - start_time
        
        # Second request (should hit cache)
        start_time = time.time()
        response2 = self.session.post(f"{self.base_url}/classify", json={
            "texts": [test_text]
        })
        second_duration = time.time() - start_time
        
        # Second request should be faster (cache hit)
        assert second_duration < first_duration
        
        # Calculate speedup safely (avoid division by zero)
        if second_duration > 0:
            speedup = first_duration / second_duration
        else:
            speedup = float('inf')  # Infinite speedup if second request was instant
        
        return {
            "first_duration": first_duration,
            "second_duration": second_duration,
            "speedup": speedup
        }
    
    def test_cache_clear(self):
        """Test cache clear functionality"""
        # Get initial cache size
        response = self.session.get(f"{self.base_url}/cache/stats")
        initial_size = response.json()["cache_size"]
        
        # Clear cache
        response = self.session.post(f"{self.base_url}/cache/clear")
        response.raise_for_status()
        
        # Verify cache is cleared
        response = self.session.get(f"{self.base_url}/cache/stats")
        final_size = response.json()["cache_size"]
        assert final_size == 0
        
        return {"initial_size": initial_size, "final_size": final_size}
    
    def test_performance_metrics(self):
        """Test performance metrics endpoint"""
        response = self.session.get(f"{self.base_url}/performance")
        response.raise_for_status()
        data = response.json()
        assert "cache" in data
        assert "task_queue" in data
        assert "system" in data
        return data
    
    def test_cache_statistics(self):
        """Test cache statistics"""
        response = self.session.get(f"{self.base_url}/cache/stats")
        response.raise_for_status()
        data = response.json()
        assert "cache_size" in data
        assert "max_size" in data
        assert "ttl_seconds" in data
        return data
    
    def test_webhook_processing(self):
        """Test webhook processing (simulated)"""
        # Start a simple webhook server in a separate thread
        self.webhook_received = False
        self.webhook_data = None
        
        def webhook_server():
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json
            
            class WebhookHandler(BaseHTTPRequestHandler):
                def do_POST(self):
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    self.webhook_data = json.loads(post_data.decode('utf-8'))
                    self.webhook_received = True
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "received"}).encode())
                
                def log_message(self, format, *args):
                    pass  # Suppress logging
            
            server = HTTPServer(('localhost', 8080), WebhookHandler)
            server.handle_request()
        
        # Start webhook server
        webhook_thread = threading.Thread(target=webhook_server)
        webhook_thread.start()
        time.sleep(1)  # Give server time to start
        
        try:
            # Send request with webhook
            response = self.session.post(f"{self.base_url}/classify", json={
                "texts": ["Webhook test text"],
                "webhook_url": "http://localhost:8080/webhook"
            })
            response.raise_for_status()
            data = response.json()
            
            # Verify webhook response
            assert data["status"] == "accepted"
            assert "webhook" in data
            
            # Wait for webhook to be received
            time.sleep(3)
            
            return {"webhook_status": "sent", "response": data}
            
        finally:
            webhook_thread.join(timeout=5)
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        def make_request():
            response = self.session.post(f"{self.base_url}/classify", json={
                "texts": [f"Concurrent test text {threading.current_thread().ident}"]
            })
            return response.json()
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # Verify all requests succeeded
        for result in results:
            assert "results" in result
            assert "total_processed" in result
        
        return {"concurrent_requests": len(results)}
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.error}")
        
        # Performance summary
        avg_duration = sum(result.duration for result in self.test_results) / total_tests
        print(f"\n⏱️  Average Test Duration: {avg_duration:.2f}s")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Task A is working correctly.")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please check the implementation.")

def main():
    """Main test runner"""
    print("🧪 Task A FastAPI Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server is not responding correctly. Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Make sure the server is running: uvicorn Task_A:app --reload")
        print(f"   Error: {e}")
        return False
    
    # Run tests
    test_suite = TaskATestSuite()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 