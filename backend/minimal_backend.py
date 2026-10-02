

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("=" * 50)
print("STARTING BACKEND SERVER")
print("=" * 50)

@app.route('/')
def home():
    print("Someone visited /")
    return jsonify({"status": "WORKING", "message": "Server is running!"})

@app.route('/api/test')
def test():
    return jsonify({"success": True, "data": "Test successful"})

if __name__ == '__main__':
    print("Trying to start server...")
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except Exception as e:
        print(f"Port 5000 failed: {e}")
        print("Trying port 5001...")
        app.run(host="0.0.0.0", port=5001, debug=False)
