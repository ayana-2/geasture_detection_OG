import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_confidence=0.7, tracking_confidence=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        
        # Hand landmarks indices
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb to Pinky tip
        
    def find_hands(self, img, draw=True):
        """Find hands in the image"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
                )
        
        return img
    
    def find_position(self, img, hand_number=0, draw=True):
        """Find hand landmark positions"""
        landmarks_list = []
        
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_number]
            
            for id, landmark in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                landmarks_list.append([id, cx, cy])
                
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
            
            # Draw bounding box
            if draw and landmarks_list:
                x_min = min([lm[1] for lm in landmarks_list])
                x_max = max([lm[1] for lm in landmarks_list])
                y_min = min([lm[2] for lm in landmarks_list])
                y_max = max([lm[2] for lm in landmarks_list])
                
                cv2.rectangle(img, (x_min-20, y_min-20), 
                            (x_max+20, y_max+20), (0, 255, 0), 2)
        
        return landmarks_list
    
    def fingers_up(self, landmarks):
        """Check which fingers are up"""
        fingers = []
        
        # Thumb
        if landmarks[self.tip_ids[0]][1] < landmarks[self.tip_ids[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other fingers
        for id in range(1, 5):
            if landmarks[self.tip_ids[id]][2] < landmarks[self.tip_ids[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def get_hand_type(self, img, hand_number=0):
        """Determine if hand is left or right"""
        if self.results.multi_handedness:
            hand_type = self.results.multi_handedness[hand_number].classification[0].label
            return hand_type
        return "Unknown"
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    
    def get_landmark_coordinates(self, landmarks_list):
        """Convert landmarks to numpy array"""
        coords = []
        for lm in landmarks_list:
            coords.extend([lm[1], lm[2]])  # Only x, y coordinates
        return np.array(coords)