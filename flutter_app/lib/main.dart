import 'dart:async';
import 'dart:convert';
import 'dart:html' as html;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const SignLanguageTranslatorApp());
}

class SignLanguageTranslatorApp extends StatelessWidget {
  const SignLanguageTranslatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sign Language Translator',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      debugShowCheckedModeBanner: false,
      home: const TranslationDashboard(),
    );
  }
}

class TranslationDashboard extends StatefulWidget {
  const TranslationDashboard({super.key});

  @override
  State<TranslationDashboard> createState() => _TranslationDashboardState();
}

class _TranslationDashboardState extends State<TranslationDashboard> {
  // Backend configuration
  final String _backendUrl = 'http://127.0.0.1:5000';
  final String _wsUrl = 'ws://127.0.0.1:5000';
  
  // App state
  String _backendStatus = 'Connecting...';
  String _currentGesture = '👋 Show your hand';
  double _confidence = 0.0;
  String _sentence = '';
  String? _processedFrame;
  bool _isTranslating = false;
  bool _isConnected = false;
  
  // WebSocket
  WebSocketChannel? _channel;
  StreamSubscription? _wsSubscription;
  
  // Camera
  html.VideoElement? _videoElement;
  html.CanvasElement? _canvasElement;
  Timer? _frameTimer;
  
