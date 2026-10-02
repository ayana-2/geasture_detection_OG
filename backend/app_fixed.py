from flask import Flask, jsonify
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        "status": "Gesture Detection Backend",
        "message": "Server is running!",
        "endpoints": {
            "/": "This page",
            "/api/start": "Start gesture detection",
            "/api/stop": "Stop gesture detection",
            "/api/status": "Get current status"
        }
    })

@app.route('/api/start')
def start():
    return jsonify({
        "success": True,
        "message": "Gesture detection started"
    })

@app.route('/api/stop')
def stop():
    return jsonify({
        "success": True,
        "message": "Gesture detection stopped"
    })

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running",
        "detection": "inactive",
        "gesture": "none"
    })

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("=" * 60)
    print("GESTURE DETECTION BACKEND")
    print("=" * 60)
    print("Server starting on:")
    print(f"  • http://localhost:5000")
    print(f"  • http://127.0.0.1:5000")
    print(f"  • http://{local_ip}:5000")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 5000 is already in use. Please free the port and try again.")
            print("You can kill the process using port 5000 by running:")
            print("  netstat -ano | findstr :5000")
            print("  taskkill /PID <PID> /F")
        else:
            raise e