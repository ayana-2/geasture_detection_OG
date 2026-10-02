import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
import os
import time
from datetime import datetime

class GestureDataCollector:
    def __init__(self, output_dir='dataset/raw'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Data collection variables
        self.collecting = False
        self.current_gesture = None
        self.samples_collected = 0
        self.max_samples = 100  # Samples per gesture
        self.data_buffer = []
        
    def start_collection(self, gesture_label):
        """Start collecting data for a specific gesture"""
        self.collecting = True
        self.current_gesture = gesture_label
        self.samples_collected = 0
        self.data_buffer = []
        
        print(f"Started collecting data for gesture: {gesture_label}")
        print(f"Show the gesture to the camera. Press 'q' to stop.")
        
    def stop_collection(self):
        """Stop data collection and save collected data"""
        if not self.collecting:
            return
        
        self.collecting = False
        
        if len(self.data_buffer) > 0:
            # Save data to CSV
            filename = f"{self.current_gesture}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            df = pd.DataFrame(self.data_buffer)
            df.to_csv(filepath, index=False)
            
            print(f"Saved {len(self.data_buffer)} samples to {filepath}")
        
        self.current_gesture = None
        self.data_buffer = []
        
    def process_frame(self, frame):
        """Process a frame and collect hand landmark data"""
        if not self.collecting:
            return frame
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Process with MediaPipe
        results = self.hands.process(rgb_frame)
        
        # Convert back to BGR for OpenCV
        rgb_frame.flags.writeable = True
        output_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks and self.samples_collected < self.max_samples:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract features
            features = self.extract_features(hand_landmarks)
            
            # Add label (numeric)
            label = ord(self.current_gesture) - ord('A')  # Convert A-Z to 0-25
            features.append(label)
            
            # Add to buffer
            self.data_buffer.append(features)
            self.samples_collected += 1
            
            # Display collection status
            cv2.putText(output_frame, 
                       f"Collecting: {self.current_gesture} ({self.samples_collected}/{self.max_samples})",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Draw landmarks
            mp.solutions.drawing_utils.draw_landmarks(
                output_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
        
        elif self.samples_collected >= self.max_samples:
            cv2.putText(output_frame, 
                       f"Collection complete for {self.current_gesture}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return output_frame
    
    def extract_features(self, hand_landmarks):
        """Extract features from hand landmarks"""
        features = []
        
        # Get all 21 landmarks (x, y, z coordinates)
        for landmark in hand_landmarks.landmark:
            features.extend([landmark.x, landmark.y, landmark.z])
        
        # Calculate distances between key points
        key_points = [0, 4, 8, 12, 16, 20]  # Wrist and finger tips
        
        for i in range(len(key_points)):
            for j in range(i+1, len(key_points)):
                point_i = hand_landmarks.landmark[key_points[i]]
                point_j = hand_landmarks.landmark[key_points[j]]
                distance = np.sqrt(
                    (point_i.x - point_j.x)**2 +
                    (point_i.y - point_j.y)**2 +
                    (point_i.z - point_j.z)**2
                )
                features.append(distance)
        
        return features

def collect_gesture_data():
    """Main function for data collection"""
    collector = GestureDataCollector()
    
    # Start camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    current_gesture = 'A'
    collecting = False
    
    print("Gesture Data Collection Tool")
    print("============================")
    print("Press 's' to start/stop collection for current gesture")
    print("Press 'n' for next gesture")
    print("Press 'p' for previous gesture")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if collecting:
            frame = collector.process_frame(frame)
        else:
            cv2.putText(frame, 
                       f"Current Gesture: {current_gesture}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, 
                       "Press 's' to start collection",
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow('Gesture Data Collection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            if not collecting:
                collector.start_collection(current_gesture)
                collecting = True
            else:
                collector.stop_collection()
                collecting = False
        elif key == ord('n'):
            if not collecting:
                current_gesture = chr(min(ord(current_gesture) + 1, ord('Z')))
        elif key == ord('p'):
            if not collecting:
                current_gesture = chr(max(ord(current_gesture) - 1, ord('A')))
    
    cap.release()
    cv2.destroyAllWindows()
    
    if collecting:
        collector.stop_collection()

if __name__ == '__main__':
    collect_gesture_data()