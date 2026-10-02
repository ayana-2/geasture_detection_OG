import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera open aayilla")
    exit()

print("✅ Camera started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    letter = ""

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            lm = hand_landmarks.landmark

            # Finger tips & PIP joints
            tips = [8, 12, 16, 20]
            pips = [6, 10, 14, 18]

            fingers = []

            for tip, pip in zip(tips, pips):
                if lm[tip].y < lm[pip].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # Alphabet logic
            if fingers == [0, 0, 0, 0]:
                letter = "A"
            elif fingers == [1, 0, 0, 0]:
                letter = "D"
            elif fingers == [1, 1, 1, 1]:
                letter = "E"
            else:
                letter = "Unknown"

    # Display result
    cv2.putText(
        frame,
        f"Letter: {letter}",
        (30, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 0),
        3
    )

    cv2.imshow("Sign Language Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
