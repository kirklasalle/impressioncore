document.addEventListener('DOMContentLoaded', function () {
    // --- Terminal Setup --- 
    const terminalPopup = document.getElementById('terminal-popup');
    const terminalContainer = document.getElementById('terminal-container');
    const toggleTerminalButton = document.getElementById('toggle-terminal-btn');
    const closeTerminalButton = document.getElementById('terminal-close-btn');
    let term; // Terminal instance
    let ws; // WebSocket instance
    let fitAddon; // For proper terminal sizing
    let searchAddon; // For searching text in terminal
    let webLinksAddon; // For clickable links
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_INTERVAL = 3000;

    // Terminal context menu for copy/paste
    const contextMenu = document.createElement('div');
    contextMenu.className = 'terminal-context-menu';
    contextMenu.style.cssText = 
        'position:absolute;' +
        'z-index:3000;' +
        'background:#23272b;' +
        'border:1px solid #343a40;' +
        'border-radius:3px;' +
        'padding:5px 0;' +
        'min-width:150px;' +
        'display:none;' +
        'box-shadow: 0 2px 8px rgba(0,0,0,0.2);';
    document.body.appendChild(contextMenu);
    
    const copyOption = document.createElement('div');
    copyOption.innerHTML = '<i class="fas fa-copy mr-2"></i> Copy';
    copyOption.style.cssText = 
        'padding:8px 15px;' +
        'cursor:pointer;' +
        'color:#fff;' +
        'transition:background 0.2s;';
    copyOption.onmouseover = function() { this.style.background = '#2563eb'; };
    copyOption.onmouseout = function() { this.style.background = 'transparent'; };
    
    const pasteOption = document.createElement('div');
    pasteOption.innerHTML = '<i class="fas fa-paste mr-2"></i> Paste';
    pasteOption.style.cssText = 
        'padding:8px 15px;' +
        'cursor:pointer;' +
        'color:#fff;' +
        'transition:background 0.2s;' +
        'border-top:1px solid #343a40;';
    pasteOption.onmouseover = function() { this.style.background = '#2563eb'; };
    pasteOption.onmouseout = function() { this.style.background = 'transparent'; };
    
    contextMenu.appendChild(copyOption);
    contextMenu.appendChild(pasteOption);

    function initializeTerminal() {
        if (term) return; // Already initialized

        // Create terminal with better options
        term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#1a1f2e',
                foreground: '#ffffff',
                cursor: '#ffffff',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#000000',
                red: '#e06c75',
                green: '#98c379',
                yellow: '#d19a66',
                blue: '#61afef',
                magenta: '#c678dd',
                cyan: '#56b6c2',
                white: '#abb2bf'
            },
            fontFamily: 'Consolas, "Courier New", monospace',
            fontSize: 14,
            lineHeight: 1.2,
            allowTransparency: true,
            convertEol: true,
            scrollback: 10000, // Large scrollback for history
            cursorStyle: 'block'
        });
        
        // Initialize add-ons
        fitAddon = new FitAddon.FitAddon();
        searchAddon = new SearchAddon.SearchAddon();
        webLinksAddon = new WebLinksAddon.WebLinksAddon();
        
        // Load add-ons
        term.loadAddon(fitAddon);
        term.loadAddon(searchAddon);
        term.loadAddon(webLinksAddon);
        
        term.open(terminalContainer);
        fitAddon.fit(); // Adjust terminal to container size
        
        term.write('\x1b[1;34m====================================\r\n');
        term.write('\x1b[1;32mImpressionCore Terminal\x1b[0m\r\n');
        term.write('\x1b[1;34m====================================\x1b[0m\r\n\r\n');
        term.write('Right-click for copy/paste options\r\n');
        term.write('Type \x1b[1;33mhelp\x1b[0m for available commands\r\n\r\n');
        
        connectWebSocket();
        
        // Resize event for the terminal
        window.addEventListener('resize', () => {
            if (terminalPopup.classList.contains('visible')) {
                fitAddon.fit();
                // Send terminal resize info to server if needed
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'resize',
                        cols: term.cols,
                        rows: term.rows
                    }));
                }
            }
        });
        
        // Handle user input
        term.onData(data => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(data);
            } else {
                term.write('\r\n\x1b[31mNot connected to server. Attempting to reconnect...\x1b[0m\r\n');
                connectWebSocket();
            }
        });
        
        // Handle selection for copy/paste
        term.attachCustomKeyEventHandler((event) => {
            // Handle Ctrl+C for copy
            if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
                if (term.hasSelection()) {
                    const selection = term.getSelection();
                    navigator.clipboard.writeText(selection).then(() => {
                        term.write('\r\n\x1b[90mCopied to clipboard\x1b[0m\r\n');
                    }).catch(err => {
                        console.error('Could not copy text: ', err);
                    });
                    return false; // Prevent default
                }
                return true;
            }
            
            // Handle Ctrl+V for paste
            if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
                navigator.clipboard.readText().then(text => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(text);
                    }
                }).catch(err => {
                    console.error('Could not paste text: ', err);
                });
                return false; // Prevent default
            }
            
            // Allow all other key events
            return true;
        });
        
        // Right-click context menu
        terminalContainer.addEventListener('contextmenu', (event) => {
            event.preventDefault();
            const hasSelection = term.hasSelection();
            copyOption.style.opacity = hasSelection ? '1' : '0.5';
            copyOption.style.cursor = hasSelection ? 'pointer' : 'not-allowed';
            
            contextMenu.style.left = `${event.pageX}px`;
            contextMenu.style.top = `${event.pageY}px`;
            contextMenu.style.display = 'block';
        });
        
        // Handle copy from context menu
        copyOption.addEventListener('click', () => {
            if (!term.hasSelection()) return;
            
            const selection = term.getSelection();
            navigator.clipboard.writeText(selection).then(() => {
                term.write('\r\n\x1b[90mCopied to clipboard\x1b[0m\r\n');
            }).catch(err => {
                console.error('Could not copy text: ', err);
            });
            
            contextMenu.style.display = 'none';
        });
        
        // Handle paste from context menu
        pasteOption.addEventListener('click', () => {
            navigator.clipboard.readText().then(text => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(text);
                }
            }).catch(err => {
                console.error('Could not paste text: ', err);
            });
            
            contextMenu.style.display = 'none';
        });
        
        // Hide context menu when clicking elsewhere
        document.addEventListener('click', () => {
            contextMenu.style.display = 'none';
        });
    }
    
    function connectWebSocket() {
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            return; // Already connected or connecting
        }
        
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            term.write('\r\n\x1b[31mMax reconnect attempts reached. Please reload the page.\x1b[0m\r\n');
            return;
        }
        
        reconnectAttempts++;
        term.write(`\r\nConnecting to WebSocket (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...\r\n`);
        
        try {
            // Use secure WebSocket (wss://) if the page is served over HTTPS
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws/terminal`);
            
            ws.onopen = function(event) {
                term.write('\x1b[32mWebSocket connection established!\x1b[0m\r\n');
                reconnectAttempts = 0; // Reset reconnect counter on successful connection
                
                // Send terminal size on connection
                ws.send(JSON.stringify({
                    type: 'resize',
                    cols: term.cols,
                    rows: term.rows
                }));
            };
            
            ws.onmessage = function(event) {
                // Handle message from server
                try {
                    const data = event.data;
                    // Check if it's a JSON control message or raw terminal output
                    if (data.startsWith('{') && data.endsWith('}')) {
                        try {
                            const jsonData = JSON.parse(data);
                            if (jsonData.type === 'error') {
                                term.write(`\x1b[31mError: ${jsonData.message}\x1b[0m\r\n`);
                            } else if (jsonData.type === 'info') {
                                term.write(`\x1b[34m${jsonData.message}\x1b[0m\r\n`);
                            }
                        } catch (e) {
                            // Not valid JSON, treat as raw terminal data
                            term.write(data);
                        }
                    } else {
                        // Raw terminal output
                        term.write(data);
                    }
                } catch (error) {
                    console.error('Error handling WebSocket message:', error);
                    term.write('\x1b[31mError processing server response\x1b[0m\r\n');
                }
            };
            
            ws.onerror = function(event) {
                term.write('\x1b[31mWebSocket connection error\x1b[0m\r\n');
                console.error('WebSocket Error:', event);
                ws = null;
            };
            
            ws.onclose = function(event) {
                const msg = event.wasClean ? 
                    '\x1b[33mWebSocket connection closed cleanly\x1b[0m\r\n' : 
                    '\x1b[31mWebSocket connection lost\x1b[0m\r\n';
                term.write(msg);
                ws = null;
                
                // Attempt to reconnect after delay if we haven't reached max attempts
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    term.write(`\x1b[33mReconnecting in ${RECONNECT_INTERVAL/1000} seconds...\x1b[0m\r\n`);
                    setTimeout(connectWebSocket, RECONNECT_INTERVAL);
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            term.write('\x1b[31mFailed to create WebSocket connection\x1b[0m\r\n');
            
            // Try again after delay
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                term.write(`\x1b[33mRetrying in ${RECONNECT_INTERVAL/1000} seconds...\x1b[0m\r\n`);
                setTimeout(connectWebSocket, RECONNECT_INTERVAL);
            }
        }
    }
    
    // --- Global function to send terminal commands ---
    window.sendTerminalCommand = function(command) {
        if (!terminalPopup.classList.contains('visible')) {
            toggleTerminal(); // Show terminal if hidden
        }
        
        if (!term) {
            initializeTerminal();
        }
        
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(command + '\r'); 
            term.focus();
        } else {
            term.write(`\x1b[31mNot connected. Cannot send command: ${command}\x1b[0m\r\n`);
            connectWebSocket(); // Try to reconnect
        }
    };
    
    function toggleTerminal() {
        terminalPopup.classList.toggle('visible');
        if (terminalPopup.classList.contains('visible')) {
            if (!term) {
                initializeTerminal(); // Initialize on first open
            } else {
                fitAddon.fit(); // Resize terminal if already initialized
            }
            term.focus();
        }
    }
    
    toggleTerminalButton.addEventListener('click', toggleTerminal);
    closeTerminalButton.addEventListener('click', toggleTerminal);
    
    // Support keyboard shortcut (Ctrl+`) to toggle terminal
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === '`') {
            e.preventDefault();
            toggleTerminal();
        }
    });
});
