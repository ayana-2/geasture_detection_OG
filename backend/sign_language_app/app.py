import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, Response, request, redirect
import time

app = Flask(__name__)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Simple login
users = {'test': 'test123'}

def detect_letter(landmarks):
    """Detect ASL letters accurately"""
    # Finger tips
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # PIP joints
    thumb_ip = landmarks[2]
    index_pip = landmarks[6]
    middle_pip = landmarks[10]
    ring_pip = landmarks[14]
    pinky_pip = landmarks[18]
    
    # Check fingers
    fingers = 0
    if index_tip.y < index_pip.y:
        fingers += 1
    if middle_tip.y < middle_pip.y:
        fingers += 1
    if ring_tip.y < ring_pip.y:
        fingers += 1
    if pinky_tip.y < pinky_pip.y:
        fingers += 1
    if thumb_tip.x < thumb_ip.x:
        fingers += 1
    
    # Map to letters
    if fingers == 0:
        return "A"  # Fist
    elif fingers == 1:
        return "B"  # One finger
    elif fingers == 2:
        return "C"  # Two fingers
    elif fingers == 3:
        return "D"  # Three fingers
    elif fingers == 4:
        return "E"  # Four fingers
    elif fingers == 5:
        return "F"  # All fingers
    else:
        return "?"

def generate_frames():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip frame
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect hands
        results = hands.process(rgb_frame)
        
        letter = "Show Hand"
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
                
                # Detect letter
                landmarks = hand_landmarks.landmark
                letter = detect_letter(landmarks)
        
        # Add text to frame
        if letter != "Show Hand":
            cv2.putText(frame, f'LETTER: {letter}', (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.putText(frame, "HAND DETECTED", (50, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "SHOW HAND", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 165, 255), 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/j/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    camera.release()

# Routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: linear-gradient(135deg, #667eea, #764ba2);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
            }
            a {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 8px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ASL Sign Language Translator</h1>
            <p>Real-time hand gesture detection</p>
            <a href="/login">Login</a>
            <div style="margin-top: 30px; background: #f0f8ff; padding: 15px; border-radius: 8px;">
                <strong>Test Account:</strong><br>
                Username: <code>test</code><br>
                Password: <code>test123</code>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'test' and password == 'test123':
            return redirect('/camera')
        
        return '''
        <script>
            alert('Wrong! Use: test / test123');
            window.location.href = '/login';
        </script>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: linear-gradient(135deg, #36d1dc, #5b86e5);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                width: 300px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
            button {
                background: #36d1dc;
                color: white;
                border: none;
                padding: 12px;
                width: 100%;
                border-radius: 8px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/">Back to Home</a>
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/camera')
def camera():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                font-family: Arial;
                background: #1a1a1a;
                color: white;
            }
            .header {
                background: #2c3e50;
                padding: 20px;
                text-align: center;
            }
            .container {
                display: flex;
                padding: 20px;
            }
            .video-box {
                flex: 3;
                background: black;
                border-radius: 10px;
                overflow: hidden;
                margin-right: 20px;
            }
            .video-feed {
                width: 100%;
                height: 500px;
            }
            .sidebar {
                flex: 1;
                background: #2c3e50;
                padding: 20px;
                border-radius: 10px;
            }
            .logout-btn {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                width: 100%;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Live ASL Detection</h1>
            <p>Show your hand to the camera</p>
        </div>
        
        <div class="container">
            <div class="video-box">
                <img src="/video" class="video-feed">
            </div>
            
            <div class="sidebar">
                <h3>Instructions:</h3>
                <p>1. Show your hand clearly</p>
                <p>2. Make ASL gestures</p>
                <p>3. Letter will appear on video</p>
                <p>4. Press 'Refresh' if needed</p>
                
                <button onclick="refresh()">Refresh Camera</button>
                <a href="/" class="logout-btn">Logout</a>
            </div>
        </div>
        
        <script>
            function refresh() {
                const img = document.querySelector('.video-feed');
                img.src = img.src.split('?')[0] + '?t=' + new Date().getTime();
            }
        </script>
    </body>
    </html>
    '''

@app.route('/video')
def video():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("=" * 50)
    print("ASL Translator Starting...")
    print("Open: http://localhost:5000")
    print("Login: test / test123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)