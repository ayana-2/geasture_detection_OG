# Save as test_gestures.py
# Run this to test if your gestures are detected correctly

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

def detect_asl_letter(landmarks):
    # Same detection function as in app.py
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    thumb_ip = landmarks[2]
    index_pip = landmarks[6]
    middle_pip = landmarks[10]
    ring_pip = landmarks[14]
    pinky_pip = landmarks[18]
    
    # FIST (A)
    if (index_tip.y > index_pip.y and
        middle_tip.y > middle_pip.y and
        ring_tip.y > ring_pip.y and
        pinky_tip.y > pinky_pip.y and
        thumb_tip.y > thumb_ip.y):
        return "A"
    
    # FLAT HAND (B)
    if (index_tip.y < index_pip.y and
        middle_tip.y < middle_pip.y and
        ring_tip.y < ring_pip.y and
        pinky_tip.y < pinky_pip.y and
        thumb_tip.x < thumb_ip.x):
        return "B"
    
    # C SHAPE
    if (middle_tip.y > middle_pip.y - 0.05 and
        index_tip.y > index_pip.y - 0.05 and
        ring_tip.y > ring_pip.y - 0.05 and
        pinky_tip.y > pinky_pip.y - 0.05 and
        thumb_tip.y <= thumb_ip.y):
        return "C"
    
    # POINTING (D)
    if (index_tip.y < index_pip.y and
        middle_tip.y > middle_pip.y and
        ring_tip.y > ring_pip.y and
        pinky_tip.y > pinky_pip.y):
        return "D"
    
    # OK SIGN (F)
    thumb_index_distance = abs(thumb_tip.x - index_tip.x) + abs(thumb_tip.y - index_tip.y)
    if thumb_index_distance < 0.1:
        return "F"
    
    # PEACE (V)
    if (index_tip.y < index_pip.y and
        middle_tip.y < middle_pip.y and
        ring_tip.y > ring_pip.y and
        pinky_tip.y > pinky_pip.y):
        return "V"
    
    return "?"

cap = cv2.VideoCapture(0)

print("=" * 60)
print("ASL GESTURE TESTER")
print("=" * 60)
print("\nMake these gestures and check if detected correctly:")
print("1. ✊ FIST → Should show: A")
print("2. 🖐️ FLAT HAND → Should show: B")
print("3. 🤏 OK SIGN → Should show: F")
print("4. ✌️ PEACE → Should show: V")
print("5. 👆 POINTING → Should show: D")
print("6. Press 'Q' to quit")
print("=" * 60)

while True:
    success, frame = cap.read()
    if not success:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    detected = "Show Hand"
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
            
            landmarks = hand_landmarks.landmark
            detected = detect_asl_letter(landmarks)
    
    # Display result
    cv2.putText(frame, f'Detected: {detected}', (20, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    
    cv2.putText(frame, "Press Q to quit", (20, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('ASL Gesture Tester', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nTest completed!")