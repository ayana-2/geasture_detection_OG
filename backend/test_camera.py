import cv2

print("Trying to open camera with index 0...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if cap.isOpened():
    print("Camera opened. Reading frame...")
    ret, frame = cap.read()
    if ret:
        print("Frame read successfully! Showing image...")
        cv2.imshow("Camera Test - Press any key", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Could not read frame from camera.")
else:
    print("❌ Could not open camera with index 0.")
cap.release()

# Try index 1 if index 0 fails
print("\nTrying index 1...")
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if cap.isOpened():
    print("Camera 1 opened.")
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Camera 1 Test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Cannot read from camera 1.")
else:
    print("❌ Camera 1 not opened.")
cap.release()