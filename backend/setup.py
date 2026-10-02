import os
import subprocess
import sys

def setup_project():
    print("Setting up Sign Language Converter Project...")
    
    # Create directory structure
    directories = [
        'backend',
        'backend/models',
        'backend/templates', 
        'backend/utils',
        'dataset/raw',
        'dataset/processed',
        'training'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created: {directory}")
    
    # Create requirements.txt
    requirements = """flask==2.3.3
flask-cors==4.0.0
flask-socketio==5.3.6
opencv-python==4.8.1.78
numpy==1.24.3
mediapipe==0.10.8
scikit-learn==1.3.0
joblib==1.3.2
pandas==2.0.3
werkzeug==3.0.1
python-socketio==5.10.0
eventlet==0.33.3
"""
    
    with open('backend/requirements.txt', 'w') as f:
        f.write(requirements)
    print("Created: backend/requirements.txt")
    
    # Create labels.json
    labels = {
        "0": "A", "1": "B", "2": "C", "3": "D", "4": "E",
        "5": "F", "6": "G", "7": "H", "8": "I", "9": "J",
        "10": "K", "11": "L", "12": "M", "13": "N", "14": "O",
        "15": "P", "16": "Q", "17": "R", "18": "S", "19": "T",
        "20": "U", "21": "V", "22": "W", "23": "X", "24": "Y", "25": "Z"
    }
    
    with open('dataset/labels.json', 'w') as f:
        import json
        json.dump(labels, f, indent=2)
    print("Created: dataset/labels.json")
    
    # Install packages
    print("\nInstalling Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("Packages installed successfully!")
    except subprocess.CalledProcessError:
        print("Error installing packages. Trying manual installation...")
        packages = [
            "flask==2.3.3", "flask-cors==4.0.0", "flask-socketio==5.3.6",
            "opencv-python==4.8.1.78", "numpy==1.24.3", "mediapipe==0.10.8",
            "scikit-learn==1.3.0", "joblib==1.3.2", "pandas==2.0.3",
            "werkzeug==3.0.1", "python-socketio==5.10.0", "eventlet==0.33.3"
        ]
        
        for package in packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Installed: {package}")
            except:
                print(f"Failed to install: {package}")
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Copy the app.py code to backend/app.py")
    print("2. Copy the index.html code to backend/templates/index.html")
    print("3. Copy the utility files to backend/utils/")
    print("4. Run: cd backend && python app.py")
    print("5. Open: http://localhost:5000")

if __name__ == "__main__":
    setup_project()