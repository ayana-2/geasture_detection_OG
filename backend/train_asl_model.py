"""
Train a simple ASL alphabet classifier and save as asl_model.pkl
Run this script once to generate the model file.
"""

import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

np.random.seed(42)
num_samples_per_letter = 200
letters = [chr(i) for i in range(65, 91)]  # A-Z

X = []  # features
y_labels = []  # labels

for letter_idx, letter in enumerate(letters):
    for _ in range(num_samples_per_letter):
        landmarks = []
        wrist = np.array([0.5, 0.5])
        # Simplified finger y positions (just for demonstration)
        if letter == 'A':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'B':
            fingers_y = [0.5, 0.3, 0.3, 0.3, 0.3]
        elif letter == 'C':
            fingers_y = [0.4, 0.35, 0.4, 0.45, 0.5]
        elif letter == 'D':
            fingers_y = [0.5, 0.3, 0.5, 0.5, 0.5]
        elif letter == 'E':
            fingers_y = [0.5, 0.45, 0.45, 0.45, 0.45]
        elif letter == 'F':
            fingers_y = [0.3, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'G':
            fingers_y = [0.3, 0.3, 0.5, 0.5, 0.5]
        elif letter == 'H':
            fingers_y = [0.5, 0.3, 0.3, 0.5, 0.5]
        elif letter == 'I':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.3]
        elif letter == 'J':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.3]
        elif letter == 'K':
            fingers_y = [0.4, 0.3, 0.3, 0.5, 0.5]
        elif letter == 'L':
            fingers_y = [0.3, 0.3, 0.5, 0.5, 0.5]
        elif letter == 'M':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'N':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'O':
            fingers_y = [0.4, 0.4, 0.5, 0.5, 0.5]
        elif letter == 'P':
            fingers_y = [0.4, 0.6, 0.5, 0.5, 0.5]
        elif letter == 'Q':
            fingers_y = [0.6, 0.3, 0.5, 0.5, 0.5]
        elif letter == 'R':
            fingers_y = [0.5, 0.3, 0.3, 0.5, 0.5]
        elif letter == 'S':
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'T':
            fingers_y = [0.4, 0.5, 0.5, 0.5, 0.5]
        elif letter == 'U':
            fingers_y = [0.5, 0.3, 0.3, 0.5, 0.5]
        elif letter == 'V':
            fingers_y = [0.5, 0.3, 0.3, 0.5, 0.5]
        elif letter == 'W':
            fingers_y = [0.5, 0.3, 0.3, 0.3, 0.5]
        elif letter == 'X':
            fingers_y = [0.5, 0.4, 0.5, 0.5, 0.5]
        elif letter == 'Y':
            fingers_y = [0.3, 0.5, 0.5, 0.5, 0.3]
        elif letter == 'Z':
            fingers_y = [0.5, 0.3, 0.5, 0.5, 0.5]
        else:
            fingers_y = [0.5, 0.5, 0.5, 0.5, 0.5]

        # Generate 21 landmarks with randomness
        for i in range(21):
            if i == 0:  # wrist
                x = wrist[0] + np.random.uniform(-0.02, 0.02)
                y_coord = wrist[1] + np.random.uniform(-0.02, 0.02)
            elif i in [1,2,3,4,5]:  # thumb
                y_coord = fingers_y[0] + np.random.uniform(-0.02, 0.02)
                x = wrist[0] - 0.1 + np.random.uniform(-0.02, 0.02)
            elif i in [6,7,8]:  # index
                y_coord = fingers_y[1] + np.random.uniform(-0.02, 0.02)
                x = wrist[0] + 0.1 + np.random.uniform(-0.02, 0.02)
            elif i in [9,10,11]: # middle
                y_coord = fingers_y[2] + np.random.uniform(-0.02, 0.02)
                x = wrist[0] + 0.15 + np.random.uniform(-0.02, 0.02)
            elif i in [12,13,14]: # ring
                y_coord = fingers_y[3] + np.random.uniform(-0.02, 0.02)
                x = wrist[0] + 0.2 + np.random.uniform(-0.02, 0.02)
            elif i in [15,16,17,18,19,20]: # pinky
                y_coord = fingers_y[4] + np.random.uniform(-0.02, 0.02)
                x = wrist[0] + 0.25 + np.random.uniform(-0.02, 0.02)
            else:
                x = wrist[0] + np.random.uniform(-0.1, 0.1)
                y_coord = wrist[1] + np.random.uniform(-0.1, 0.1)

            landmarks.extend([x, y_coord])

        X.append(landmarks)
        y_labels.append(letter_idx)

X = np.array(X)
y_labels = np.array(y_labels)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_labels, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model accuracy on synthetic data: {acc:.2f}")

# Save model
with open('asl_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model saved as asl_model.pkl")