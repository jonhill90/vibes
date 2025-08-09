import React, { useEffect, useRef, useState } from 'react';

const VncViewer = ({ onStatusChange, wsUrl }) => {
  const canvasRef = useRef(null);
  const rfbRef = useRef(null);
  const [status, setStatus] = useState('Initializing...');
  const [isConnecting, setIsConnecting] = useState(false);

  const updateStatus = (newStatus) => {
    setStatus(newStatus);
    if (onStatusChange) onStatusChange(newStatus);
  };

  const connectToVNC = () => {
    console.log('VNC Connect attempt started...');
    
    if (isConnecting) {
      console.log('Already connecting, ignoring request');
      return;
    }

    if (!window.RFB) {
      updateStatus('noVNC library not available');
      console.error('window.RFB not available');
      return;
    }

    if (!canvasRef.current) {
      updateStatus('Canvas element not found');
      console.error('Canvas element not found');
      return;
    }

    setIsConnecting(true);
    updateStatus('Connecting to VNC...');

    try {
      console.log('Creating RFB instance with URL:', wsUrl);
      
      // Clean up existing connection
      if (rfbRef.current) {
        console.log('Cleaning up existing RFB connection');
        rfbRef.current.disconnect();
        rfbRef.current = null;
      }

      // Create new RFB connection
      rfbRef.current = new window.RFB(canvasRef.current, wsUrl, {
        credentials: {}
      });

      // Add event listeners
      rfbRef.current.addEventListener('connect', () => {
        console.log('VNC connected successfully');
        updateStatus('Connected');
        setIsConnecting(false);
      });

      rfbRef.current.addEventListener('disconnect', (e) => {
        console.log('VNC disconnected:', e.detail);
        updateStatus('Disconnected');
        setIsConnecting(false);
        rfbRef.current = null;
      });

      console.log('RFB instance created successfully');

    } catch (error) {
      console.error('Failed to create VNC connection:', error);
      updateStatus(`Connection error: ${error.message}`);
      setIsConnecting(false);
    }
  };

  const disconnect = () => {
    console.log('VNC Disconnect requested');
    if (rfbRef.current) {
      rfbRef.current.disconnect();
      rfbRef.current = null;
    }
    setIsConnecting(false);
    updateStatus('Disconnected');
  };

  // Auto-connect when component mounts and canvas is ready
  useEffect(() => {
    console.log('VncViewer useEffect triggered');
    if (canvasRef.current && window.RFB && !isConnecting && !rfbRef.current) {
      console.log('Conditions met, starting auto-connect');
      const timer = setTimeout(() => {
        connectToVNC();
      }, 500); // Small delay to ensure DOM is fully ready
      
      return () => clearTimeout(timer);
    }
  }, [wsUrl, isConnecting]);

  // Check for window.RFB availability
  useEffect(() => {
    const checkRFB = () => {
      if (window.RFB) {
        console.log('window.RFB is available');
        updateStatus('noVNC loaded, ready to connect');
      } else {
        console.log('window.RFB not yet available, checking again...');
        updateStatus('Loading noVNC...');
        setTimeout(checkRFB, 100);
      }
    };
    
    checkRFB();
  }, []);

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#1a1a1a',
      border: '1px solid #444'
    }}>
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#2a2a2a', 
        color: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span>VNC Connection: {status}</span>
        <div>
          <button 
            onClick={connectToVNC} 
            disabled={isConnecting}
            style={{ 
              marginRight: '10px',
              padding: '5px 10px',
              backgroundColor: isConnecting ? '#666' : '#007ACC',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: isConnecting ? 'not-allowed' : 'pointer'
            }}
          >
            {isConnecting ? 'Connecting...' : 'Connect'}
          </button>
          <button 
            onClick={disconnect}
            style={{ 
              padding: '5px 10px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: 'pointer'
            }}
          >
            Disconnect
          </button>
        </div>
      </div>
      
      <div style={{ 
        flex: 1, 
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <canvas 
          ref={canvasRef}
          style={{ 
            display: 'block',
            maxWidth: '100%',
            maxHeight: '100%',
            backgroundColor: '#000'
          }}
        />
        {!rfbRef.current && (
          <div style={{
            position: 'absolute',
            color: '#888',
            fontSize: '14px',
            pointerEvents: 'none'
          }}>
            {status.includes('Connecting') ? '🔄 Connecting to VNC...' : '📺 VNC Display'}
          </div>
        )}
      </div>
    </div>
  );
};

export default VncViewer;
