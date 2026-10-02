import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os

print("🤖 Creating ASL A-Z Model...")

# Create synthetic dataset for A-Z
def create_asl_dataset():
    """Create synthetic ASL dataset for letters A-Z"""
    data = []
    letters = [chr(i) for i in range(65, 91)]  # A to Z
    
    for letter_idx, letter in enumerate(letters):
        print(f"Generating data for letter: {letter}")
        
        for sample in range(100):  # 100 samples per letter
            # Base features (42 = 21 landmarks × 2)
            features = np.random.rand(42)
            
            # Add letter-specific patterns
            # Wrist position
            features[0] = 0.5 + np.random.normal(0, 0.05)  # x
            features[1] = 0.5 + np.random.normal(0, 0.05)  # y
            
            # Letter-specific adjustments
            if letter == 'A':  # Fist
                features[4*2+1] = 0.3  # Thumb tip low
            elif letter == 'B':  # All fingers up
                for i in range(5, 21, 4):
                    features[i*2+1] = 0.2  # Finger tips up
            elif letter == 'C':  # Curved
                for i in range(5, 21, 4):
                    features[i*2] = 0.4 + (i//4)*0.05  # Spread
            # Add more letter patterns as needed...
            
            data.append([letter] + list(features))
    
    # Create DataFrame
    columns = ['letter'] + [f'f{i}' for i in range(42)]
    df = pd.DataFrame(data, columns=columns)
    
    print(f"\n📊 Dataset created:")
    print(f"   Total samples: {len(df)}")
    print(f"   Letters: {sorted(df['letter'].unique())}")
    print(f"   Samples per letter: {df['letter'].value_counts().min()}")
    
    return df

# Create and train model
print("📊 Creating dataset...")
df = create_asl_dataset()

# Split data
X = df.drop('letter', axis=1).values
y = df['letter'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n🎯 Training model...")
print(f"   Training samples: {len(X_train)}")
print(f"   Testing samples: {len(X_test)}")

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=25,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"\n✅ Model trained successfully!")
print(f"📈 Accuracy: {accuracy:.4f}")

# Save model
with open('asl_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"\n💾 Model saved as: asl_model.pkl")
print(f"🔤 Model supports {len(model.classes_)} letters:")
print(f"   {''.join(sorted(model.classes_))}")

# Test predictions
print(f"\n🧪 Testing predictions...")
test_sample = X_test[0].reshape(1, -1)
prediction = model.predict(test_sample)[0]
print(f"   Test prediction: {prediction}")
print(f"   Actual: {y_test[0]}")

print("\n" + "="*60)
print("🎉 ASL Model ready! Use with Flask app.")
print("="*60)