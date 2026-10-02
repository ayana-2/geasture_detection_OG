// File: lib/services/prediction_service.dart
import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class PredictionService {
  // Backend URL configuration
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:5000'; // For web browser
    } else {
      return 'http://10.0.2.2:5000'; // For Android emulator
    }
  }
  
  // Timeout for API calls
  static const Duration _timeout = Duration(seconds: 10);
  
  // Check if Flask backend is running
  static Future<BackendStatus> checkBackendStatus() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(_timeout);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return BackendStatus(
          isConnected: true,
          status: data['status'] ?? 'unknown',
          message: data['message'] ?? 'Backend is running',
          modelLoaded: data['model_loaded'] ?? false,
        );
      } else {
        return BackendStatus(
          isConnected: false,
          message: 'HTTP ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      return BackendStatus(
        isConnected: false,
        message: 'Cannot connect to backend: $e\n'
            'Make sure Flask is running: python app.py',
      );
    }
  }
  
  // Get available letters from backend
  static Future<List<String>> getAvailableLetters() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/api/letters'))
          .timeout(_timeout);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final letters = data['letters'] as List<dynamic>;
        return letters.map((l) => l.toString()).toList();
      }
      return _getDefaultLetters();
    } catch (e) {
      // Return default if backend fails
      return _getDefaultLetters();
    }
  }
  
  static List<String> _getDefaultLetters() {
    return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
            'U', 'V', 'W', 'X', 'Y', 'Z', 'space', 'nothing'];
  }
  
  // Send image for detection (base64)
  static Future<DetectionResult> detectFromBase64(String base64Image) async {
    try {
      // Remove data URL prefix if present
      String imageData = base64Image;
      if (imageData.contains('base64,')) {
        imageData = imageData.split('base64,').last;
      }
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/detect'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'image': 'data:image/jpeg;base64,$imageData'}),
      ).timeout(_timeout);
      
      return _parseResponse(response);
    } catch (e) {
      print('Detection failed: $e');
      return DetectionResult.error('Detection failed: $e');
    }
  }
  
  // Simple detection for testing
  static Future<DetectionResult> simpleDetect() async {
    // Check if backend is available first
    final status = await checkBackendStatus();
    
    if (!status.isConnected) {
      // Backend not available, use mock detection
      return await mockDetection();
    }
    
    try {
      // For simple testing without actual image
      final response = await http.post(
        Uri.parse('$baseUrl/api/detect'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'test': 'simple_detection'}),
      ).timeout(_timeout);
      
      return _parseResponse(response);
    } catch (e) {
      return DetectionResult.error('Simple detection failed: $e');
    }
  }
  
  // Mock detection for testing (returns random letters)
  static Future<DetectionResult> mockDetection() async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Generate random letter and confidence
    final letters = await getAvailableLetters();
    final randomLetter = letters[DateTime.now().millisecondsSinceEpoch % letters.length];
    final randomConfidence = 0.6 + (DateTime.now().millisecond % 40) / 100.0;
    
    return DetectionResult(
      letter: randomLetter,
      confidence: randomConfidence,
      isValid: randomConfidence > 0.6,
      rawData: {'detection_mode': 'mock'},
      success: true,
      message: 'Mock detection (backend not connected)',
    );
  }
  
  // Private helper: parse HTTP response
  static DetectionResult _parseResponse(http.Response response) {
    if (response.statusCode == 200) {
      try {
        final data = jsonDecode(response.body);
        
        // Check if backend returned success
        if (data['success'] == true) {
          return DetectionResult(
            letter: data['letter']?.toString() ?? '?',
            confidence: (data['confidence'] ?? 0.0).toDouble(),
            isValid: data['is_valid'] ?? false,
            rawData: data,
            success: true,
            message: 'Detection successful',
          );
        } else {
          return DetectionResult.error(
            'Backend error: ${data['error'] ?? 'Unknown error'}',
          );
        }
      } catch (e) {
        return DetectionResult.error('Failed to parse response: $e');
      }
    } else {
      return DetectionResult.error(
        'HTTP ${response.statusCode}: ${response.body}',
      );
    }
  }
  
  // Get backend URL for display
  static String getBackendUrl() {
    return baseUrl;
  }
  
  // Get connection status for UI
  static Future<String> getConnectionStatus() async {
    final status = await checkBackendStatus();
    if (status.isConnected) {
      return 'Connected to ${getBackendUrl()}';
    } else {
      return 'Not connected. Using mock detection.';
    }
  }
}

// Model class for detection results
class DetectionResult {
  final String letter;
  final double confidence;
  final bool isValid;
  final Map<String, dynamic> rawData;
  final bool success;
  final String message;
  
  DetectionResult({
    required this.letter,
    required this.confidence,
    required this.isValid,
    required this.rawData,
    required this.success,
    required this.message,
  });
  
  // Factory for error results
  factory DetectionResult.error(String errorMessage) {
    return DetectionResult(
      letter: '?',
      confidence: 0.0,
      isValid: false,
      rawData: {'error': errorMessage},
      success: false,
      message: errorMessage,
    );
  }
  
  // Format confidence as percentage
  String get confidencePercent => '${(confidence * 100).toStringAsFixed(1)}%';
  
  // Check if result has meaningful data
  bool get hasDetection => letter != '?' && confidence > 0.1;
  
  @override
  String toString() {
    return 'DetectionResult(letter: $letter, confidence: $confidence, valid: $isValid)';
  }
}

// Model class for backend status
class BackendStatus {
  final bool isConnected;
  final String status;
  final String message;
  final bool modelLoaded;
  
  BackendStatus({
    required this.isConnected,
    this.status = 'unknown',
    this.message = '',
    this.modelLoaded = false,
  });
  
  // Helper for UI display
  String get displayStatus {
    if (!isConnected) return 'Not Connected';
    if (modelLoaded) return 'Connected (Real Model)';
    return 'Connected (Mock Mode)';
  }
}