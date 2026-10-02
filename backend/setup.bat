@echo off
echo Setting up ASL Translator...
echo.

cd /d "C:\asl_translator"

echo Creating necessary folders...
mkdir templates 2>nul

echo Creating files...
echo Please copy the code from above into these files.

echo.
echo Installing dependencies...
pip install flask opencv-python mediapipe numpy

echo.
echo Setup complete!
echo Run: python app.py
echo.
pause