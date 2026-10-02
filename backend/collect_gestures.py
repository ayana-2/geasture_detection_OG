import cv2
import mediapipe as mp
import csv
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

os.makedirs('data', exist_ok=True)

# All gestures: A-Z, SPACE, DEL
gestures = [chr(i) for i in range(ord('A'), ord('Z')+1)] + ['SPACE', 'DEL']

def collect_gesture(gesture):
    cap = cv2.VideoCapture(0)
    print(f"\n📸 Collecting: {gesture}")
    print("Press 's' to save, 'q' to quit")
    samples = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Extract 63 features (21 landmarks * 3)
            features = []
            for lm in hand_landmarks.landmark:
                features.extend([lm.x, lm.y, lm.z])
        
        cv2.putText(frame, f"{gesture} | Samples: {len(samples)}", (10,30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow('Collect Gestures', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and results.multi_hand_landmarks:
            samples.append(features)
            print(f"✅ Sample {len(samples)} saved")
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if samples:
        filepath = os.path.join('data', f'{gesture}.csv')
        with open(filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            for sample in samples:
                writer.writerow([gesture] + sample)
        print(f"💾 Saved {len(samples)} samples to {gesture}.csv")

# Collect for each gesture
for g in gestures:
    input(f"Press Enter to start collecting for {g}...")
    collect_gesture(g)