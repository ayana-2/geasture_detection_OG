from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import time

app = Flask(__name__)
CORS(app)

print("=" * 60)
print("SIGN LANGUAGE DETECTION BACKEND")
print("=" * 60)
print("Starting server...")

@app.route('/')
def home():
    return jsonify({
        "status": "Server is running!",
        "message": "Sign Language Detection Backend",
        "endpoints": {
            "/": "This page",
            "/api/start": "Start detection",
            "/api/stop": "Stop detection",
            "/api/status": "Get status"
        }
    })

@app.route('/api/start')
def start():
    return jsonify({
        "success": True,
        "message": "Detection started"
    })

@app.route('/api/stop')
def stop():
    return jsonify({
        "success": True,
        "message": "Detection stopped"
    })

@app.route('/api/status')
def status():
    return jsonify({
        "status": "active",
        "detection": "running",
        "gesture": "Test gesture"
    })

if __name__ == '__main__':
    print("Server running at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)