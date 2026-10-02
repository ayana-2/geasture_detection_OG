import 'package:flutter/material.dart';

class LiveCameraScreen extends StatelessWidget {
  const LiveCameraScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Live Detection")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "Live Sign Language Detection",
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: 640,
              height: 480,
              child: HtmlElementView(viewType: 'camera-stream'),
            ),
          ],
        ),
      ),
    );
  }
}
