class RealtimeDemo {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.isMuted = false;
        this.isCapturing = false;
        this.debugMode = false;
        this.captureAudioContext = null;
        this.processor = null;
        this.stream = null;
        this.sessionId = this.generateSessionId();
        
        this.audioQueue = [];
        this.isPlayingAudio = false;
        this.currentAudioSource = null;
        this.audioContext = null;
        this.analyser = null;
        this.gainNode = null;
        this.compressor = null;
        this.amplitudeLevels = new Array(5).fill(0);
        this.amplitudeInterval = null;
        this.audioVisualizationEnabled = !this.isSafari();
        
        // Audio playback speed control (0.5 = half speed, 1.0 = normal, 2.0 = double speed)
        this.playbackSpeed = 0.95; // 95% of normal speed - slightly slower but still natural
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.connectBtn = document.getElementById('connectBtn');
        this.micBtn = document.getElementById('micBtn');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.debugToggle = document.getElementById('debugToggle');
        this.debugPanel = document.getElementById('debugPanel');
        this.eventsContent = document.getElementById('eventsContent');
        this.toolsContent = document.getElementById('toolsContent');
        
        // User info elements
        this.userEmailElement = document.getElementById('userEmail');
    }
    
    setupEventListeners() {
        if (this.connectBtn) {
            this.connectBtn.addEventListener('click', () => {
                if (this.isConnected) {
                    this.disconnect();
                } else {
                    this.connect();
                }
            });
        }
        
        if (this.micBtn) {
            this.micBtn.addEventListener('click', () => {
                this.toggleMute();
            });
        }
        
        if (this.debugToggle) {
            this.debugToggle.addEventListener('change', () => {
                this.toggleDebugMode();
            });
        }
        
        // Setup debug toggle listener when navigation loads
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => this.setupDebugToggleListener(), 1000);
        });
        
        // Also setup a MutationObserver to detect when debug toggle is added
        this.observeDebugToggle();
    }
    
    observeDebugToggle() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if the debug toggle was added
                        if (node.id === 'debugToggle' || node.querySelector && node.querySelector('#debugToggle')) {
                            console.log('Debug toggle detected in DOM, setting up listener');
                            setTimeout(() => this.setupDebugToggleListener(), 100);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    setupDebugToggleListener() {
        const debugToggle = document.getElementById('debugToggle');
        if (debugToggle && !debugToggle.hasEventListener) {
            console.log('Setting up debug toggle listener');
            debugToggle.addEventListener('change', () => {
                console.log('Debug toggle changed');
                this.toggleDebugMode();
            });
            debugToggle.hasEventListener = true;
        } else if (!debugToggle) {
            console.log('Debug toggle not found, will retry...');
            // Retry after navigation loads
            setTimeout(() => this.setupDebugToggleListener(), 1000);
        }
    }
    
    submitEmployeeId() {
        const employeeId = this.employeeIdInput.value.trim();
        
        if (!employeeId) {
            this.showEmployeeStatus('Please enter an Employee ID', 'error');
            return;
        }
        
        // Basic validation - alphanumeric only, max 10 chars
        if (!/^[a-zA-Z0-9]+$/.test(employeeId)) {
            this.showEmployeeStatus('Employee ID must contain only letters and numbers', 'error');
            return;
        }
        
        this.employeeId = employeeId;
        this.isEmployeeSubmitted = true;
        
        // Update UI
        this.employeeIdInput.disabled = true;
        this.submitEmployeeBtn.disabled = true;
        this.submitEmployeeBtn.textContent = 'Submitted';
        
        // Show success status
        this.showEmployeeStatus(`Employee ID: ${employeeId} submitted successfully`, 'success');
        
        // Enable connect button and update instructions
        this.connectBtn.disabled = false;
        this.preConnectInstructions.style.display = 'none';
        this.postSubmitInstructions.style.display = 'block';
    }
    
    showEmployeeStatus(message, type) {
        // Remove any existing status
        const existingStatus = document.querySelector('.employee-status');
        if (existingStatus) {
            existingStatus.remove();
        }
        
        // Create new status element
        const statusDiv = document.createElement('div');
        statusDiv.className = `employee-status ${type}`;
        statusDiv.innerHTML = `
            <div class="employee-status-icon"></div>
            <span>${message}</span>
        `;
        
        // Insert after the form
        const form = document.querySelector('.employee-id-form');
        form.parentNode.insertBefore(statusDiv, form.nextSibling);
        
        // Remove error status after 5 seconds
        if (type === 'error') {
            setTimeout(() => {
                statusDiv.remove();
            }, 5000);
        }
    }
    
    toggleDebugMode() {
        // Get current state of debug toggle since it's loaded dynamically
        const debugToggle = document.getElementById('debugToggle');
        const debugPanel = document.getElementById('debugPanel');
        
        if (debugToggle) {
            this.debugMode = debugToggle.checked;
            console.log('Debug mode toggled:', this.debugMode);
            
            if (debugPanel) {
                debugPanel.classList.toggle('active', this.debugMode);
            }
        }
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    async connect() {
        try {
            // Start interview session with authenticated user
            const response = await fetch('/api/start-interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Failed to start interview session');
            }
            
            const sessionData = await response.json();
            this.sessionId = sessionData.session_id;
            
            // Clear empty state
            this.clearEmptyState();
            
            // Use current location for WebSocket to support different environments
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsHost = window.location.host || 'localhost:8002';
            this.ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/${this.sessionId}`);
            
            this.ws.onopen = () => {
                console.log('WebSocket connection opened');
                this.isConnected = true;
                this.updateUI();
                
                // User email is already set on the server side
                this.startAudioCapture();
            };
            
            this.ws.onmessage = (event) => {
                console.log('WebSocket message received:', event.data);
                try {
                    const data = JSON.parse(event.data);
                    this.handleRealtimeEvent(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket connection closed');
                this.isConnected = false;
                this.updateUI();
                this.stopAudioCapture();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addMessage('assistant', 'Connection error occurred. Please try again.');
            };
            
        } catch (error) {
            console.error('Connection failed:', error);
            this.addMessage('assistant', 'Failed to connect. Please check your connection.');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        this.stopAudioCapture();
        this.stopAudioPlayback(); // Clean up audio playback
        this.isConnected = false;
        this.updateUI();
    }
    
    updateUI() {
        // Update connection status
        this.connectBtn.textContent = this.isConnected ? 'Disconnect' : 'Connect';
        if (this.isConnected) {
            this.connectBtn.classList.remove('primary');
            this.connectBtn.classList.add('secondary');
        } else {
            this.connectBtn.classList.remove('secondary');
            this.connectBtn.classList.add('primary');
        }
        
        // Update microphone button
        this.micBtn.disabled = !this.isConnected;
        this.micBtn.classList.toggle('listening', this.isCapturing && !this.isMuted);
        
        // Update mic button text
        const micStatusSpan = this.micBtn.querySelector('.mic-button-content span:last-child');
        if (micStatusSpan) {
            if (this.isConnected) {
                micStatusSpan.textContent = this.isMuted ? 'Muted' : 'Listening';
            } else {
                micStatusSpan.textContent = 'Disconnected';
            }
        }
    }
    
    clearEmptyState() {
        // Remove welcome content
        const emptyState = this.messagesContainer.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        // Reset container styles for chat layout
        this.messagesContainer.style.display = '';
        this.messagesContainer.style.flexDirection = '';
        this.messagesContainer.style.alignItems = '';
        this.messagesContainer.style.justifyContent = '';
        this.messagesContainer.style.textAlign = '';
        this.messagesContainer.style.padding = '';
        this.messagesContainer.style.color = '';
    }
    
    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Add avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = type === 'user' ? 'U' : 'A';
        
        // Add content wrapper
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;
        
        contentDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    isSafari() {
        return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    }
    
    setPlaybackSpeed(speed) {
        // Allow setting playback speed between 0.25x (very slow) and 2.0x (fast)
        this.playbackSpeed = Math.max(0.25, Math.min(2.0, speed));
        console.log(`Playback speed set to: ${this.playbackSpeed}x`);
        
        // If audio is currently playing, update its speed
        if (this.currentAudioSource && this.isPlayingAudio) {
            this.currentAudioSource.playbackRate.value = this.playbackSpeed;
        }
    }
    
    async startAudioCapture() {
        console.log('Starting audio capture...');
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 24000,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            console.log('Audio stream obtained successfully');
            
            this.captureAudioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 24000
            });
            
            const source = this.captureAudioContext.createMediaStreamSource(this.stream);
            this.processor = this.captureAudioContext.createScriptProcessor(4096, 1, 1);
            
            this.processor.onaudioprocess = (event) => {
                if (!this.isMuted && this.isConnected) {
                    const inputData = event.inputBuffer.getChannelData(0);
                    const int16Data = new Int16Array(inputData.length);
                    
                    for (let i = 0; i < inputData.length; i++) {
                        int16Data[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
                    }
                    
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            type: 'audio',
                            data: Array.from(int16Data)
                        }));
                    }
                }
            };
            
            source.connect(this.processor);
            this.processor.connect(this.captureAudioContext.destination);
            this.isCapturing = true;
            this.updateUI();
            
        } catch (error) {
            console.error('Failed to start audio capture:', error);
            this.addMessage('assistant', 'Microphone access denied. Please allow microphone access and try again.');
            // If audio fails, disconnect the WebSocket
            this.disconnect();
        }
    }
    
    stopAudioCapture() {
        if (this.processor) {
            this.processor.disconnect();
            this.processor = null;
        }
        
        if (this.captureAudioContext) {
            this.captureAudioContext.close();
            this.captureAudioContext = null;
        }
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.isCapturing = false;
        this.updateUI();
    }
    
    toggleMute() {
        this.isMuted = !this.isMuted;
        this.updateUI();
    }
    
    handleRealtimeEvent(event) {
        // Add to raw events pane
        this.addRawEvent(event);
        
        // Add to tools panel if it's a tool or handoff event
        if (event.type === 'tool_start' || event.type === 'tool_end' || event.type === 'handoff') {
            this.addToolEvent(event);
        }
        
        // Handle specific events for the main interface
        switch (event.type) {
            case 'history_updated':
                console.log('Handling history update:', event.history); // Debug log
                this.updateMessagesFromHistory(event.history);
                break;
            case 'audio':
                console.log('Handling audio data - length:', event.audio?.length || 0); // Debug log
                this.playAudio(event.audio);
                break;
            case 'audio_interrupted':
                console.log('Audio interrupted - stopping current playback');
                this.stopAudioPlayback();
                break;
            case 'audio_end':
                console.log('Audio stream ended');
                // Don't stop audio here as it might still be playing buffered audio
                break;
            case 'tool_start':
            case 'tool_end':
            case 'handoff':
                if (this.debugMode) {
                    this.addToolEvent(event);
                }
                break;
            case 'error':
                console.log('Handling error:', event.error); // Debug log
                this.addMessage('assistant', `Error: ${event.error}`);
                break;
            default:
                console.log('Unhandled event type:', event.type); // Debug log
        }
    }
    
    updateMessagesFromHistory(history) {
        console.log('updateMessagesFromHistory called with:', history);
        
        // Clear all existing messages
        this.messagesContainer.innerHTML = '';
        
        // Add messages from history
        if (history && Array.isArray(history)) {
            console.log('Processing history array with', history.length, 'items');
            history.forEach((item, index) => {
                console.log(`History item ${index}:`, item);
                if (item.type === 'message') {
                    const role = item.role;
                    let content = '';
                    
                    console.log(`Message item - role: ${role}, content:`, item.content);
                    
                    if (item.content && Array.isArray(item.content)) {
                        // Extract text from content array
                        item.content.forEach(contentPart => {
                            console.log('Content part:', contentPart);
                            if (contentPart.type === 'text' && contentPart.text) {
                                content += contentPart.text;
                            } else if (contentPart.type === 'input_text' && contentPart.text) {
                                content += contentPart.text;
                            } else if (contentPart.type === 'input_audio' && contentPart.transcript) {
                                content += contentPart.transcript;
                            } else if (contentPart.type === 'audio' && contentPart.transcript) {
                                content += contentPart.transcript;
                            }
                        });
                    }
                    
                    console.log(`Final content for ${role}:`, content);
                    
                    if (content.trim()) {
                        this.addMessage(role, content.trim());
                        console.log(`Added message: ${role} - ${content.trim()}`);
                    }
                } else {
                    console.log(`Skipping non-message item of type: ${item.type}`);
                }
            });
        } else {
            console.log('History is not an array or is null/undefined');
        }
        
        this.scrollToBottom();
    }
    
    addRawEvent(event) {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'event';
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'event-header';
        headerDiv.innerHTML = `
            <span>${event.type}</span>
            <span>▼</span>
        `;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'event-content collapsed';
        contentDiv.textContent = JSON.stringify(event, null, 2);
        
        headerDiv.addEventListener('click', () => {
            const isCollapsed = contentDiv.classList.contains('collapsed');
            if (isCollapsed) {
                contentDiv.classList.remove('collapsed');
                contentDiv.classList.add('expanded');
                headerDiv.querySelector('span:last-child').textContent = '▲';
            } else {
                contentDiv.classList.add('collapsed');
                contentDiv.classList.remove('expanded');
                headerDiv.querySelector('span:last-child').textContent = '▼';
            }
        });
        
        eventDiv.appendChild(headerDiv);
        eventDiv.appendChild(contentDiv);
        this.eventsContent.appendChild(eventDiv);
        
        // Auto-scroll events pane
        this.eventsContent.scrollTop = this.eventsContent.scrollHeight;
    }
    
    addToolEvent(event) {
        const eventDiv = document.createElement('div');
        eventDiv.className = 'event';
        
        let title = '';
        let description = '';
        let eventClass = '';
        
        if (event.type === 'handoff') {
            title = `🔄 Handoff`;
            description = `From ${event.from} to ${event.to}`;
            eventClass = 'handoff';
        } else if (event.type === 'tool_start') {
            title = `🔧 Tool Started`;
            description = `Running ${event.tool}`;
            eventClass = 'tool';
        } else if (event.type === 'tool_end') {
            title = `✅ Tool Completed`;
            description = `${event.tool}: ${event.output || 'No output'}`;
            eventClass = 'tool';
        }
        
        eventDiv.innerHTML = `
            <div class="event-header ${eventClass}">
                <div>
                    <div style="font-weight: 600; margin-bottom: 2px;">${title}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">${description}</div>
                </div>
                <span style="font-size: 0.7rem; opacity: 0.6;">${new Date().toLocaleTimeString()}</span>
            </div>
        `;
        
        this.toolsContent.appendChild(eventDiv);
        
        // Auto-scroll tools pane
        this.toolsContent.scrollTop = this.toolsContent.scrollHeight;
    }
    
    async playAudio(audioBase64) {
        try {
            if (!audioBase64 || audioBase64.length === 0) {
                console.warn('Received empty audio data, skipping playback');
                return;
            }
            
            // Add to queue
            this.audioQueue.push(audioBase64);
            
            // Start processing queue if not already playing
            if (!this.isPlayingAudio) {
                this.processAudioQueue();
            }
            
        } catch (error) {
            console.error('Failed to play audio:', error);
        }
    }
    
    async processAudioQueue() {
        if (this.isPlayingAudio || this.audioQueue.length === 0) {
            return;
        }
        
        this.isPlayingAudio = true;
        
        // Initialize audio context if needed
        if (!this.playbackAudioContext) {
            this.playbackAudioContext = new AudioContext({ sampleRate: 24000 });
        }
        
        while (this.audioQueue.length > 0) {
            const audioBase64 = this.audioQueue.shift();
            await this.playAudioChunk(audioBase64);
        }
        
        this.isPlayingAudio = false;
    }
    
    async playAudioChunk(audioBase64) {
        return new Promise((resolve, reject) => {
            try {
                // Decode base64 to ArrayBuffer
                const binaryString = atob(audioBase64);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                
                const int16Array = new Int16Array(bytes.buffer);
                
                if (int16Array.length === 0) {
                    console.warn('Audio chunk has no samples, skipping');
                    resolve();
                    return;
                }
                
                const float32Array = new Float32Array(int16Array.length);
                
                // Convert int16 to float32
                for (let i = 0; i < int16Array.length; i++) {
                    float32Array[i] = int16Array[i] / 32768.0;
                }
                
                const audioBuffer = this.playbackAudioContext.createBuffer(1, float32Array.length, 24000);
                audioBuffer.getChannelData(0).set(float32Array);
                
                const source = this.playbackAudioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(this.playbackAudioContext.destination);
                
                // Store reference to current source
                this.currentAudioSource = source;
                
                source.onended = () => {
                    this.currentAudioSource = null;
                    resolve();
                };
                source.start();
                
            } catch (error) {
                console.error('Failed to play audio chunk:', error);
                reject(error);
            }
        });
    }
    
    stopAudioPlayback() {
        console.log('Stopping audio playback due to interruption');
        
        // Stop current audio source if playing
        if (this.currentAudioSource) {
            try {
                this.currentAudioSource.stop();
                this.currentAudioSource = null;
            } catch (error) {
                console.error('Error stopping audio source:', error);
            }
        }
        
        // Clear the audio queue
        this.audioQueue = [];
        
        // Reset playback state
        this.isPlayingAudio = false;
        
        console.log('Audio playback stopped and queue cleared');
    }
}

// Initialize the demo when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeDemo = new RealtimeDemo();
});