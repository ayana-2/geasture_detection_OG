@echo off
chcp 65001 > nul
echo ============================================
echo    Gesture Detection Project - Complete Setup
echo ============================================
echo.

REM Create main project directory
cd /d "C:\"
if not exist "gesture_detection_simple" mkdir gesture_detection_simple
cd gesture_detection_simple

echo 📁 Creating project structure...
mkdir backend
mkdir backend\templates
mkdir backend\models
mkdir backend\utils
mkdir dataset

echo 📄 Creating project files...

REM Create requirements.txt
echo flask==2.3.3 > backend\requirements.txt
echo flask-cors==4.0.0 >> backend\requirements.txt
echo opencv-python==4.8.1.78 >> backend\requirements.txt
echo numpy==1.24.3 >> backend\requirements.txt
echo mediapipe==0.10.8 >> backend\requirements.txt

REM Create simple app.py
echo from flask import Flask, render_template_string, Response > backend\app.py
echo import cv2 >> backend\app.py
echo import numpy as np >> backend\app.py
echo import threading >> backend\app.py
echo import time >> backend\app.py
echo. >> backend\app.py
echo app = Flask(__name__) >> backend\app.py
echo. >> backend\app.py
echo # Global variables >> backend\app.py
echo current_frame = None >> backend\app.py
echo is_camera_running = False >> backend\app.py
echo. >> backend\app.py
echo def camera_worker(): >> backend\app.py
echo     global current_frame, is_camera_running >> backend\app.py
echo     import cv2 >> backend\app.py
echo. >> backend\app.py
echo     # Try different camera indices >> backend\app.py
echo     cap = None >> backend\app.py
echo     for i in range(4): >> backend\app.py
echo         cap = cv2.VideoCapture(i) >> backend\app.py
echo         if cap.isOpened(): >> backend\app.py
echo             print(f"✅ Using camera index {i}") >> backend\app.py
echo             break >> backend\app.py
echo. >> backend\app.py
echo     if not cap or not cap.isOpened(): >> backend\app.py
echo         print("❌ No camera found") >> backend\app.py
echo         error_frame = np.zeros((480, 640, 3), dtype=np.uint8) >> backend\app.py
echo         cv2.putText(error_frame, "NO CAMERA FOUND", (100, 200), >> backend\app.py
echo                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) >> backend\app.py
echo         current_frame = error_frame >> backend\app.py
echo         return >> backend\app.py
echo. >> backend\app.py
echo     is_camera_running = True >> backend\app.py
echo     print("📸 Camera started successfully!") >> backend\app.py
echo. >> backend\app.py
echo     while is_camera_running: >> backend\app.py
echo         ret, frame = cap.read() >> backend\app.py
echo         if not ret: >> backend\app.py
echo             break >> backend\app.py
echo. >> backend\app.py
echo         # Process frame >> backend\app.py
echo         frame = cv2.flip(frame, 1)  # Mirror effect >> backend\app.py
echo. >> backend\app.py
echo         # Add text overlay >> backend\app.py
echo         cv2.putText(frame, "Gesture Detection System", (10, 30), >> backend\app.py
echo                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) >> backend\app.py
echo         cv2.putText(frame, "Show your hand to camera", (10, 70), >> backend\app.py
echo                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2) >> backend\app.py
echo. >> backend\app.py
echo         # Draw center crosshair >> backend\app.py
echo         h, w = frame.shape[:2] >> backend\app.py
echo         cv2.line(frame, (w//2, h//2-20), (w//2, h//2+20), (0, 255, 0), 2) >> backend\app.py
echo         cv2.line(frame, (w//2-20, h//2), (w//2+20, h//2), (0, 255, 0), 2) >> backend\app.py
echo. >> backend\app.py
echo         current_frame = frame >> backend\app.py
echo         time.sleep(0.03) >> backend\app.py
echo. >> backend\app.py
echo     cap.release() >> backend\app.py
echo. >> backend\app.py
echo @app.route('/') >> backend\app.py
echo def home(): >> backend\app.py
echo     return ''' >> backend\app.py
echo     <!DOCTYPE html> >> backend\app.py
echo     <html> >> backend\app.py
echo     <head> >> backend\app.py
echo         <title>Gesture Detection</title> >> backend\app.py
echo         <style> >> backend\app.py
echo             body { font-family: Arial; text-align: center; padding: 20px; background: #f0f0f0; } >> backend\app.py
echo             .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); } >> backend\app.py
echo             video { max-width: 100%; border: 2px solid #333; } >> backend\app.py
echo             button { padding: 10px 20px; margin: 10px; font-size: 16px; } >> backend\app.py
echo         </style> >> backend\app.py
echo     </head> >> backend\app.py
echo     <body> >> backend\app.py
echo         <div class="container"> >> backend\app.py
echo             <h1>Gesture Detection System</h1> >> backend\app.py
echo             <p>Real-time hand gesture recognition</p> >> backend\app.py
echo             <img id="videoFeed" src="/video_feed"> >> backend\app.py
echo             <div> >> backend\app.py
echo                 <button onclick="startCamera()">Start Camera</button> >> backend\app.py
echo                 <button onclick="stopCamera()">Stop Camera</button> >> backend\app.py
echo             </div> >> backend\app.py
echo             <div id="status">Status: Ready</div> >> backend\app.py
echo         </div> >> backend\app.py
echo         <script> >> backend\app.py
echo             function startCamera() { >> backend\app.py
echo                 document.getElementById('videoFeed').src = '/video_feed'; >> backend\app.py
echo                 document.getElementById('status').innerHTML = '✅ Camera started'; >> backend\app.py
echo             } >> backend\app.py
echo             function stopCamera() { >> backend\app.py
echo                 document.getElementById('videoFeed').src = ''; >> backend\app.py
echo                 document.getElementById('status').innerHTML = '⏸️ Camera stopped'; >> backend\app.py
echo             } >> backend\app.py
echo             // Auto start >> backend\app.py
echo             window.onload = function() { >> backend\app.py
echo                 setTimeout(startCamera, 1000); >> backend\app.py
echo             }; >> backend\app.py
echo         </script> >> backend\app.py
echo     </body> >> backend\app.py
echo     </html> >> backend\app.py
echo     ''' >> backend\app.py
echo. >> backend\app.py
echo def generate_frames(): >> backend\app.py
echo     global current_frame >> backend\app.py
echo     while True: >> backend\app.py
echo         if current_frame is not None: >> backend\app.py
echo             ret, buffer = cv2.imencode('.jpg', current_frame) >> backend\app.py
echo             frame_bytes = buffer.tobytes() >> backend\app.py
echo             yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n') >> backend\app.py
echo         time.sleep(0.03) >> backend\app.py
echo. >> backend\app.py
echo @app.route('/video_feed') >> backend\app.py
echo def video_feed(): >> backend\app.py
echo     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') >> backend\app.py
echo. >> backend\app.py
echo if __name__ == '__main__': >> backend\app.py
echo     print("🚀 Starting Gesture Detection System...") >> backend\app.py
echo. >> backend\app.py
echo     # Start camera thread >> backend\app.py
echo     import threading >> backend\app.py
echo     cam_thread = threading.Thread(target=camera_worker, daemon=True) >> backend\app.py
echo     cam_thread.start() >> backend\app.py
echo. >> backend\app.py
echo     print("✅ System initialized!") >> backend\app.py
echo     print("🌐 Open: http://localhost:5000") >> backend\app.py
echo. >> backend\app.py
echo     # Wait for camera >> backend\app.py
echo     time.sleep(2) >> backend\app.py
echo. >> backend\app.py
echo     app.run(host='0.0.0.0', port=5000, debug=True) >> backend\app.py

echo ✅ Created backend\app.py

REM Create run.bat
echo @echo off > run.bat
echo cd /d "C:\gesture_detection_simple\backend" >> run.bat
echo echo Installing requirements... >> run.bat
echo pip install -r requirements.txt >> run.bat
echo echo Starting application... >> run.bat
echo python app.py >> run.bat
echo pause >> run.bat

echo ✅ Created run.bat

echo.
echo ============================================
echo ✅ Setup completed successfully!
echo.
echo 📁 Project location: C:\gesture_detection_simple\
echo.
echo 🚀 To run the application:
echo    1. Double-click run.bat
echo    2. Or open command prompt and run:
echo       cd C:\gesture_detection_simple\backend
echo       pip install -r requirements.txt
echo       python app.py
echo.
echo 🌐 Then open in browser: http://localhost:5000
echo ============================================
echo.
pause