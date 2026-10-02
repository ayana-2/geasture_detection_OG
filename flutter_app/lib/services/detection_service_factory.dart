import 'package:flutter/foundation.dart';
import 'detection_service.dart';
import 'web_detection_service.dart';

class DetectionServiceFactory with ChangeNotifier {
  DetectionService? _service;
  bool _useWebService = false;

  DetectionService getService({String? serverUrl}) {
    if (_service != null) return _service!;

    if (_useWebService && serverUrl != null) {
      _service = WebDetectionService(serverUrl);
    } else {
      _service = TFLiteDetectionService();
    }

    return _service!;
  }

  void toggleService(bool useWeb) {
    _useWebService = useWeb;
    _service = null;
    notifyListeners();
  }

  bool get useWebService => _useWebService;
}