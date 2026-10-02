import 'package:flutter/material.dart';

// This is a placeholder widget since the real camera package
// doesn't fully work on web. It allows your app to run and test UI.
class CameraWidget extends StatelessWidget {
  final Function(String gesture, double confidence) onGestureDetected;

  CameraWidget({required this.onGestureDetected});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black87,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.videocam_off, size: 80, color: Colors.white54),
            SizedBox(height: 20),
            Text(
              'Camera Preview',
              style: TextStyle(color: Colors.white, fontSize: 24),
            ),
            SizedBox(height: 10),
            Text(
              'On mobile, this would show the live camera feed.',
              style: TextStyle(color: Colors.white70),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                // Simulate a detection for testing
                onGestureDetected('A', 0.85);
              },
              child: Text('Simulate "A" Detection'),
            ),
          ],
        ),
      ),
    );
  }
}