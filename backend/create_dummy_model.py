import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import json
import os

def create_dummy_model():
    """ഡമ്മി മോഡൽ സൃഷ്ടിക്കുക - ഉടൻ പ്രവർത്തനം തുടങ്ങാൻ"""
    
    # Create models directory if not exists
    os.makedirs('models', exist_ok=True)
    
    # Create dataset directory if not exists
    os.makedirs('dataset', exist_ok=True)
    
    # Create dummy labels (A-Z)
    labels = {str(i): chr(65 + i) for i in range(26)}  # A-Z
    labels.update({str(26): "Hello", str(27): "Thank You", str(28): "Yes", str(29): "No"})
    
    with open('dataset/labels.json', 'w') as f:
        json.dump(labels, f, indent=2)
    
    print("✅ Created labels.json")
    
    # Create dummy training data
    # Each hand has 21 landmarks * 3 coordinates = 63 features
    # Plus 15 distances between key points = 78 total features
    
    n_samples = 1000
    n_features = 78  # 21*3 + 15
    
    # Generate random data (simulating hand landmarks)
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 30, n_samples)  # 30 classes (A-Z + 4 gestures)
    
    # Create and train a simple model
    model = make_pipeline(
        StandardScaler(),
        RandomForestClassifier(n_estimators=50, random_state=42)
    )
    
    model.fit(X, y)
    
    # Save the model
    with open('models/classifier_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save model metadata
    metadata = {
        'accuracy': 0.95,
        'model_type': 'RandomForest',
        'num_classes': 30,
        'features': n_features,
        'is_dummy': True,
        'description': 'Dummy model for initial testing'
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Created dummy classifier_model.pkl")
    print("✅ Model saved in models/ directory")
    print("\n⚠️  Note: This is a DUMMY model for testing.")
    print("   For real sign language detection, you need to:")
    print("   1. Collect real gesture data")
    print("   2. Train the model with your data")
    print("   3. Replace this dummy model")
    
    return True

if __name__ == "__main__":
    create_dummy_model()