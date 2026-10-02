# test_server.py - Simple Flask server with no dependencies
from flask import Flask, jsonify
import datetime

app = Flask(__name__)

# Very simple CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def home():
    return jsonify({
        "status": "Server is running!",
        "message": "Sign Language Backend",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test_api():
    return jsonify({
        "success": True,
        "detected_sign": "HELLO",
        "confidence": 0.95,
        "message": "Test response - server is working!",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/api/detect', methods=['POST'])
def detect():
    # Simple echo for testing
    return jsonify({
        "success": True,
        "detected_sign": "TEST_GESTURE",
        "confidence": 0.88,
        "mode": "test_server",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 TEST SERVER STARTING")
    print("=" * 50)
    print("🌐 REST API: http://localhost:5000")
    print("📤 POST to: http://localhost:5000/api/detect")
    print("📋 GET from: http://localhost:5000/api/test")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run without debug mode for more stability
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)