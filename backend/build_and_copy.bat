# build_and_copy.bat (Windows batch file)
@echo off
echo Building Flutter web app...
cd /d C:\gesture_live_detection\flutter_app
call flutter build web --release

echo.
echo Copying files to backend...
if exist "C:\gesture_live_detection\backend\static" (
    rmdir /s /q "C:\gesture_live_detection\backend\static"
)
mkdir "C:\gesture_live_detection\backend\static"
xcopy /E /I /Y "C:\gesture_live_detection\flutter_app\build\web\*" "C:\gesture_live_detection\backend\static\"

echo.
echo ✅ Build and copy completed!
echo.
echo To run backend:
echo   cd C:\gesture_live_detection\backend
echo   python app.py
pause