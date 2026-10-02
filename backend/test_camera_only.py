import cv2
import mediapipe as mp
import numpy as np

print("🎬 Camera & Hand Detection Test")
print("="*50)

# Try different camera indices
for i in range(4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Camera {i} found!")
        break
    else:
        print(f"❌ Camera {i} not found")

if not cap.isOpened():
    print("❌ No camera found!")
    exit()

print("\n🎯 Press 'q' to quit, 'h' to show/hide hand landmarks")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

show_landmarks = True
hand_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame")
        break
    
    # Flip frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)
    
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
    
    # Process with MediaPipe
    results = hands.process(rgb_frame)
    
    # Convert back to BGR
    rgb_frame.flags.writeable = True
    output_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    
    hand_detected = False
    
    if results.multi_hand_landmarks and show_landmarks:
        hand_detected = True
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks
            mp.solutions.drawing_utils.draw_landmarks(
                output_frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style()
            )
            
            # Get bounding box
            h, w, _ = output_frame.shape
            x_coords = [lm.x for lm in hand_landmarks.landmark]
            y_coords = [lm.y for lm in hand_landmarks.landmark]
            
            x_min = int(min(x_coords) * w)
            y_min = int(min(y_coords) * h)
            x_max = int(max(x_coords) * w)
            y_max = int(max(y_coords) * h)
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x_min-20, y_min-20), 
                         (x_max+20, y_max+20), (0, 255, 0), 2)
            
            # Display "Hand Detected"
            cv2.putText(output_frame, "HAND DETECTED", (x_min, y_min-30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Display status
    status_text = "✅ Hand Detected" if hand_detected else "❌ No Hand Detected"
    status_color = (0, 255, 0) if hand_detected else (0, 0, 255)
    
    cv2.putText(output_frame, status_text, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
    # Display instructions
    cv2.putText(output_frame, "Press 'h': Toggle landmarks", (10, 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(output_frame, "Press 'q': Quit", (10, 100),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('Hand Detection Test', output_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('h'):
        show_landmarks = not show_landmarks

cap.release()
cv2.destroyAllWindows()
print("\n✅ Test completed!")