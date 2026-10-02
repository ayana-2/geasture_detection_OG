# app_test.py - Minimal Flask server without TensorFlow
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "status": "Server is running!",
        "message": "Sign Language Backend API"
    })

@app.route('/api/test')
def test():
    return jsonify({
        "detected_sign": "HELLO",
        "confidence": 0.95,
        "mode": "test"
    })

if __name__ == '__main__':
    print("✅ Server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)