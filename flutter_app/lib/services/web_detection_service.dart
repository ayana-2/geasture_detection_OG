// File: lib/services/web_detection_service.dart
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'detection_service.dart';  // Import the abstract class

/// A service specifically for web platform detection
/// Implements the DetectionService interface
class WebDetectionService implements DetectionService {
  final String _serverUrl;
  
  WebDetectionService(this._serverUrl);
  
  /// Initialize connection to the backend
  @override
  Future<void> initialize() async {
    try {
      final response = await http.get(Uri.parse('$_serverUrl/health'));
      if (response.statusCode == 200) {
        print('✅ Web detection service initialized');
      } else {
        print('❌ Server returned status: ${response.statusCode}');
        throw Exception('Server returned status: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Failed to connect to server: $e');
      throw Exception('Failed to connect to server: $e');
    }
  }
  
  /// Detect gesture from image bytes (web-compatible)
  @override
  Future<Map<String, dynamic>> detectGesture(List<int> imageBytes) async {
    try {
      final uri = Uri.parse('$_serverUrl/api/detect');
      
      // Convert bytes to base64 for web transmission
      final base64Image = base64Encode(imageBytes);
      
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'image': 'data:image/jpeg;base64,$base64Image'}),
      );
      
      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        return responseData;
      } else {
        throw Exception('Detection failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Detection error: $e');
    }
  }
  
  /// Alternative: multipart form data upload (not required by interface)
  Future<Map<String, dynamic>> detectGestureMultipart(Uint8List imageBytes) async {
    try {
      final uri = Uri.parse('$_serverUrl/api/detect');
      final request = http.MultipartRequest('POST', uri)
        ..files.add(http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'frame.jpg',
        ));
      
      final response = await request.send();
      
      if (response.statusCode == 200) {
        final responseData = await response.stream.bytesToString();
        return jsonDecode(responseData);
      } else {
        throw Exception('Detection failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Multipart detection error: $e');
    }
  }
  
  /// Get available gestures from server (not required by interface, but useful)
  Future<List<String>> getAvailableGestures() async {
    try {
      final response = await http.get(Uri.parse('$_serverUrl/api/letters'));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final letters = data['letters'] as List<dynamic>;
        return letters.map((l) => l.toString()).toList();
      } else {
        // Return default set
        return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
      }
    } catch (e) {
      return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
    }
  }
  
  /// Cleanup resources
  @override
  Future<void> dispose() async {
    print('Web detection service disposed');
  }
  
  /// Get server URL
  String get serverUrl => _serverUrl;
}