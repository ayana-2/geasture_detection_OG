// frontend/src/components/GestureDetector.jsx
import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './GestureDetector.css';

const GestureDetector = ({ onDetection, cameraActive, setCameraActive }) => {
  const webcamRef = useRef(null);
  const [detectionResult, setDetectionResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fps, setFps] = useState(0);
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [showDebug, setShowDebug] = useState(false);
  const [debugImage, setDebugImage] = useState(null);
  const frameCountRef = useRef(0);
  const lastFpsUpdateRef = useRef(Date.now());
  const animationRef = useRef();

  // Initialize gesture detection session
  useEffect(() => {
    const initSession = async () => {
      try {
        await axios.get('http://localhost:5000/health');
        console.log('✅ Backend connected');
      } catch (error) {
        console.warn('⚠️ Backend health check failed, but continuing...');
      }
    };
    initSession();
  }, []);

  // Capture and process frame
  const captureAndProcess = useCallback(async () => {
    if (!webcamRef.current || !cameraActive || isProcessing) return;

    setIsProcessing(true);
    const startTime = performance.now();

    try {
      // Capture image from webcam
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        setIsProcessing(false);
        return;
      }

      // Convert base64 to blob
      const base64Data = imageSrc.split(',')[1];
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(res => res.blob());

      // Create FormData for upload
      const formData = new FormData();
      formData.append('image', blob, 'frame.jpg');

      // Send to backend for detection
      const response = await axios.post('http://localhost:5000/api/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: {
          sessionId,
          metadata: JSON.stringify({
            device: navigator.userAgent,
            resolution: `${webcamRef.current.video.videoWidth}x${webcamRef.current.video.videoHeight}`,
            fps: Math.round(fps)
          })
        }
      });

      if (response.data.success) {
        const result = response.data.data.detection;
        setDetectionResult(result);
        
        // Call parent callback
        onDetection({
          ...result,
          id: response.data.data.id,
          timestamp: new Date().toISOString(),
          debugImageUrl: response.data.data.debugImageUrl
        });

        // Show debug image if available
        if (response.data.data.debugImageUrl) {
          setDebugImage(`http://localhost:5000${response.data.data.debugImageUrl}`);
        }
      }

    } catch (error) {
      console.error('❌ Detection error:', error);
      setDetectionResult({
        gesture: 'ERROR',
        confidence: 0,
        message: 'Detection failed'
      });
    } finally {
      setIsProcessing(false);
      
      // Calculate FPS
      const endTime = performance.now();
      const processingTime = endTime - startTime;
      
      frameCountRef.current++;
      const now = Date.now();
      if (now - lastFpsUpdateRef.current >= 1000) {
        setFps(frameCountRef.current);
        frameCountRef.current = 0;
        lastFpsUpdateRef.current = now;
      }

      // Continue processing if camera is still active
      if (cameraActive) {
        animationRef.current = requestAnimationFrame(captureAndProcess);
      }
    }
  }, [cameraActive, isProcessing, sessionId, fps, onDetection]);

  // Start/stop detection loop
  useEffect(() => {
    if (cameraActive && !isProcessing) {
      animationRef.current = requestAnimationFrame(captureAndProcess);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [cameraActive, captureAndProcess, isProcessing]);

  // Toggle camera
  const toggleCamera = () => {
    setCameraActive(!cameraActive);
    if (cameraActive) {
      setDetectionResult(null);
      setDebugImage(null);
    }
  };

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user"
  };

  return (
    <div className="gesture-detector">
      <div className="detector-container">
        {/* Webcam feed */}
        <div className="webcam-section">
          <div className="webcam-wrapper">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="webcam-feed"
            />
            
            {/* Overlay for detection result */}
            {detectionResult && (
              <div className="detection-overlay">
                <div className={`gesture-badge ${detectionResult.confidence > 0.8 ? 'high' : detectionResult.confidence > 0.6 ? 'medium' : 'low'}`}>
                  <span className="gesture-letter">{detectionResult.gesture}</span>
                  <span className="confidence">{(detectionResult.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            )}

            {/* Camera status */}
            <div className="camera-status">
              <div className={`status-indicator ${cameraActive ? 'recording' : 'paused'}`}></div>
              <span>{cameraActive ? 'LIVE' : 'PAUSED'}</span>
              <span className="fps">FPS: {fps}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="controls">
            <button 
              className={`btn ${cameraActive ? 'btn-stop' : 'btn-start'}`}
              onClick={toggleCamera}
            >
              {cameraActive ? '⏸ Stop Detection' : '▶ Start Detection'}
            </button>
            
            <button 
              className="btn btn-debug"
              onClick={() => setShowDebug(!showDebug)}
            >
              {showDebug ? 'Hide Debug' : 'Show Debug'}
            </button>
          </div>
        </div>

        {/* Results panel */}
        <div className="results-panel">
          <h3>Detection Results</h3>
          
          {detectionResult ? (
            <div className="result-card">
              <div className="gesture-display">
                <div className="gesture-symbol">{detectionResult.gesture}</div>
                <div className="gesture-info">
                  <h4>Letter: {detectionResult.gesture}</h4>
                  <p>{detectionResult.message}</p>
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${detectionResult.confidence * 100}%` }}
                    ></div>
                  </div>
                  <div className="details">
                    <span>Confidence: {(detectionResult.confidence * 100).toFixed(1)}%</span>
                    {detectionResult.area && <span>Area: {Math.round(detectionResult.area)}px²</span>}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="no-result">
              <p>No detection yet. Start the camera to begin.</p>
            </div>
          )}

          {/* Debug info */}
          {showDebug && (
            <div className="debug-section">
              <h4>Debug Information</h4>
              <div className="debug-info">
                <p>Session ID: {sessionId}</p>
                <p>FPS: {fps}</p>
                <p>Status: {isProcessing ? 'Processing...' : 'Ready'}</p>
                <p>Camera: {cameraActive ? 'Active' : 'Inactive'}</p>
              </div>
              
              {/* Debug image */}
              {debugImage && (
                <div className="debug-image">
                  <h5>Debug Frame:</h5>
                  <img src={debugImage} alt="Debug" className="debug-frame" />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GestureDetector;