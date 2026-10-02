// frontend/src/components/RealTimeDashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RealTimeDashboard.css';

const RealTimeDashboard = () => {
  const [stats, setStats] = useState({
    totalDetections: 0,
    uniqueGestures: 0,
    avgConfidence: 0,
    recentDetections: []
  });
  const [gestureDistribution, setGestureDistribution] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);

  useEffect(() => {
    // Fetch initial stats
    fetchStats();
    fetchGestureDistribution();
    
    // Set up real-time updates
    const eventSource = new EventSource('http://localhost:5000/api/detect/stream');
    
    eventSource.onmessage = (event) => {
      if (event.data) {
        try {
          const data = JSON.parse(event.data);
          if (data.gesture) {
            setRealtimeData(prev => [data, ...prev.slice(0, 9)]);
            fetchStats(); // Refresh stats
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      eventSource.close();
    };

    // Poll for updates every 30 seconds
    const interval = setInterval(fetchStats, 30000);

    return () => {
      eventSource.close();
      clearInterval(interval);
    };
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/detect', {
        params: { limit: 10 }
      });
      
      const recent = response.data.data;
      const uniqueGestures = [...new Set(recent.map(d => d.gesture))].length;
      const avgConfidence = recent.length > 0
        ? recent.reduce((sum, d) => sum + d.confidence, 0) / recent.length
        : 0;

      setStats({
        totalDetections: response.data.total,
        uniqueGestures,
        avgConfidence,
        recentDetections: recent
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchGestureDistribution = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/detect');
      const distribution = response.data.statistics || [];
      setGestureDistribution(distribution);
    } catch (error) {
      console.error('Error fetching distribution:', error);
    }
  };

  return (
    <div className="dashboard">
      <h1>📊 Real-Time Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Detections</h3>
          <div className="stat-number">{stats.totalDetections.toLocaleString()}</div>
          <div className="stat-trend">↗️ +12% this week</div>
        </div>
        
        <div className="stat-card">
          <h3>Unique Gestures</h3>
          <div className="stat-number">{stats.uniqueGestures}</div>
          <div className="stat-trend">26 possible gestures</div>
        </div>
        
        <div className="stat-card">
          <h3>Avg Confidence</h3>
          <div className="stat-number">{(stats.avgConfidence * 100).toFixed(1)}%</div>
          <div className="stat-trend">🎯 Accuracy rate</div>
        </div>
        
        <div className="stat-card">
          <h3>Active Sessions</h3>
          <div className="stat-number">3</div>
          <div className="stat-trend">👥 Currently online</div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="realtime-feed">
          <h3>🎯 Real-Time Detections</h3>
          <div className="detection-stream">
            {realtimeData.map((detection, index) => (
              <div key={index} className="realtime-card">
                <div className="gesture-badge-small">{detection.gesture}</div>
                <div className="realtime-info">
                  <span className="confidence-badge">
                    {(detection.confidence * 100).toFixed(1)}%
                  </span>
                  <span className="timestamp">
                    {new Date(detection.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="gesture-distribution">
          <h3>📈 Gesture Distribution</h3>
          <div className="distribution-list">
            {gestureDistribution.map((item, index) => (
              <div key={item._id || index} className="distribution-item">
                <div className="gesture-label">
                  <span className="gesture-letter">{item._id}</span>
                  <span className="gesture-count">{item.count}</span>
                </div>
                <div className="distribution-bar">
                  <div 
                    className="bar-fill"
                    style={{ width: `${(item.count / stats.totalDetections) * 100}%` }}
                  ></div>
                </div>
                <span className="confidence-avg">
                  {(item.avgConfidence * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="recent-detections">
        <h3>🕐 Recent Detections</h3>
        <table className="detections-table">
          <thead>
            <tr>
              <th>Gesture</th>
              <th>Confidence</th>
              <th>Area</th>
              <th>Time</th>
              <th>Session</th>
            </tr>
          </thead>
          <tbody>
            {stats.recentDetections.map((detection) => (
              <tr key={detection._id}>
                <td>
                  <span className="table-gesture">{detection.gesture}</span>
                </td>
                <td>
                  <div className="confidence-cell">
                    <div 
                      className="confidence-visual"
                      style={{ width: `${detection.confidence * 100}%` }}
                    ></div>
                    <span>{(detection.confidence * 100).toFixed(1)}%</span>
                  </div>
                </td>
                <td>{detection.area ? Math.round(detection.area) : 'N/A'}</td>
                <td>
                  {new Date(detection.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </td>
                <td className="session-id">{detection.sessionId?.substring(0, 8)}...</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RealTimeDashboard;