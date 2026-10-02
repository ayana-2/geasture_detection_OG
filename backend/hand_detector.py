import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time

class HandDetector:
    def __init__(self):
        print("🤖 Initializing Hand Detection System...")
        
        # Initialize MediaPipe with better settings
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,  # Higher confidence
            min_tracking_confidence=0.7
        )
        
        # Camera
        self.cap = None
        self.camera_index = 0
        self.camera_initialized = False
        
        # Detection
        self.current_letter = ""
        self.detection_history = deque(maxlen=15)  # Larger buffer
        self.last_detection_time = 0
        
        # Initialize camera
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize camera with retry logic"""
        max_retries = 3
        
        for i in range(max_retries):
            try:
                print(f"📷 Attempting to initialize camera (Attempt {i+1}/{max_retries})...")
                
                # Try different camera indices
                for cam_idx in range(0, 3):  # Try cameras 0, 1, 2
                    self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
                    
                    # Set camera properties
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Test if camera opens
                    if self.cap.isOpened():
                        ret, test_frame = self.cap.read()
                        if ret and test_frame is not None:
                            self.camera_index = cam_idx
                            self.camera_initialized = True
                            print(f"✅ Camera {cam_idx} initialized successfully!")
                            print(f"   Resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
                            return True
                        else:
                            self.cap.release()
                    else:
                        self.cap.release()
                
                print(f"❌ Camera initialization failed on attempt {i+1}")
                time.sleep(1)  # Wait before retry
                
            except Exception as e:
                print(f"⚠️ Camera error: {str(e)}")
                if self.cap:
                    self.cap.release()
        
        print("❌ Failed to initialize camera after all attempts")
        return False
    
    def detect_letter(self, landmarks):
        """Improved letter detection"""
        if not landmarks:
            return ""
        
        # Get key points
        tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        pips = [3, 6, 10, 14, 18]   # Corresponding joints
        
        # Count extended fingers
        fingers = 0
        finger_states = []
        
        for tip_idx, pip_idx in zip(tips, pips):
            if tip_idx == 4:  # Thumb (different logic)
                extended = landmarks[tip_idx].x < landmarks[pip_idx].x - 0.02
            else:  # Other fingers
                extended = landmarks[tip_idx].y < landmarks[pip_idx].y - 0.02
            
            finger_states.append(1 if extended else 0)
            if extended:
                fingers += 1
        
        # Map to letters A-F (simple for reliability)
        letter_map = {
            0: "A",  # Fist
            1: "B",  # One finger
            2: "C",  # Two fingers
            3: "D",  # Three fingers
            4: "E",  # Four fingers
            5: "F"   # All fingers
        }
        
        return letter_map.get(fingers, "A")
    
    def get_current_letter(self):
        return self.current_letter
    
    def camera_status(self):
        if self.cap and self.cap.isOpened():
            return "active"
        elif self.camera_initialized:
            return "initialized"
        else:
            return "inactive"
    
    def generate_frames(self):
        """Generate video frames with enhanced display"""
        if not self.camera_initialized or not self.cap:
            print("⚠️ Camera not available, attempting re-initialization...")
            self.initialize_camera()
            if not self.camera_initialized:
                # Generate error frame
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "CAMERA UNAVAILABLE", (120, 200),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(error_frame, "Check camera connection", (100, 250),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                while True:
                    ret, buffer = cv2.imencode('.jpg', error_frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        print("🎬 Starting video stream...")
        
        while True:
            try:
                # Read frame
                success, frame = self.cap.read()
                
                if not success:
                    print("⚠️ Failed to read frame, reinitializing camera...")
                    self.cap.release()
                    self.initialize_camera()
                    time.sleep(0.1)
                    continue
                
                # Flip and process
                frame = cv2.flip(frame, 1)
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.hands.process(rgb_frame)
                
                detected_letter = ""
                hand_present = False
                
                if results.multi_hand_landmarks:
                    hand_present = True
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks with custom style
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing.DrawingSpec(color=(57, 255, 20), thickness=3, circle_radius=4),
                            self.mp_drawing.DrawingSpec(color=(255, 110, 20), thickness=3)
                        )
                        
                        # Detect letter
                        detected_letter = self.detect_letter(hand_landmarks.landmark)
                        
                        if detected_letter:
                            self.detection_history.append(detected_letter)
                            
                            # Get most common letter
                            if self.detection_history:
                                counts = {}
                                for letter in self.detection_history:
                                    counts[letter] = counts.get(letter, 0) + 1
                                detected_letter = max(counts, key=counts.get)
                
                # Update current letter
                self.current_letter = detected_letter if detected_letter else ""
                
                # ====================================
                # MODERN DISPLAY - CLEAN & PROFESSIONAL
                # ====================================
                
                # Add semi-transparent overlay for text
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), (20, 20, 20), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                if hand_present and self.current_letter:
                    # Status indicator (green circle)
                    cv2.circle(frame, (40, 50), 15, (57, 255, 20), -1)
                    cv2.circle(frame, (40, 50), 18, (57, 255, 20), 2)
                    
                    # Status text
                    cv2.putText(frame, "HAND DETECTED", (70, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (220, 220, 220), 2)
                    
                    # Detected letter
                    cv2.putText(frame, f"LETTER: {self.current_letter}", (70, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.1, (57, 255, 20), 3)
                    
                    # Large letter display (centered)
                    text_size = cv2.getTextSize(self.current_letter, cv2.FONT_HERSHEY_TRIPLEX, 8, 10)[0]
                    text_x = (frame.shape[1] - text_size[0]) // 2
                    text_y = (frame.shape[0] + text_size[1]) // 2
                    
                    # Add glow effect for letter
                    for i in range(3):
                        cv2.putText(frame, self.current_letter,
                                   (text_x - i, text_y - i),
                                   cv2.FONT_HERSHEY_TRIPLEX, 8,
                                   (20, 20, 60), 10)
                    
                    cv2.putText(frame, self.current_letter,
                               (text_x, text_y),
                               cv2.FONT_HERSHEY_TRIPLEX, 8,
                               (57, 255, 20), 10)
                
                else:
                    # No hand detected
                    cv2.circle(frame, (40, 50), 15, (100, 100, 255), -1)
                    cv2.circle(frame, (40, 50), 18, (100, 100, 255), 2)
                    
                    # Instruction text
                    text = "SHOW HAND TO CAMERA"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
                    text_x = (frame.shape[1] - text_size[0]) // 2
                    
                    cv2.putText(frame, text, (text_x, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (100, 100, 255), 3)
                
                # Bottom status bar
                cv2.rectangle(frame, (0, frame.shape[0] - 40),
                            (frame.shape[1], frame.shape[0]), (20, 20, 20), -1)
                
                status_text = f"ASL Translator • Camera: {self.camera_index} • FPS: 30"
                cv2.putText(frame, status_text, (20, frame.shape[0] - 12),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
            except Exception as e:
                print(f"❌ Frame generation error: {str(e)}")
                time.sleep(0.1)
                continue
    
    def release_camera(self):
        """Cleanly release camera resources"""
        print("🔴 Releasing camera resources...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.camera_initialized = False
        print("✅ Camera released")