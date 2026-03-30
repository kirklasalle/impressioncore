document.addEventListener("DOMContentLoaded", () => {
    const initButton = document.getElementById('init-model-btn');
    const terminal = document.getElementById('init-terminal');

    if (initButton && terminal) {
        initButton.addEventListener('click', () => {
            terminal.style.display = 'block';
            terminal.innerHTML = '<div class="term-line">Starting initialization...</div>';

            const ws = new WebSocket(`ws://${location.host}/ws/init`);

            ws.onmessage = (event) => {
                const isError = event.data.startsWith('ERR:');
                const isSystem = event.data.startsWith('[System]');
                const cssClass = isError ? 'term-error' : isSystem ? 'term-system' : '';

                terminal.innerHTML += `
                    <div class="term-line">
                        <span class="term-prompt">${isError ? '!' : '$'}></span>
                        <span class="term-output ${cssClass}">${event.data}</span>
                    </div>`;
                terminal.scrollTop = terminal.scrollHeight;
            };

            ws.onerror = (error) => {
                terminal.innerHTML += `
                    <div class="term-line">
                        <span class="term-error">
                            Connection error: ${error.message || 'Unknown error'}
                        </span>
                    </div>`;
                terminal.scrollTop = terminal.scrollHeight;
            };

            ws.onclose = () => {
                if (!terminal.innerHTML.includes('[System]')) {
                    terminal.innerHTML += `
                        <div class="term-line">
                            <span class="term-system">Connection closed</span>
                        </div>`;
                    terminal.scrollTop = terminal.scrollHeight;
                }
            };
        });
    } else {
        console.error('Initialize Model button or terminal container not found');
    }
});

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
    #init-terminal {
        display: none;
        height: 300px;
        background: #1e1e1e;
        color: #d4d4d4;
        font-family: monospace;
        padding: 10px;
        margin: 10px 0;
        overflow-y: auto;
        border-radius: 4px;
    }
    .term-line {
        margin: 2px 0;
        line-height: 1.4;
    }
    .term-prompt {
        color: #569cd6;
        margin-right: 8px;
    }
    .term-error {
        color: #f14c4c;
    }
    .term-system {
        color: #4ec9b0;
    }
    .term-output {
        white-space: pre-wrap;
        word-break: break-word;
    }
`;
document.head.appendChild(style);