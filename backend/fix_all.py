import os
import sys
import subprocess

def fix_all_issues():
    print("🔧 Fixing all issues...")
    
    # 1. Create necessary directories
    directories = ['models', 'dataset', 'templates', 'utils']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}/")
    
    # 2. Create dummy model
    print("\n🤖 Creating dummy model...")
    create_dummy_model()
    
    # 3. Create index.html template
    print("\n📄 Creating HTML template...")
    create_index_html()
    
    # 4. Check and install missing packages
    print("\n📦 Checking packages...")
    check_packages()
    
    print("\n" + "="*50)
    print("✅ All issues fixed!")
    print("📁 Project structure created:")
    print("   backend/models/ - Contains classifier model")
    print("   backend/dataset/ - Contains labels")
    print("   backend/templates/ - Contains web interface")
    print("\n🚀 To run the application:")
    print("   cd C:\\gesture_live_detection\\backend")
    print("   python app.py")
    print("   Open http://localhost:5000 in browser")
    print("="*50)

def create_dummy_model():
    """Create dummy model and labels"""
    import pickle
    import numpy as np
    import json
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    
    # Create dummy model
    model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=20, random_state=42)
    )
    
    # Dummy training data
    X_dummy = np.random.randn(100, 78)
    y_dummy = np.random.randint(0, 26, 100)
    model.fit(X_dummy, y_dummy)
    
    # Save model
    with open('models/classifier_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Create labels
    labels = {str(i): chr(65 + i) for i in range(26)}
    labels.update({
        "26": "Hello", "27": "Thank You", "28": "Yes",
        "29": "No", "30": "Please", "31": "Help"
    })
    
    with open('dataset/labels.json', 'w') as f:
        json.dump(labels, f, indent=2)
    
    print("✅ Created dummy model and labels")

def create_index_html():
    """Create basic HTML template"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Sign Language Converter</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .video-container { text-align: center; margin: 20px 0; }
        video { max-width: 100%; border: 2px solid #333; }
        .controls { text-align: center; margin: 20px; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; }
        .result { text-align: center; font-size: 48px; margin: 20px; color: #4CAF50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Sign Language Converter</h1>
        <p>Show your hand gestures to the camera</p>
        
        <div class="video-container">
            <img id="videoFeed" src="/video_feed">
        </div>
        
        <div class="controls">
            <button onclick="startCamera()">Start Camera</button>
            <button onclick="stopCamera()">Stop Camera</button>
        </div>
        
        <div class="result" id="gestureResult">Waiting for gesture...</div>
        
        <div id="status" style="text-align:center; color:#666;">Status: Ready</div>
    </div>
    
    <script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>
    <script>
        const socket = io();
        
        socket.on('connect', () => {
            document.getElementById('status').innerHTML = 'Status: Connected ✅';
        });
        
        socket.on('new_gesture', (data) => {
            document.getElementById('gestureResult').innerHTML = data.gesture;
            document.getElementById('gestureResult').style.animation = 'none';
            setTimeout(() => {
                document.getElementById('gestureResult').style.animation = 'pulse 0.5s';
            }, 10);
        });
        
        function startCamera() {
            document.getElementById('videoFeed').src = '/video_feed';
            document.getElementById('status').innerHTML = 'Status: Camera started 🎥';
        }
        
        function stopCamera() {
            document.getElementById('videoFeed').src = '';
            document.getElementById('status').innerHTML = 'Status: Camera stopped ⏸️';
        }
        
        // Auto start camera
        window.onload = () => {
            setTimeout(startCamera, 1000);
        };
    </script>
</body>
</html>"""
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Created HTML template")

def check_packages():
    """Check and install required packages"""
    packages = [
        'flask', 'flask-cors', 'flask-socketio',
        'opencv-python', 'numpy', 'mediapipe',
        'scikit-learn', 'joblib', 'pandas'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    fix_all_issues()