  // ASL Alphabet reference
  final Map<String, String> _aslAlphabet = {
    'A': '✊ Thumb out',
    'B': '✋ Flat hand',
    'C': 'C shape',
    'D': '👉 Point up',
    'E': '🤚 Fingers curled',
    'F': '👌 OK sign',
    'G': '👉 Point sideways',
    'H': '👉👈 Two fingers',
    'I': '☝️ Pinky up',
    'J': '✍️ J motion',
    'K': '✌️ V with thumb',
    'L': '👆 L shape',
    'M': '✊ Three fingers down',
    'N': '✌️ Two fingers down',
    'O': '⭕ O shape',
    'P': '👇 P shape',
    'Q': '👉 Q shape',
    'R': '✌️ Cross fingers',
    'S': '✊ Fist',
    'T': '👍 Thumb between fingers',
    'U': '✌️ Two fingers up',
    'V': '✌️ Peace sign',
    'W': '✌️ Three fingers',
    'X': '👉 Bent index',
    'Y': '🤟 Rock on',
    'Z': '💫 Z motion',
  };

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkBackendConnection();
    });
  }
  
  void _initializeCamera() {
    _videoElement = html.VideoElement()
      ..width = 640
      ..height = 480
      ..autoplay = true;
    
    _canvasElement = html.CanvasElement()
      ..width = 640
      ..height = 480;
  }
  
  Future<void> _checkBackendConnection() async {
    try {
      final response = await http.get(
        Uri.parse(_backendUrl),
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        setState(() => _backendStatus = '✅ Connected');
        _connectWebSocket();
      } else {
        setState(() => _backendStatus = '❌ Error: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _backendStatus = '❌ Cannot connect');
      _showError('Backend not running. Open Terminal and run: python app.py');
    }
  }
  
  void _connectWebSocket() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(_wsUrl));
      
      _wsSubscription = _channel!.stream.listen(
        (message) {
          try {
            final data = json.decode(message);
            
            if (data['gesture'] != null) {
              setState(() {
                _currentGesture = data['gesture'];
                _confidence = (data['confidence'] ?? 0.0).toDouble();
              });
            }
            
            if (data['frame'] != null) {
              setState(() {
                _processedFrame = data['frame'];
              });
            }
            
            if (data['sentence'] != null) {
              setState(() {
                _sentence = data['sentence'];
              });
            }
          } catch (e) {
            print('Parse error: $e');
          }
        },
        onError: (error) {
          print('WebSocket error: $error');
          setState(() => _isConnected = false);
        },
        onDone: () {
          print('WebSocket closed');
          setState(() => _isConnected = false);
        },
      );
      
      setState(() => _isConnected = true);
      
    } catch (e) {
      print('WebSocket failed: $e');
      setState(() => _isConnected = false);
    }
  }
  
  Future<void> _startTranslation() async {
    try {
      // Request camera access
      final stream = await html.window.navigator.mediaDevices!
          .getUserMedia({'video': { 
            'width': { 'ideal': 640 },
            'height': { 'ideal': 480 },
            'facingMode': 'user'
          }});
      
      _videoElement!.srcObject = stream;
      
      // Start sending frames
      _frameTimer = Timer.periodic(const Duration(milliseconds: 150), (timer) {
        _captureAndSendFrame();
      });
      
      // Start backend translation
      await http.get(Uri.parse('$_backendUrl/api/start'));
      
      setState(() => _isTranslating = true);
      
      _showSuccess('Translation started! Show your hand to camera.');
      
    } catch (e) {
      _showError('Camera error: $e');
    }
  }
  
  void _captureAndSendFrame() {
    if (_videoElement == null || 
        _canvasElement == null || 
        _channel == null || 
        !_isTranslating) return;
    
    try {
      final ctx = _canvasElement!.context2D;
      ctx.drawImage(_videoElement!, 0, 0);
      
      final imageData = _canvasElement!.toDataUrl('image/jpeg', 0.7);
      
      _channel!.sink.add(json.encode({
        'image': imageData,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
      }));
    } catch (e) {
      print('Frame error: $e');
    }
  }
  
  Future<void> _stopTranslation() async {
    _frameTimer?.cancel();
    
    if (_videoElement?.srcObject != null) {
      final stream = _videoElement!.srcObject as html.MediaStream;
      final tracks = stream.getTracks();
      for (final track in tracks) {
        track.stop();
      }
    }
    
    if (_backendStatus.contains('✅')) {
      await http.get(Uri.parse('$_backendUrl/api/stop'));
    }
    
    setState(() {
      _isTranslating = false;
      _processedFrame = null;
      _currentGesture = '👋 Show your hand';
      _confidence = 0.0;
    });
    
    _showInfo('Translation stopped');
  }
  
  Future<void> _addToSentence() async {
    if (_currentGesture != 'No hand detected' && 
        _currentGesture != '👋 Show your hand' &&
        _confidence > 0.5) {
      
      final gesture = _currentGesture.replaceAll(RegExp(r'[^A-Za-z]'), '');
      
      if (gesture.isNotEmpty) {
        try {
          final response = await http.get(
            Uri.parse('$_backendUrl/api/add/$gesture'),
          );
          
          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            setState(() => _sentence = data['sentence'] ?? _sentence + gesture);
            _showSuccess('Added: $gesture');
          }
        } catch (e) {
          // Fallback: add locally
          setState(() => _sentence += gesture);
        }
      }
    } else {
      _showError('No valid gesture detected');
    }
  }
  
  Future<void> _clearSentence() async {
    try {
      await http.get(Uri.parse('$_backendUrl/api/clear'));
      setState(() => _sentence = '');
      _showInfo('Sentence cleared');
    } catch (e) {
      setState(() => _sentence = '');
    }
  }
  
  Future<void> _speakSentence() async {
    if (_sentence.isEmpty) {
      _showError('No sentence to speak');
      return;
    }
    
    // Fixed: Use null-aware operator and check availability
    if (html.window.speechSynthesis != null) {
      final utterance = html.SpeechSynthesisUtterance(_sentence);
      // Use ?. to safely call speak()
      html.window.speechSynthesis?.speak(utterance);
      _showSuccess('Speaking: $_sentence');
    } else {
      _showError('Text-to-speech not supported in this browser');
    }
  }
  
  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
  
  void _showSuccess(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
  
  void _showInfo(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.blue,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
  
  Widget _buildVideoDisplay() {
    if (_processedFrame != null && _processedFrame!.isNotEmpty) {
      try {
        String base64Data = _processedFrame!;
        if (base64Data.contains(',')) {
          base64Data = base64Data.split(',')[1];
        }
        
        final bytes = base64.decode(base64Data);
        
        return ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: Image.memory(
            bytes,
            width: 640,
            height: 480,
            fit: BoxFit.cover,
            gaplessPlayback: true,
            errorBuilder: (context, error, stackTrace) {
              return _buildPlaceholder();
            },
          ),
        );
      } catch (e) {
        return _buildPlaceholder();
      }
    }
    
    return _buildPlaceholder();
  }
  
  Widget _buildPlaceholder() {
    return Container(
      width: 640,
      height: 480,
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            _isTranslating ? Icons.camera : Icons.camera_alt,
            size: 80,
            color: _isTranslating ? Colors.green : Colors.grey,
          ),
          const SizedBox(height: 20),
          Text(
            _isTranslating ? 'Processing hand gestures...' : 'Camera Ready',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
            ),
          ),
          if (_isTranslating) ...[
            const SizedBox(height: 20),
            const CircularProgressIndicator(color: Colors.green),
            const SizedBox(height: 10),
            const Text(
              'Show your hand clearly to camera',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ],
      ),
    );
  }
  
  Widget _buildASLGuide() {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.blue[100]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ASL Alphabet Guide',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.blue,
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            height: 150,
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 7,
                crossAxisSpacing: 5,
                mainAxisSpacing: 5,
              ),
              itemCount: 26,
              itemBuilder: (context, index) {
                final letter = String.fromCharCode(65 + index);
                return Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(5),
                    border: Border.all(color: Colors.blue[200]!),
                  ),
                  child: Center(
                    child: Text(
                      letter,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'Special Commands:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const Text('• Space: Add space between words'),
          const Text('• Del: Delete last character'),
        ],
      ),
    );
  }
  
  @override
  void dispose() {
    _stopTranslation();
    _wsSubscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.translate, color: Colors.white),
            SizedBox(width: 10),
            Text(
              'Sign Language Translator',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 20,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.blue[700],
        foregroundColor: Colors.white,
        elevation: 5,
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Bar
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: Row(
                children: [
                  _buildStatusIndicator('Backend', _backendStatus.contains('✅')),
                  const SizedBox(width: 20),
                  _buildStatusIndicator('Camera', _isTranslating),
                  const SizedBox(width: 20),
                  _buildStatusIndicator('Detection', _confidence > 0.3),
                  const Spacer(),
                  Text(
                    _backendStatus,
                    style: TextStyle(
                      color: _backendStatus.contains('✅') ? Colors.green : Colors.red,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 25),
            
            // Main Content
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Left Column - Video and Controls
                Expanded(
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            const Text(
                              '📹 LIVE HAND DETECTION',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            const SizedBox(height: 15),
                            Container(
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: _isTranslating ? Colors.green : Colors.grey,
                                  width: 3,
                                ),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: _buildVideoDisplay(),
                            ),
                            const SizedBox(height: 20),
                            
                            // Control Buttons
                            Wrap(
                              spacing: 15,
                              runSpacing: 15,
                              alignment: WrapAlignment.center,
                              children: [
                                ElevatedButton.icon(
                                  onPressed: _isTranslating ? _stopTranslation : _startTranslation,
                                  icon: Icon(
                                    _isTranslating ? Icons.stop : Icons.play_arrow,
                                    size: 24,
                                  ),
                                  label: Text(
                                    _isTranslating ? 'STOP TRANSLATION' : 'START TRANSLATION',
                                    style: const TextStyle(fontSize: 16),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _isTranslating ? Colors.red : Colors.green,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 25,
                                      vertical: 15,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                  ),
                                ),
                                
                                ElevatedButton.icon(
                                  onPressed: _addToSentence,
                                  icon: const Icon(Icons.add_circle),
                                  label: const Text(
                                    'ADD TO TEXT',
                                    style: TextStyle(fontSize: 16),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.blue,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 25,
                                      vertical: 15,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                  ),
                                ),
                                
                                ElevatedButton.icon(
                                  onPressed: _clearSentence,
                                  icon: const Icon(Icons.delete),
                                  label: const Text(
                                    'CLEAR TEXT',
                                    style: TextStyle(fontSize: 16),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.orange,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 25,
                                      vertical: 15,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                  ),
                                ),
                                
                                ElevatedButton.icon(
                                  onPressed: _speakSentence,
                                  icon: const Icon(Icons.volume_up),
                                  label: const Text(
                                    'SPEAK TEXT',
                                    style: TextStyle(fontSize: 16),
                                  ),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.purple,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 25,
                                      vertical: 15,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // ASL Guide
                      _buildASLGuide(),
                    ],
                  ),
                ),
                
                const SizedBox(width: 25),
                
                // Right Column - Results
                Container(
                  width: 400,
                  child: Column(
                    children: [
                      // Gesture Detection
                      Container(
                        padding: const EdgeInsets.all(25),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            const Text(
                              '✋ DETECTED GESTURE',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            const SizedBox(height: 25),
                            Container(
                              padding: const EdgeInsets.all(30),
                              decoration: BoxDecoration(
                                color: Colors.blue[50],
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: Colors.blue[100]!, width: 2),
                              ),
                              child: Column(
                                children: [
                                  Text(
                                    _currentGesture,
                                    style: const TextStyle(
                                      fontSize: 48,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.blue,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(
                                    _aslAlphabet[_currentGesture.replaceAll(RegExp(r'[^A-Z]'), '')] ?? 'Hand gesture',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: Colors.blue[700],
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 25),
                            
                            // Confidence Meter
                            Column(
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    const Text(
                                      'Confidence Level:',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                    Text(
                                      '${(_confidence * 100).toStringAsFixed(1)}%',
                                      style: TextStyle(
                                        fontSize: 20,
                                        fontWeight: FontWeight.bold,
                                        color: _confidence > 0.7 
                                            ? Colors.green 
                                            : _confidence > 0.4 
                                                ? Colors.orange 
                                                : Colors.red,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                LinearProgressIndicator(
                                  value: _confidence,
                                  backgroundColor: Colors.grey[200],
                                  color: _confidence > 0.7 
                                      ? Colors.green 
                                      : _confidence > 0.4 
                                          ? Colors.orange 
                                          : Colors.red,
                                  minHeight: 15,
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                const SizedBox(height: 5),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      'Low',
                                      style: TextStyle(color: Colors.grey[600]),
                                    ),
                                    Text(
                                      'High',
                                      style: TextStyle(color: Colors.grey[600]),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // Sentence Builder
                      Container(
                        padding: const EdgeInsets.all(25),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '📝 TRANSLATED TEXT',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                            const SizedBox(height: 15),
                            Container(
                              height: 200,
                              padding: const EdgeInsets.all(20),
                              decoration: BoxDecoration(
                                color: Colors.grey[50],
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(color: Colors.grey[300]!),
                              ),
                              child: SingleChildScrollView(
                                child: Text(
                                  _sentence.isEmpty 
                                      ? 'Your translated text will appear here...\n\nStart translation and add gestures to build sentences.' 
                                      : _sentence,
                                  style: TextStyle(
                                    fontSize: _sentence.isEmpty ? 18 : 24,
                                    color: _sentence.isEmpty ? Colors.grey : Colors.black,
                                    height: 1.5,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(height: 20),
                            Row(
                              children: [
                                Chip(
                                  label: Text('Characters: ${_sentence.length}'),
                                  backgroundColor: Colors.blue[100],
                                ),
                                const SizedBox(width: 10),
                                Chip(
                                  label: Text('Words: ${_sentence.split(' ').where((w) => w.isNotEmpty).length}'),
                                  backgroundColor: Colors.green[100],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 30),
            
            // Instructions
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.blue[100]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📋 HOW TO USE:',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(height: 15),
                  const Row(
                    children: [
                      Icon(Icons.play_arrow, color: Colors.green),
                      SizedBox(width: 10),
                      Expanded(child: Text('Click START TRANSLATION and allow camera access')),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Row(
                    children: [
                      Icon(Icons.back_hand, color: Colors.blue),
                      SizedBox(width: 10),
                      Expanded(child: Text('Show your hand clearly to the camera (good lighting)')),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Row(
                    children: [
                      Icon(Icons.add, color: Colors.orange),
                      SizedBox(width: 10),
                      Expanded(child: Text('Click ADD TO TEXT when correct letter is detected')),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Row(
                    children: [
                      Icon(Icons.volume_up, color: Colors.purple),
                      SizedBox(width: 10),
                      Expanded(child: Text('Click SPEAK TEXT to hear the translated sentence')),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 20),
            
            // Footer
            Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: Colors.blueGrey[50],
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.code, color: Colors.blueGrey),
                  const SizedBox(width: 10),
                  Text(
                    'Backend: $_backendUrl',
                    style: const TextStyle(color: Colors.blueGrey),
                  ),
                  const SizedBox(width: 20),
                  const Icon(Icons.wifi, color: Colors.blueGrey),
                  const SizedBox(width: 10),
                  Text(
                    'Status: ${_isConnected ? 'Connected' : 'Disconnected'}',
                    style: TextStyle(
                      color: _isConnected ? Colors.green : Colors.red,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusIndicator(String label, bool isActive) {
    return Column(
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(
            color: isActive ? Colors.green : Colors.red,
            shape: BoxShape.circle,
            boxShadow: [
              if (isActive)
                BoxShadow(
                  color: Colors.green.withOpacity(0.5),
                  blurRadius: 8,
                ),
            ],
          ),
        ),
        const SizedBox(height: 5),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: isActive ? Colors.green : Colors.red,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}