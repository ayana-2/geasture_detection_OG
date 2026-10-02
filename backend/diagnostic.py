# diagnostic.py
import cv2
import mediapipe as mp
import sys

print("🔍 Diagnostic Check")
print("="*50)

# 1. Check Python version
print(f"Python: {sys.version}")

# 2. Check OpenCV
print(f"OpenCV: {cv2.__version__}")

# 3. Check MediaPipe
print(f"MediaPipe: {mp.__version__}")

# 4. Check camera
for i in range(4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Camera {i}: Connected")
        cap.release()
    else:
        print(f"❌ Camera {i}: Not connected")

print("="*50)
print("Diagnostic complete!")