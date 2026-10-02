from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "BACKEND IS WORKING!", "test": "success"})

@app.route('/api/test')
def test():
    return jsonify({"message": "API is working"})

if __name__ == '__main__':
    print("=" * 50)
    print("BACKEND TEST SERVER")
    print("=" * 50)
    print("Server starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
