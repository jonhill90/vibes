import React, { useEffect, useRef, useState } from 'react';

const VncViewer = ({ onStatusChange, wsUrl }) => {
  const containerRef = useRef(null);  // Changed from canvasRef to containerRef
  const rfbRef = useRef(null);
  const [status, setStatus] = useState('Initializing...');
  const [isConnecting, setIsConnecting] = useState(false);
  const [novncReady, setNovncReady] = useState(false);
  const [hasAutoConnected, setHasAutoConnected] = useState(false);

  const updateStatus = (newStatus) => {
    setStatus(newStatus);
    if (onStatusChange) {
      // Map internal statuses to external ones
      const externalStatus = newStatus.toLowerCase().includes('connected') ? 'connected' : 'disconnected';
      onStatusChange(externalStatus);
    }
  };

  // Build proper WebSocket URL from relative path
  const buildWebSocketUrl = (relativePath) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const cleanPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
    return `${protocol}//${host}${cleanPath}`;
  };

  const connectToVNC = () => {
    console.log('VNC Connect attempt started...');
    
    if (isConnecting) {
      console.log('Already connecting, ignoring request');
      return;
    }

    if (rfbRef.current) {
      console.log('Already connected, ignoring request');
      return;
    }

    if (!novncReady || !window.RFB) {
      updateStatus('noVNC library not ready');
      console.error('window.RFB not available or noVNC not ready');
      return;
    }

    if (!containerRef.current) {  // Changed from canvasRef to containerRef
      updateStatus('Container element not found');
      console.error('Container element not found');
      return;
    }

    setIsConnecting(true);
    updateStatus('Connecting to VNC...');

    try {
      // Build full WebSocket URL
      const fullWsUrl = buildWebSocketUrl(wsUrl);
      console.log('Creating RFB instance with URL:', fullWsUrl);

      // Create new RFB connection using container div (like working test HTML)
      rfbRef.current = new window.RFB(containerRef.current, fullWsUrl, {
        credentials: { password: '' }
      });

      // Add event listeners
      rfbRef.current.addEventListener('connect', () => {
        console.log('✅ VNC connected successfully');
        updateStatus('Connected');
        setIsConnecting(false);
      });

      rfbRef.current.addEventListener('disconnect', (e) => {
        console.log('❌ VNC disconnected:', e.detail);
        const reason = e.detail?.clean ? 'Clean disconnect' : 'Connection lost';
        updateStatus(`Disconnected - ${reason}`);
        setIsConnecting(false);
        rfbRef.current = null;
        
        // Only auto-reconnect if it was NOT a clean disconnect (connection lost unexpectedly)
        if (!e.detail?.clean && novncReady) {
          console.log('Connection lost unexpectedly, will retry in 5 seconds...');
          setTimeout(() => {
            if (!rfbRef.current && novncReady) {
              connectToVNC();
            }
          }, 5000);
        }
      });

      rfbRef.current.addEventListener('credentialsrequired', () => {
        console.log('VNC credentials required - this should not happen with SecurityTypes None');
        updateStatus('Authentication required (unexpected)');
        setIsConnecting(false);
      });

      rfbRef.current.addEventListener('securityfailure', (e) => {
        console.log('VNC security failure:', e.detail);
        updateStatus('Authentication failed');
        setIsConnecting(false);
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

  // Listen for noVNC ready event
  useEffect(() => {
    const handleNovncReady = () => {
      console.log('noVNC ready event received');
      setNovncReady(true);
      updateStatus('noVNC loaded, ready to connect');
    };

    // Check if already available
    if (window.RFB) {
      handleNovncReady();
    } else {
      // Listen for ready event
      window.addEventListener('novnc-ready', handleNovncReady);
      return () => window.removeEventListener('novnc-ready', handleNovncReady);
    }
  }, []);

  // Auto-connect ONCE when everything is ready
  useEffect(() => {
    console.log('VncViewer mount effect - novncReady:', novncReady, 'hasAutoConnected:', hasAutoConnected);
    if (novncReady && containerRef.current && !hasAutoConnected && !rfbRef.current) {
      console.log('Conditions met, starting auto-connect (once only)');
      setHasAutoConnected(true);
      const timer = setTimeout(() => {
        connectToVNC();
      }, 1000); // Give UI time to stabilize
      
      return () => clearTimeout(timer);
    }
  }, [novncReady]); // Only depend on novncReady

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
            disabled={isConnecting || !novncReady || rfbRef.current}
            style={{ 
              marginRight: '10px',
              padding: '5px 10px',
              backgroundColor: (isConnecting || !novncReady || rfbRef.current) ? '#666' : '#007ACC',
              color: 'white',
              border: 'none',
              borderRadius: '3px',
              cursor: (isConnecting || !novncReady || rfbRef.current) ? 'not-allowed' : 'pointer'
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
        {/* Changed from <canvas> to <div> container like working test HTML */}
        <div 
          ref={containerRef}
          style={{ 
            width: '100%',
            height: '100%',
            backgroundColor: '#000',
            border: 'none'
          }}
        />
        {!rfbRef.current && (
          <div style={{
            position: 'absolute',
            color: '#888',
            fontSize: '14px',
            pointerEvents: 'none',
            textAlign: 'center'
          }}>
            {isConnecting ? (
              <>🔄 Connecting to VNC...<br/>Please wait...</>
            ) : novncReady ? (
              <>📺 Click Connect to view desktop<br/>URL: {wsUrl}</>
            ) : (
              <>⏳ Loading noVNC library...</>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VncViewer;
