// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Webcam from 'react-webcam';

// Components
import GestureDetector from './components/GestureDetector';
import DetectionHistory from './components/DetectionHistory';
import GestureLibrary from './components/GestureLibrary';
import RealTimeDashboard from './components/RealTimeDashboard';
import Navbar from './components/Navbar';

function App() {
  const [detections, setDetections] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  return (
    <Router>
      <div className="App">
        <Navbar />
        
        <Routes>
          <Route path="/" element={
            <div className="home-page">
              <h1>🎯 Hand Gesture Recognition System</h1>
              <p>Real-time hand gesture detection using computer vision</p>
              
              <div className="status-indicator">
                <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
                <span>Backend: {isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>

              <GestureDetector 
                onDetection={(detection) => {
                  setDetections(prev => [detection, ...prev]);
                }}
                cameraActive={cameraActive}
                setCameraActive={setCameraActive}
              />
            </div>
          } />
          
          <Route path="/dashboard" element={<RealTimeDashboard />} />
          <Route path="/history" element={<DetectionHistory detections={detections} />} />
          <Route path="/library" element={<GestureLibrary />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;