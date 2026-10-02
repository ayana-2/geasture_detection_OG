import numpy as np
import pickle
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class GestureClassifier:
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = StandardScaler()
        self.labels = {}
        
        if model_path:
            self.load_model(model_path)
        else:
            # Create a simple model if none exists
            self.model = make_pipeline(
                StandardScaler(),
                RandomForestClassifier(n_estimators=100, random_state=42)
            )
    
    def load_model(self, model_path):
        """Load pre-trained model"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {model_path}")
        except FileNotFoundError:
            print("Model file not found. Creating new model.")
            self.model = make_pipeline(
                StandardScaler(),
                RandomForestClassifier(n_estimators=100, random_state=42)
            )
    
    def save_model(self, model_path):
        """Save model to file"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {model_path}")
    
    def load_labels(self, labels_path):
        """Load gesture labels"""
        try:
            with open(labels_path, 'r') as f:
                self.labels = json.load(f)
        except FileNotFoundError:
            print("Labels file not found")
    
    def extract_features(self, landmarks):
        """Extract features from hand landmarks"""
        features = []
        
        # Basic landmark coordinates
        for lm in landmarks:
            features.extend([lm[0], lm[1], lm[2]])
        
        # Distances between key points
        key_points = [0, 4, 8, 12, 16, 20]  # Wrist and fingertips
        
        for i in range(len(key_points)):
            for j in range(i+1, len(key_points)):
                # Calculate Euclidean distance
                dist = np.sqrt(
                    (landmarks[key_points[i]][0] - landmarks[key_points[j]][0])**2 +
                    (landmarks[key_points[i]][1] - landmarks[key_points[j]][1])**2 +
                    (landmarks[key_points[i]][2] - landmarks[key_points[j]][2])**2
                )
                features.append(dist)
        
        # Angles between fingers
        # (This is simplified - actual implementation would be more complex)
        
        return np.array(features)
    
    def train(self, X, y):
        """Train the classifier"""
        self.model.fit(X, y)
        print("Model training completed")
    
    def predict(self, landmarks):
        """Predict gesture from landmarks"""
        if self.model is None:
            return "UNKNOWN", 0.0
        
        features = self.extract_features(landmarks).reshape(1, -1)
        
        try:
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            confidence = np.max(probabilities)
            
            # Convert numeric label to string if labels available
            if self.labels and str(prediction) in self.labels:
                gesture = self.labels[str(prediction)]
            else:
                gesture = f"GESTURE_{prediction}"
            
            return gesture, confidence
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return "ERROR", 0.0
    
    def predict_batch(self, landmarks_list):
        """Predict multiple gestures"""
        predictions = []
        for landmarks in landmarks_list:
            gesture, confidence = self.predict(landmarks)
            predictions.append((gesture, confidence))
        return predictions