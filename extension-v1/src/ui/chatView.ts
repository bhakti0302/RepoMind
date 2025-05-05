import * as vscode from 'vscode';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'extension-v1.chatView';
    
    constructor(private readonly _extensionUri: vscode.Uri) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(message => {
            if (message.command === 'sendMessage') {
                this._handleUserMessage(webviewView.webview, message.text);
            }
        });
    }
    
    private _handleUserMessage(webview: vscode.Webview, text: string) {
        // Echo the message back for now
        setTimeout(() => {
            webview.postMessage({
                command: 'addMessage',
                text: `You said: ${text}`,
                isUser: false
            });
        }, 500);
    }
    
    private _getHtmlForWebview(webview: vscode.Webview): string {
        const stylesUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css')
        );
        
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RepoMind</title>
            <link href="${stylesUri}" rel="stylesheet">
        </head>
        <body>
            <div id="chat-container">
                <div class="welcome-message">
                    <h2>Welcome to RepoMind</h2>
                    <p>I can help you with coding tasks, answer questions, and generate code based on your requirements.</p>
                    <p>Try asking about:</p>
                    <ul>
                        <li>Code implementation</li>
                        <li>Debugging help</li>
                        <li>Best practices</li>
                    </ul>
                </div>
                <div id="message-history"></div>
            </div>
            <div class="input-container">
                <textarea id="message-input" placeholder="Type your message here..."></textarea>
                <button id="send-button">Send</button>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                const messageHistory = document.getElementById('message-history');
                const messageInput = document.getElementById('message-input');
                const sendButton = document.getElementById('send-button');
                
                // Send message when button is clicked
                sendButton.addEventListener('click', sendMessage);
                
                // Send message when Enter key is pressed (but allow Shift+Enter for new lines)
                messageInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                // Handle messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'addMessage') {
                        addMessage(message.text, message.isUser === true);
                    }
                });
                
                function sendMessage() {
                    const text = messageInput.value.trim();
                    if (text) {
                        // Add message to UI
                        addMessage(text, true);
                        
                        // Send message to extension
                        vscode.postMessage({
                            command: 'sendMessage',
                            text: text
                        });
                        
                        // Clear input
                        messageInput.value = '';
                    }
                }
                
                function addMessage(text, isUser) {
                    const messageElement = document.createElement('div');
                    messageElement.className = isUser ? 'user-message' : 'assistant-message';
                    messageElement.textContent = text;
                    messageHistory.appendChild(messageElement);
                    
                    // Scroll to bottom
                    messageHistory.scrollTop = messageHistory.scrollHeight;
                }
            </script>
        </body>
        </html>`;
    }
}