import cv2
import mediapipe as mp
import numpy as np
import time
import joblib
import atexit
from flask import Flask, Response, render_template, request, redirect, url_for, session
from functools import wraps

# ---------------- Flask ----------------
app = Flask(__name__)
app.secret_key = "asl_secret_key"

# ---------------- Load ML files ----------------
model = joblib.load("asl_model.pkl")
scaler = joblib.load("scaler.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# ---------------- MediaPipe ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# ---------------- Camera ----------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# ---------------- Sentence Logic ----------------
sentence = ""
last_letter = ""
last_time = 0
COOLDOWN = 2.5

# ---------------- Login Decorator ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------------- Routes ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "gangso" and password == "ct2":
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("index.html", sentence=sentence)

@app.route("/video")
@login_required
def video():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/get_sentence")
@login_required
def get_sentence():
    return sentence

@app.route("/clear_sentence")
@login_required
def clear_sentence():
    global sentence
    sentence = ""
    return "cleared"

@app.route("/delete_last")
@login_required
def delete_last():
    global sentence
    sentence = sentence[:-1]
    return "deleted"

@app.route("/add_space", methods=["GET", "POST"])
@login_required
def add_space():
    global sentence
    sentence += " "
    return "space added"

# 🆕 New route: delete a character at a specific position
@app.route("/delete_char/<int:pos>", methods=["POST"])
@login_required
def delete_char(pos):
    global sentence
    if 0 <= pos < len(sentence):
        sentence = sentence[:pos] + sentence[pos+1:]
    return "deleted"

# ---------------- Camera Generator ----------------
def generate_frames():
    global sentence, last_letter, last_time
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=2),
                mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1)
            )

            features = []
            for lm in hand.landmark:
                features.extend([lm.x, lm.y, lm.z])

            features = scaler.transform([features])
            pred = model.predict(features)[0]
            gesture = label_encoder.inverse_transform([pred])[0]

            cv2.putText(frame, gesture, (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (0, 255, 0), 4)

            now = time.time()
            if gesture != last_letter and (now - last_time) > COOLDOWN:
                if gesture == "SPACE":
                    sentence += " "
                elif gesture == "DEL":
                    sentence = sentence[:-1]
                else:
                    sentence += gesture
                last_letter = gesture
                last_time = now

        cv2.putText(frame, sentence[-40:], (20, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

# ---------------- Cleanup ----------------
@atexit.register
def cleanup():
    cap.release()
    cv2.destroyAllWindows()
    print("👋 Camera released")

# ---------------- Run ----------------
if __name__ == "__main__":
    print("\n🚀 ASL SIGN LANGUAGE DETECTOR (FINAL)")
    print("🌐 http://127.0.0.1:5000")
    print("🔑 Login → gangso / ct2\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)