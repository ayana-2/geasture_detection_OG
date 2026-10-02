from flask import Flask, render_template_string, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import json
import os

app = Flask(__name__)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Global variables
current_frame = None
gesture_text = "Show your hand"
gesture_history = []
is_camera_running = False
camera_thread = None

# Create directories
os.makedirs('models', exist_ok=True)
os.makedirs('dataset', exist_ok=True)

# Create dummy labels if not exists
if not os.path.exists('dataset/labels.json'):
    labels = {str(i): chr(65 + i) for i in range(26)}  # A-Z
    with open('dataset/labels.json', 'w') as f:
        json.dump(labels, f, indent=2)

def camera_worker():
    """Camera worker thread"""
    global current_frame, gesture_text, is_camera_running
    
    # Try different camera indices
    cap = None
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"📸 Using camera index {i}")
            break
        elif cap:
            cap.release()
    
    if not cap or not cap.isOpened():
        print("❌ No camera found")
        # Create black frame with error message
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "NO CAMERA FOUND", (100, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(error_frame, "Connect camera and restart", (80, 250),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        current_frame = error_frame
        is_camera_running = False
        return
    
    # Initialize hand detector
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    is_camera_running = True
    
    while is_camera_running:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Detect hands
        results = hands.process(rgb_frame)
        
        # Convert back to BGR
        rgb_frame.flags.writeable = True
        output_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # Reset gesture text
        gesture_text = "Show your hand"
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                 results.multi_handedness):
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    output_frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Get hand type (left/right)
                hand_type = handedness.classification[0].label
                
                # Simple gesture detection based on finger positions
                detected_gesture = detect_simple_gesture(hand_landmarks)
                
                # Update global gesture text
                gesture_text = f"{hand_type}: {detected_gesture}"
                
                # Add to history
                timestamp = time.strftime("%H:%M:%S")
                gesture_history.append({
                    "gesture": detected_gesture,
                    "hand": hand_type,
                    "time": timestamp
                })
                
                # Keep only last 10 gestures
                if len(gesture_history) > 10:
                    gesture_history.pop(0)
                
                # Draw gesture text
                h, w, _ = output_frame.shape
                x_coords = [lm.x for lm in hand_landmarks.landmark]
                y_coords = [lm.y for lm in hand_landmarks.landmark]
                
                x_min = int(min(x_coords) * w)
                y_min = int(min(y_coords) * h)
                
                cv2.putText(output_frame, detected_gesture, (x_min, y_min-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        else:
            # No hand detected
            cv2.putText(output_frame, "No hand detected", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Add FPS counter
        current_frame = output_frame
        
        time.sleep(0.03)  # ~30 FPS
    
    cap.release()
    hands.close()
    print("Camera stopped")

def detect_simple_gesture(hand_landmarks):
    """Simple gesture detection based on finger positions"""
    # Landmark indices for fingertips
    tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    
    # Get y-coordinates of fingertips
    y_coords = [hand_landmarks.landmark[i].y for i in tip_ids]
    
    # Get y-coordinates of corresponding PIP joints
    pip_ids = [3, 6, 10, 14, 18]
    pip_y_coords = [hand_landmarks.landmark[i].y for i in pip_ids]
    
    # Check which fingers are extended (tip higher than pip)
    extended_fingers = []
    for i in range(len(tip_ids)):
        if y_coords[i] < pip_y_coords[i]:  # Tip is above pip joint
            extended_fingers.append(1)
        else:
            extended_fingers.append(0)
    
    # Simple gesture recognition
    # Count extended fingers
    finger_count = sum(extended_fingers)
    
    # Basic ASL gestures
    if extended_fingers == [0, 1, 0, 0, 0]:  # Index finger only
        return "A (Index Up)"
    elif extended_fingers == [1, 1, 0, 0, 0]:  # Thumb + Index
        return "L"
    elif extended_fingers == [0, 1, 1, 0, 0]:  # Peace sign
        return "V/Peace"
    elif extended_fingers == [1, 1, 1, 1, 1]:  # All fingers
        return "5/All Open"
    elif extended_fingers == [0, 0, 0, 0, 0]:  # Fist
        return "Fist/0"
    elif finger_count == 1:
        return f"1 Finger"
    elif finger_count == 2:
        return f"2 Fingers"
    elif finger_count == 3:
        return f"3 Fingers"
    elif finger_count == 4:
        return f"4 Fingers"
    else:
        return f"Gesture {finger_count}"

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        if current_frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', current_frame, 
                                      [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        time.sleep(0.03)

@app.route('/')
def home():
    """Main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sign Language Converter - Complete Solution</title>
        <meta charset="utf-8">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                padding: 30px 0;
                border-bottom: 2px solid #0f3460;
                margin-bottom: 30px;
            }
            
            .logo {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                margin-bottom: 15px;
            }
            
            .logo i {
                font-size: 40px;
                color: #00adb5;
            }
            
            .logo h1 {
                font-size: 36px;
                background: linear-gradient(45deg, #00adb5, #64dfdf);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            
            .subtitle {
                color: #8f9ba8;
                font-size: 18px;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 400px;
                gap: 30px;
            }
            
            @media (max-width: 1024px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
            }
            
            .video-section, .results-section {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .video-container {
                position: relative;
                width: 100%;
                height: 500px;
                border-radius: 15px;
                overflow: hidden;
                background: #0f3460;
                margin-bottom: 20px;
            }
            
            #videoFeed {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .controls {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin: 20px 0;
            }
            
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: linear-gradient(45deg, #00adb5, #0077b6);
                color: white;
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 173, 181, 0.4);
            }
            
            .current-gesture {
                background: rgba(15, 52, 96, 0.5);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 25px;
                text-align: center;
                border: 2px solid #00adb5;
            }
            
            .gesture-text {
                font-size: 48px;
                font-weight: bold;
                color: #64dfdf;
                margin-bottom: 10px;
                min-height: 60px;
            }
            
            .history-list {
                max-height: 300px;
                overflow-y: auto;
                margin-top: 20px;
            }
            
            .history-item {
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 3px solid #64dfdf;
            }
            
            .history-gesture {
                font-size: 20px;
                font-weight: bold;
                color: #64dfdf;
            }
            
            .history-time {
                font-size: 12px;
                color: #8f9ba8;
            }
            
            .status-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.9);
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top: 1px solid #0f3460;
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #00adb5;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .instructions {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
            }
            
            .step {
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-top: 20px;
            }
            
            .stat-box {
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 20px;
                color: #64dfdf;
                font-weight: bold;
            }
            
            .stat-label {
                font-size: 12px;
                color: #8f9ba8;
                margin-top: 5px;
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo">
                    <i class="fas fa-hands"></i>
                    <h1>Sign Language Converter</h1>
                </div>
                <p class="subtitle">Real-time hand gesture recognition with MediaPipe</p>
            </header>
            
            <div class="main-content">
                <!-- Video Section -->
                <div class="video-section">
                    <h2><i class="fas fa-video"></i> Live Camera Feed</h2>
                    
                    <div class="video-container">
                        <img id="videoFeed" src="/video_feed">
                    </div>
                    
                    <div class="controls">
                        <button class="btn btn-primary" onclick="startCamera()">
                            <i class="fas fa-play"></i> Start Camera
                        </button>
                        <button class="btn btn-secondary" onclick="stopCamera()">
                            <i class="fas fa-stop"></i> Stop Camera
                        </button>
                        <button class="btn btn-secondary" onclick="captureGesture()">
                            <i class="fas fa-camera"></i> Capture
                        </button>
                    </div>
                    
                    <div class="instructions">
                        <h3><i class="fas fa-info-circle"></i> How to use:</h3>
                        <div class="step">1. Click "Start Camera" button</div>
                        <div class="step">2. Allow camera permission in browser</div>
                        <div class="step">3. Show your hand to the camera</div>
                        <div class="step">4. System will detect gestures automatically</div>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-value" id="fpsCounter">0</div>
                            <div class="stat-label">FPS</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value" id="gestureCounter">0</div>
                            <div class="stat-label">Gestures</div>
                        </div>
                    </div>
                </div>
                
                <!-- Results Section -->
                <div class="results-section">
                    <div class="current-gesture">
                        <div style="font-size: 14px; color: #8f9ba8;">Current Gesture</div>
                        <div class="gesture-text" id="currentGesture">--</div>
                        <div id="gestureDescription">Show hand to camera</div>
                    </div>
                    
                    <h2><i class="fas fa-history"></i> Gesture History</h2>
                    <div class="history-list" id="historyList">
                        <!-- History will be populated here -->
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <h3><i class="fas fa-lightbulb"></i> Tips:</h3>
                        <p style="color: #8f9ba8; font-size: 14px;">
                            • Ensure good lighting<br>
                            • Use plain background<br>
                            • Keep hand visible<br>
                            • Try different gestures
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="status-bar">
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Status: <span id="systemStatus">Ready</span></span>
                </div>
                <div>
                    <span id="connectionStatus">Camera: Stopped</span>
                </div>
            </div>
        </div>
        
        <script>
            let gestureCount = 0;
            let fps = 0;
            let lastTime = Date.now();
            let frameCount = 0;
            
            // Update FPS counter
            function updateFPS() {
                frameCount++;
                const currentTime = Date.now();
                if (currentTime - lastTime >= 1000) {
                    fps = frameCount;
                    frameCount = 0;
                    lastTime = currentTime;
                    document.getElementById('fpsCounter').textContent = fps;
                }
                requestAnimationFrame(updateFPS);
            }
            
            // Start camera
            function startCamera() {
                document.getElementById('videoFeed').src = '/video_feed';
                document.getElementById('systemStatus').textContent = 'Camera Active';
                document.getElementById('connectionStatus').textContent = 'Camera: Running';
                updateStatus('Camera started successfully', 'success');
            }
            
            // Stop camera
            function stopCamera() {
                document.getElementById('videoFeed').src = '';
                document.getElementById('systemStatus').textContent = 'Camera Stopped';
                document.getElementById('connectionStatus').textContent = 'Camera: Stopped';
                updateStatus('Camera stopped', 'info');
            }
            
            // Capture gesture
            function captureGesture() {
                fetch('/get_gesture')
                    .then(response => response.json())
                    .then(data => {
                        if (data.gesture !== 'Show your hand') {
                            gestureCount++;
                            document.getElementById('gestureCounter').textContent = gestureCount;
                            
                            // Add to history
                            addToHistory(data.gesture, data.timestamp);
                            updateStatus('Gesture captured: ' + data.gesture, 'success');
                        }
                    });
            }
            
            // Add gesture to history
            function addToHistory(gesture, timestamp) {
                const historyList = document.getElementById('historyList');
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div class="history-gesture">${gesture}</div>
                    <div class="history-time">${timestamp}</div>
                `;
                
                // Add to top
                historyList.insertBefore(historyItem, historyList.firstChild);
                
                // Limit to 10 items
                if (historyList.children.length > 10) {
                    historyList.removeChild(historyList.lastChild);
                }
            }
            
            // Update status
            function updateStatus(message, type) {
                const statusElement = document.getElementById('systemStatus');
                statusElement.textContent = message;
                
                // Color coding
                const colors = {
                    'success': '#4CAF50',
                    'error': '#F44336',
                    'info': '#2196F3'
                };
                
                statusElement.style.color = colors[type] || colors.info;
                
                // Auto reset after 3 seconds
                setTimeout(() => {
                    statusElement.textContent = 'Camera Active';
                    statusElement.style.color = '';
                }, 3000);
            }
            
            // Auto start camera
            window.onload = function() {
                setTimeout(startCamera, 1000);
                updateFPS();
                
                // Update gesture from server every second
                setInterval(() => {
                    fetch('/get_gesture')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('currentGesture').textContent = data.gesture;
                            document.getElementById('gestureDescription').textContent = 
                                data.hand ? `${data.hand} hand detected` : 'Show hand to camera';
                        });
                }, 1000);
            };
        </script>
    </body>
    </html>
    ''')

@app.route('/video_feed')
def video_feed():
    """Video streaming endpoint"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_gesture')
def get_gesture():
    """Get current gesture"""
    global gesture_text, gesture_history
    return jsonify({
        'gesture': gesture_text,
        'timestamp': time.strftime("%H:%M:%S"),
        'history': gesture_history[-5:],
        'camera_status': is_camera_running
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'camera': is_camera_running,
        'service': 'Sign Language Converter',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("="*60)
    print("🎬 SIGN LANGUAGE CONVERTER - COMPLETE SOLUTION")
    print("="*60)
    print("🚀 Starting camera and hand detection...")
    
    # Start camera in background thread
    camera_thread = threading.Thread(target=camera_worker, daemon=True)
    camera_thread.start()
    
    # Wait for camera to initialize
    time.sleep(2)
    
    print("\n✅ System initialized!")
    print("📡 Open in browser:")
    print("   http://localhost:5000")
    print("   http://127.0.0.1:5000")
    print("\n🎯 Tips:")
    print("   • Ensure camera is connected")
    print("   • Allow camera permission in browser")
    print("   • Show hand clearly to camera")
    print("="*60)
    
    # Run Flask app
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except OSError:
        print("⚠️  Port 5000 busy. Trying port 5001...")
        app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)