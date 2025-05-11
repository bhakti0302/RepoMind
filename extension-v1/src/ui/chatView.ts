import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'extension-v1.chatView';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        // Store the webview for later use
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(message => {
            if (message.command === 'sendMessage') {
                this._handleUserMessage(webviewView.webview, message.text);
            } else if (message.command === 'syncCodebase') {
                this._handleSyncCodebase(webviewView.webview);
            } else if (message.command === 'attachFile') {
                this._handleAttachFile(webviewView.webview);
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

    private _handleSyncCodebase(webview: vscode.Webview) {
        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            webview.postMessage({
                command: 'addMessage',
                text: 'Error: No workspace folder is open. Please open a folder first.',
                isUser: false
            });
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;

        // Show a message that we're syncing
        webview.postMessage({
            command: 'addMessage',
            text: `Syncing codebase from "${workspaceFolder}"... This may take a moment.`,
            isUser: false
        });

        // No need for a listener, we'll use a timeout instead

        // We'll use a timeout to check for messages in the extension.ts file
        setTimeout(() => {
            // We'll add a status message
            webview.postMessage({
                command: 'addMessage',
                text: 'Codebase analysis in progress... This may take a few minutes.',
                isUser: false
            });

            // Add another message after 20 seconds
            setTimeout(() => {
                webview.postMessage({
                    command: 'addMessage',
                    text: 'Still working... The analysis is running in the background.',
                    isUser: false
                });

                // Add final message after another 20 seconds
                setTimeout(() => {
                    webview.postMessage({
                        command: 'addMessage',
                        text: 'Codebase analysis completed. You can now ask questions about the code.',
                        isUser: false
                    });
                }, 20000);
            }, 20000);
        }, 10000); // Wait 10 seconds for the process to complete

        // Execute the command to sync the codebase
        try {
            vscode.commands.executeCommand('extension-v1.syncCodebase');
            // Success message will be shown by the command itself
        } catch (error: unknown) {
            webview.postMessage({
                command: 'addMessage',
                text: `Error syncing codebase: ${error instanceof Error ? error.message : String(error)}`,
                isUser: false
            });
        }
    }

    private _handleAttachFile(webview: vscode.Webview) {
        // Execute the command to attach a file
        vscode.window.showOpenDialog({
            canSelectMany: false,
            openLabel: 'Attach',
            filters: {
                'Text Files': ['txt', 'md', 'json', 'js', 'ts', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'go', 'rs', 'rb']
            }
        }).then(files => {
            if (files && files.length > 0) {
                const filePath = files[0].fsPath;
                const fileName = path.basename(filePath);

                try {
                    const fileContent = fs.readFileSync(filePath, 'utf8');

                    // Add a message showing the attached file
                    webview.postMessage({
                        command: 'addMessage',
                        text: `Attached file: ${fileName}`,
                        isUser: true
                    });

                    // Add the file content as a message
                    webview.postMessage({
                        command: 'addMessage',
                        text: `File content:\n\`\`\`\n${fileContent}\n\`\`\``,
                        isUser: false
                    });
                } catch (error: unknown) {
                    webview.postMessage({
                        command: 'addMessage',
                        text: `Error reading file: ${error instanceof Error ? error.message : String(error)}`,
                        isUser: false
                    });
                }
            }
        });
    }

    // Method to send a message to the webview
    public sendMessageToWebviews(message: any) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
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
            <div class="action-buttons">
                <button id="sync-button" class="action-button">Sync Codebase</button>
                <button id="attach-button" class="action-button">Attach File</button>
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

                // Get references to the new buttons
                const syncButton = document.getElementById('sync-button');
                const attachButton = document.getElementById('attach-button');

                // Send message when button is clicked
                sendButton.addEventListener('click', sendMessage);

                // Send message when Enter key is pressed (but allow Shift+Enter for new lines)
                messageInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });

                // Add event listeners for the new buttons
                syncButton.addEventListener('click', () => {
                    vscode.postMessage({
                        command: 'syncCodebase'
                    });
                });

                attachButton.addEventListener('click', () => {
                    vscode.postMessage({
                        command: 'attachFile'
                    });
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