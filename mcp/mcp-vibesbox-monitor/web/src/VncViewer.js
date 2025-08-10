import React, { useEffect, useRef, useState } from 'react';

const VncViewer = ({ onStatusChange, wsUrl }) => {
  const containerRef = useRef(null);
  const rfbRef = useRef(null);
  const [status, setStatus] = useState('Initializing...');
  const [isConnecting, setIsConnecting] = useState(false);
  const [novncReady, setNovncReady] = useState(false);
  const [hasAutoConnected, setHasAutoConnected] = useState(false);

  const updateStatus = (newStatus) => {
    setStatus(newStatus);
    if (onStatusChange) {
      const externalStatus = newStatus.toLowerCase().includes('connected') ? 'connected' : 'disconnected';
      onStatusChange(externalStatus);
    }
  };

  const buildWebSocketUrl = (relativePath) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const cleanPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
    return `${protocol}//${host}${cleanPath}`;
  };

  // Force noVNC to apply scaling and remove overflow
  const forceVncScaling = () => {
    if (!rfbRef.current) return;
    
    console.log('🎯 Forcing VNC scaling...');
    
    // Force noVNC to recalculate viewport scaling
    try {
      rfbRef.current.scaleViewport = true;
      rfbRef.current.clipViewport = true;
      
      // Remove overflow: auto from noVNC's internal containers
      const vncContainer = containerRef.current;
      if (vncContainer) {
        const overflowDivs = vncContainer.querySelectorAll('div[style*="overflow: auto"]');
        overflowDivs.forEach(div => {
          console.log('🚫 Removing overflow: auto from noVNC container');
          div.style.overflow = 'hidden';
        });
        
        // Force canvas to fit container size
        const canvas = vncContainer.querySelector('canvas');
        if (canvas) {
          console.log('📐 Canvas current size:', canvas.style.width, 'x', canvas.style.height);
          console.log('📐 Container size:', vncContainer.offsetWidth, 'x', vncContainer.offsetHeight);
          
          // Calculate proper scaling
          const containerWidth = vncContainer.offsetWidth;
          const containerHeight = vncContainer.offsetHeight;
          const canvasRatio = 1920 / 1080; // VNC aspect ratio
          const containerRatio = containerWidth / containerHeight;
          
          let scaledWidth, scaledHeight;
          if (containerRatio > canvasRatio) {
            // Container is wider - fit to height
            scaledHeight = containerHeight;
            scaledWidth = scaledHeight * canvasRatio;
          } else {
            // Container is taller - fit to width  
            scaledWidth = containerWidth;
            scaledHeight = scaledWidth / canvasRatio;
          }
          
          console.log('🎯 Scaling canvas to:', scaledWidth, 'x', scaledHeight);
          canvas.style.width = `${scaledWidth}px`;
          canvas.style.height = `${scaledHeight}px`;
        }
      }
    } catch (error) {
      console.error('❌ Error forcing VNC scaling:', error);
    }
  };

  const handleResize = () => {
    console.log('🔄 Window resized, re-applying VNC scaling...');
    setTimeout(forceVncScaling, 100);
  };

  const connectToVNC = () => {
    console.log('VNC Connect attempt started...');
    
    if (isConnecting || rfbRef.current) {
      console.log('Already connecting/connected, ignoring request');
      return;
    }

    if (!novncReady || !window.RFB || !containerRef.current) {
      updateStatus('noVNC library not ready');
      console.error('Prerequisites not met for VNC connection');
      return;
    }

    setIsConnecting(true);
    updateStatus('Connecting to VNC...');

    try {
      const fullWsUrl = buildWebSocketUrl(wsUrl);
      console.log('Creating RFB instance with URL:', fullWsUrl);

      // Create RFB with scaling options
      rfbRef.current = new window.RFB(containerRef.current, fullWsUrl, {
        credentials: { password: '' },
        scaleViewport: true,
        clipViewport: true,
        resizeSession: false
      });

      rfbRef.current.addEventListener('connect', () => {
        console.log('✅ VNC connected successfully');
        updateStatus('Connected');
        setIsConnecting(false);
        
        // CRITICAL: Force scaling after connection established
        setTimeout(() => {
          forceVncScaling();
          window.addEventListener('resize', handleResize);
        }, 1000);
      });

      rfbRef.current.addEventListener('disconnect', (e) => {
        console.log('❌ VNC disconnected:', e.detail);
        const reason = e.detail?.clean ? 'Clean disconnect' : 'Connection lost';
        updateStatus(`Disconnected - ${reason}`);
        setIsConnecting(false);
        rfbRef.current = null;
        window.removeEventListener('resize', handleResize);
        
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
        console.log('VNC credentials required');
        updateStatus('Authentication required');
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
    window.removeEventListener('resize', handleResize);
  };

  useEffect(() => {
    const handleNovncReady = () => {
      console.log('noVNC ready event received');
      setNovncReady(true);
      updateStatus('noVNC loaded, ready to connect');
    };

    if (window.RFB) {
      handleNovncReady();
    } else {
      window.addEventListener('novnc-ready', handleNovncReady);
      return () => window.removeEventListener('novnc-ready', handleNovncReady);
    }
  }, []);

  useEffect(() => {
    if (novncReady && containerRef.current && !hasAutoConnected && !rfbRef.current) {
      console.log('Conditions met, starting auto-connect');
      setHasAutoConnected(true);
      const timer = setTimeout(connectToVNC, 1000);
      return () => clearTimeout(timer);
    }
  }, [novncReady]);

  useEffect(() => {
    return () => {
      if (rfbRef.current) {
        rfbRef.current.disconnect();
      }
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#1a1a1a',
      border: '1px solid #444',
      overflow: 'hidden'
    }}>
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#2a2a2a', 
        color: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexShrink: 0
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
          {rfbRef.current && (
            <button 
              onClick={forceVncScaling}
              style={{ 
                marginLeft: '10px',
                padding: '5px 10px',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              Force Scale
            </button>
          )}
        </div>
      </div>
      
      <div style={{ 
        flex: 1, 
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 0
      }}>
        <div 
          ref={containerRef}
          style={{ 
            width: '100%',
            height: '100%',
            backgroundColor: '#000',
            border: 'none',
            overflow: 'hidden'
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
              <>📺 Click Connect to view desktop<br/>🎯 Fixed scaling enabled</>
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
