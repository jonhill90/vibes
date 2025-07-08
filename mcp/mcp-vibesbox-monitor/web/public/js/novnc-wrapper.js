// Simple RFB class for testing VNC connection
console.log('Loading noVNC wrapper...');

window.RFB = class RFB {
    constructor(target, url, options = {}) {
        console.log('RFB constructor called:', { target, url, options });
        this.target = target;
        this.url = url;
        this.options = options;
        this._events = {};
        
        // Simulate connection attempt
        setTimeout(() => {
            console.log('Attempting VNC connection to:', url);
            this._connect();
        }, 1000);
    }
    
    _connect() {
        // Try to establish WebSocket connection to VNC proxy
        try {
            const wsUrl = this.url.replace('http:', 'ws:').replace('https:', 'wss:');
            console.log('Connecting to WebSocket:', wsUrl);
            
            this._socket = new WebSocket(wsUrl);
            
            this._socket.onopen = () => {
                console.log('WebSocket connected to VNC proxy');
                this._fireEvent('connect');
            };
            
            this._socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this._fireEvent('disconnect', { detail: { clean: false } });
            };
            
            this._socket.onclose = () => {
                console.log('WebSocket closed');
                this._fireEvent('disconnect', { detail: { clean: true } });
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this._fireEvent('disconnect', { detail: { clean: false } });
        }
    }
    
    addEventListener(event, handler) {
        console.log('RFB addEventListener:', event);
        if (!this._events[event]) this._events[event] = [];
        this._events[event].push(handler);
    }
    
    _fireEvent(event, data = {}) {
        console.log('RFB firing event:', event, data);
        if (this._events[event]) {
            this._events[event].forEach(handler => handler(data));
        }
    }
    
    disconnect() {
        console.log('RFB disconnect called');
        if (this._socket) {
            this._socket.close();
        }
        this._fireEvent('disconnect', { detail: { clean: true } });
    }
};

console.log('window.RFB is now available:', window.RFB);
