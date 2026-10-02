# ASL Alphabet Detection System

A real‑time American Sign Language (ASL) alphabet recognizer using a webcam.  
Built with Flask, MediaPipe, and OpenCV.

## Features
- Login (demo/demo123)
- Live camera feed with hand landmarks (red dots, white lines)
- Real‑time letter detection (A–Z)
- Detection history and alphabet grid
- Works even without a camera (virtual mode)

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python app.py`
3. Open http://127.0.0.1:5000 in your browser
4. Log in with `demo` / `demo123`

## Troubleshooting
- If camera feed is blank, check terminal for camera index messages.
- If no camera is detected, the app automatically switches to virtual mode.
- Press Ctrl+F5 to force a browser refresh.