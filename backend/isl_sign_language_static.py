import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

def distance(a, b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    letter = " "

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark

            # Finger open detection
            fingers = []
            fingers.append(1 if lm[8].y < lm[6].y else 0)   # Index
            fingers.append(1 if lm[12].y < lm[10].y else 0) # Middle
            fingers.append(1 if lm[16].y < lm[14].y else 0) # Ring
            fingers.append(1 if lm[20].y < lm[18].y else 0) # Pinky

            thumb_open = lm[4].x < lm[3].x  # Right hand thumb

            # Distances
            thumb_index_dist = distance(lm[4], lm[8])

            # ---------------- ISL LETTER LOGIC ----------------

            # A – fist, thumb outside
            if fingers == [0,0,0,0] and thumb_open:
                letter = "A"

            # B – all fingers open, thumb folded
            elif fingers == [1,1,1,1] and not thumb_open:
                letter = "B"

            # C – curved hand
            elif thumb_index_dist < 0.15 and fingers == [1,1,1,1]:
                letter = "C"

            # D – index up, others closed
            elif fingers == [1,0,0,0]:
                letter = "D"

            # E – all fingers bent
            elif fingers == [0,0,0,0] and not thumb_open:
                letter = "E"

            # F – OK sign
            elif thumb_index_dist < 0.05 and fingers == [0,1,1,1]:
                letter = "F"

            # H – index + middle
            elif fingers == [1,1,0,0]:
                letter = "H"

            # I – pinky up
            elif fingers == [0,0,0,1]:
                letter = "I"

            # L – thumb + index
            elif thumb_open and fingers == [1,0,0,0]:
                letter = "L"

            # U – index + middle together
            elif fingers == [1,1,0,0] and not thumb_open:
                letter = "U"

            # V – index + middle apart
            elif fingers == [1,1,0,0] and thumb_open:
                letter = "V"

            # W – index, middle, ring
            elif fingers == [1,1,1,0]:
                letter = "W"

            # Y – thumb + pinky
            elif thumb_open and fingers == [0,0,0,1]:
                letter = "Y"

            else:
                letter = "Unknown"

    cv2.putText(frame, f"Letter: {letter}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0,255,0), 3)

    cv2.imshow("ISL Sign Language Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
