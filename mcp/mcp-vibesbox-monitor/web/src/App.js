import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [status, setStatus] = useState(null);
  const [operations, setOperations] = useState([]);
  const [currentScreenshot, setCurrentScreenshot] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Fetch initial status
    fetchStatus();
    fetchOperations();
    
    // Setup WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'operation') {
        setOperations(prev => [data.operation, ...prev.slice(0, 49)]); // Keep last 50
      } else if (data.type === 'screenshot') {
        setCurrentScreenshot(data.screenshot);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/api/status');
      setStatus(response.data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const fetchOperations = async () => {
    try {
      const response = await axios.get('/api/operations');
      setOperations(response.data);
    } catch (error) {
      console.error('Error fetching operations:', error);
    }
  };

  const takeScreenshot = async () => {
    try {
      const response = await axios.post('/api/screenshot');
      setCurrentScreenshot(response.data.screenshot);
    } catch (error) {
      console.error('Error taking screenshot:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getOperationIcon = (operation) => {
    switch (operation) {
      case 'click_desktop': return '🖱️';
      case 'type_text': return '⌨️';
      case 'take_screenshot': return '📸';
      case 'drag_mouse': return '🔄';
      case 'send_keys': return '🔤';
      default: return '🔧';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🖥️ MCP Vibesbox Monitor</h1>
        <div className="status-bar">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          {status && (
            <span className="vibesbox-status">
              Vibesbox: {status.vibesbox_connected ? '🟢 Online' : '🔴 Offline'}
            </span>
          )}
        </div>
      </header>

      <div className="dashboard">
        <div className="screenshot-panel">
          <div className="panel-header">
            <h2>📸 Current View</h2>
            <button onClick={takeScreenshot} className="btn-primary">
              Take Screenshot
            </button>
          </div>
          <div className="screenshot-container">
            {currentScreenshot ? (
              <img 
                src={`data:image/png;base64,${currentScreenshot}`} 
                alt="Current Vibesbox State"
                className="screenshot"
              />
            ) : (
              <div className="no-screenshot">
                <p>No screenshot available</p>
                <button onClick={takeScreenshot} className="btn-secondary">
                  Take First Screenshot
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="operations-panel">
          <div className="panel-header">
            <h2>📊 Recent Operations</h2>
            <span className="operation-count">
              {operations.length} operations logged
            </span>
          </div>
          <div className="operations-list">
            {operations.length > 0 ? (
              operations.map((op, index) => (
                <div key={index} className="operation-item">
                  <div className="operation-header">
                    <span className="operation-icon">
                      {getOperationIcon(op.operation)}
                    </span>
                    <span className="operation-name">{op.operation}</span>
                    <span className="operation-time">
                      {formatTimestamp(op.timestamp)}
                    </span>
                  </div>
                  <div className="operation-details">
                    {Object.entries(op.details).map(([key, value]) => (
                      <div key={key} className="detail-item">
                        <span className="detail-key">{key}:</span>
                        <span className="detail-value">
                          {typeof value === 'object' ? JSON.stringify(value) : value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-operations">
                <p>No operations recorded yet</p>
                <p>Operations will appear here as Claude interacts with the vibesbox</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="App-footer">
        <p>MCP Vibesbox Monitor v1.0 - Real-time GUI automation monitoring</p>
      </footer>
    </div>
  );
}

export default App;
