@echo off
echo 🧪 Task A Comprehensive Test Suite for Windows
echo ==============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    echo Creating .env file template...
    echo ULTRASAFE_API_KEY=your-api-key-here > .env
    echo ULTRASAFE_API_BASE=https://api.us.inc/usf/v1/hiring/chat/completions >> .env
    echo Please edit .env file with your actual API key
    pause
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
pip install -r requirements_task_a.txt

REM Check if server is running
echo 🔍 Checking if server is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Server is not running. Please start it first with:
    echo    start_server.bat
    echo.
    echo Or run the simple tests instead:
    echo    run_tests.bat
    pause
    exit /b 1
)

REM Run the comprehensive test script
echo 🚀 Running comprehensive tests...
echo This will test webhooks, concurrent loads, and advanced features...
echo.
python test_task_a.py

echo.
echo Press any key to exit...
pause >nul 