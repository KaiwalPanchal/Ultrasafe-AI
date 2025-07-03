# Task A Testing Guide

This guide will help you test your Task A FastAPI NLP application to ensure everything is working correctly.

## 🚀 Quick Start

### Windows Users
1. **Double-click `run_tests.bat`** to run all tests automatically
2. **Double-click `start_server.bat`** to start the server
3. **Or use PowerShell/Command Prompt:**
   ```cmd
   python simple_test_task_a.py
   ```

### All Platforms
1. **Install Dependencies**
   ```bash
   pip install -r requirements_task_a.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file in your project root:
   ```env
   ULTRASAFE_API_KEY=your-api-key-here
   ULTRASAFE_API_BASE=https://api.us.inc/usf/v1/hiring/chat/completions
   ```

3. **Run the Application**
   ```bash
   python run_task_a.py
   ```

## 🧪 Automated Testing

### Run All Tests
```bash
python simple_test_task_a.py
```

This will test:
- ✅ Server health and connectivity
- ✅ All NLP endpoints (classification, sentiment, NER, summarization)
- ✅ Batch processing (single and multiple texts)
- ✅ Caching system (hit/miss performance)
- ✅ Performance monitoring endpoints
- ✅ API documentation availability

### Expected Output
```
🧪 Task A Simple Test Suite
========================================
Checking server health...
✅ Server is healthy! Using model: usf1-mini

========================================
Testing NLP Endpoints
========================================
Testing /classify...
  ✅ Success! Processed 5 texts
Testing /sentiment...
  ✅ Success! Processed 5 texts
Testing /extract...
  ✅ Success! Processed 5 texts
Testing /summarize...
  ✅ Success! Processed 1 texts

========================================
Testing Batch Processing
========================================
Testing /classify...
  ✅ Success! Processed 1 texts
Testing /classify...
  ✅ Success! Processed 10 texts

========================================
Testing Caching System
========================================
Testing GET /cache/stats...
  ✅ Success!
Testing cache performance...
  First request: 1.234s
  Second request: 0.012s
  Speedup: 102.8x
Testing cache clear...
  ✅ Cache cleared successfully

========================================
Testing Performance Monitoring
========================================
Testing GET /performance...
  ✅ Success!
Testing GET /cache/stats...
  ✅ Success!

========================================
Testing API Documentation
========================================
✅ Swagger UI available at /docs
✅ ReDoc available at /redoc

========================================
Test Summary
========================================
Successful tests: 9/9
Success rate: 100.0%

🎉 ALL TESTS PASSED! Your Task A application is working correctly!
```

## 🔍 Manual Testing

### 1. Web Interface
Open your browser and go to:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 2. Test Individual Endpoints

#### Text Classification
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Artificial intelligence is transforming technology."]
  }'
```

#### Sentiment Analysis
```bash
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["I love this amazing product!"]
  }'
```

#### Entity Extraction
```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Apple CEO Tim Cook announced new products in San Francisco."]
  }'
```

#### Text Summarization
```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Long article text here..."]
  }'
```

### 3. Test Batch Processing
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "AI is amazing!",
      "The stock market is up today.",
      "Football game was exciting."
    ]
  }'
```

### 4. Test Caching
```bash
# First request (will be slower)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Test caching performance"]}'

# Second request (should be much faster due to cache)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Test caching performance"]}'
```

### 5. Check Performance Metrics
```bash
# Get performance metrics
curl http://localhost:8000/performance

# Get cache statistics
curl http://localhost:8000/cache/stats

# Clear cache
curl -X POST http://localhost:8000/cache/clear
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Server Won't Start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Install dependencies
```bash
pip install -r requirements_task_a.txt
```

#### 2. API Key Error
**Error**: `ULTRASAFE_API_KEY environment variable is not set`
**Solution**: Set your API key in `.env` file
```env
ULTRASAFE_API_KEY=your-actual-api-key
```

#### 3. Connection Refused
**Error**: `Connection refused` when running tests
**Solution**: Make sure the server is running
```bash
python run_task_a.py
# Choose option 1 to start the server
```

#### 4. Slow Responses
**Expected**: First requests are slow, subsequent requests are fast due to caching
**Solution**: This is normal behavior. Check cache performance in the test output.

### Performance Expectations

- **First Request**: 1-3 seconds (API call to UltraSafe)
- **Cached Request**: 0.01-0.1 seconds (from cache)
- **Batch Processing**: Scales linearly with number of texts
- **Cache Hit Rate**: Should improve with repeated requests

## 📊 Monitoring

### Performance Endpoints
- `/performance` - System metrics
- `/cache/stats` - Cache statistics
- `/health` - Service health check

### Expected Metrics
```json
{
  "cache": {
    "size": 15,
    "max_size": 1000,
    "hit_rate": "N/A"
  },
  "task_queue": {
    "active_tasks": 0,
    "pending_tasks": 0,
    "max_concurrent": 5,
    "completed_tasks": 0
  }
}
```

## ✅ Success Criteria

Your Task A application is working correctly if:

1. ✅ All automated tests pass (9/9)
2. ✅ Server starts without errors
3. ✅ All NLP endpoints return valid results
4. ✅ Caching provides significant speedup (10x+ faster)
5. ✅ Batch processing works for multiple texts
6. ✅ Performance monitoring endpoints return data
7. ✅ API documentation is accessible

## 🎯 Next Steps

Once testing is complete:

1. **Production Deployment**: Consider using Redis for distributed caching
2. **Load Testing**: Test with higher concurrent loads
3. **Monitoring**: Set up proper monitoring and alerting
4. **Documentation**: Update API documentation for your specific use case

---

**Happy Testing! 🚀** 