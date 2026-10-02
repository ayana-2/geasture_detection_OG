@echo off
echo.
echo ============================================
echo        ASL TRANSLATOR SYSTEM
echo ============================================
echo.

cd /d "C:\asl_project"

echo Installing dependencies...
pip install flask opencv-python mediapipe numpy

echo.
echo Starting application...
echo.
echo OPEN YOUR BROWSER AND GO TO:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python app.py

pause