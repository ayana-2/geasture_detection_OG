import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score

# Load all data
X, y = [], []
data_dir = 'data'

for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        gesture = file.replace('.csv', '')
        df = pd.read_csv(os.path.join(data_dir, file), header=None)
        X.extend(df.iloc[:, 1:].values)
        y.extend([gesture] * len(df))
        print(f"Loaded {len(df)} samples for {gesture}")

X = np.array(X)
y = np.array(y)
print(f"\nTotal samples: {len(X)}")

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest
print("\n🚀 Training Random Forest...")
model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Test accuracy: {accuracy*100:.2f}%")

# Save model and preprocessors
joblib.dump(model, 'asl_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')
print("\n💾 Model saved as asl_model.pkl, scaler.pkl, label_encoder.pkl")