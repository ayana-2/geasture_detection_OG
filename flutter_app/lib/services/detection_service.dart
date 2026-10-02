abstract class DetectionService {
  Future<void> initialize();
  Future<Map<String, dynamic>> detectGesture(List<int> imageBytes);
  Future<void> dispose();
}

class TFLiteDetectionService implements DetectionService {
  bool _isInitialized = false;

  @override
  Future<void> initialize() async {
    // Initialize TFLite model
    // This is a placeholder - actual implementation would load the .tflite model
    await Future.delayed(Duration(seconds: 1));
    _isInitialized = true;
    print('TFLite service initialized');
  }

  @override
  Future<Map<String, dynamic>> detectGesture(List<int> imageBytes) async {
    if (!_isInitialized) {
      throw Exception('Service not initialized');
    }

    // Simulate detection (replace with actual TFLite inference)
    await Future.delayed(Duration(milliseconds: 100));
    
    final gestures = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
    final randomIndex = DateTime.now().millisecond % gestures.length;
    
    return {
      'gesture': gestures[randomIndex],
      'confidence': 0.7 + (DateTime.now().millisecond % 300) / 1000,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  @override
  Future<void> dispose() async {
    _isInitialized = false;
    print('TFLite service disposed');
  }
}