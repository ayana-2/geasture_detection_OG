import cv2
import mediapipe as mp
import numpy as np
import joblib

model = joblib.load('asl_model.pkl')
scaler = joblib.load('scaler.pkl')
encoder = joblib.load('label_encoder.pkl')

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

print("🔍 Debug Mode - Showing Top 3 Predictions")
print("Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    if results.multi_hand_landmarks:
        h = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(frame, h, mp_hands.HAND_CONNECTIONS)
        
        features = []
        for lm in h.landmark:
            features.extend([lm.x, lm.y, lm.z])
        
        features_scaled = scaler.transform([features])
        proba = model.predict_proba(features_scaled)[0]
        top3 = np.argsort(proba)[-3:][::-1]
        
        y_pos = 30
        for i, idx in enumerate(top3):
            letter = encoder.inverse_transform([idx])[0]
            confidence = proba[idx]
            color = (0, 255, 0) if i == 0 else (0, 255, 255)
            cv2.putText(frame, f"{i+1}: {letter} ({confidence:.2f})", 
                        (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_pos += 30
    else:
        cv2.putText(frame, "No hand", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    
    cv2.imshow('Debug - Top 3 Predictions', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()