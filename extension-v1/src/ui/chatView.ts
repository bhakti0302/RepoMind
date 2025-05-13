import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { commands } from '../utils/commands';
import { generateResponse, suggestCorrection } from '../utils/chatAssistant';

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

        // Get workspace folders to allow access to visualization images
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const localResourceRoots = [this._extensionUri];

        // Add workspace folders to allowed resources
        if (workspaceFolders && workspaceFolders.length > 0) {
            workspaceFolders.forEach(folder => {
                localResourceRoots.push(folder.uri);
            });
        }

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: localResourceRoots
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(message => {
            if (message.command === commands.SEND_MESSAGE) {
                this._handleUserMessage(webviewView.webview, message.text);
            } else if (message.command === commands.SYNC_CODEBASE) {
                this._handleSyncCodebase(webviewView.webview);
            } else if (message.command === commands.ATTACH_FILE) {
                this._handleAttachFile(webviewView.webview);
            } else if (message.command === commands.OPEN_IMAGE) {
                this._handleOpenImage(message.path);
            } else if (message.command === commands.VISUALIZE_RELATIONSHIPS) {
                this._handleVisualizeRelationships(webviewView.webview);
            }
        });
    }

    private _handleOpenImage(imagePath: string) {
        // Open the image in the external viewer
        try {
            vscode.env.openExternal(vscode.Uri.file(imagePath));
        } catch (error: unknown) {
            console.error(`Error opening image: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    private _handleUserMessage(webview: vscode.Webview, text: string) {
        // Check for misspellings and suggest corrections
        const correction = suggestCorrection(text);
        if (correction && correction !== text) {
            // Suggest a correction
            setTimeout(() => {
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: `Did you mean: "${correction}"? I'll try to answer based on that.`,
                    isUser: false
                });

                // Process the corrected text
                this._processUserMessage(webview, correction);
            }, 500);
        } else {
            // Process the original text
            this._processUserMessage(webview, text);
        }
    }

    private _processUserMessage(webview: vscode.Webview, text: string) {
        // Generate a response using the chat assistant
        const response = generateResponse(text);

        // Handle any commands detected
        if (response.command === commands.VISUALIZE_RELATIONSHIPS) {
            // Handle visualization request
            this._handleVisualizeRelationships(webview);
        } else {
            // Send the text response
            setTimeout(() => {
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: response.text,
                    isUser: false
                });
            }, 500);
        }
    }

    private _handleVisualizeRelationships(webview: vscode.Webview) {
        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: 'Error: No workspace folder is open. Please open a folder first.',
                isUser: false
            });
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Path to the visualizations directory
        const visualizationsDir = path.join(workspaceFolder, 'visualizations');

        // Make sure the visualizations directory exists
        if (!fs.existsSync(visualizationsDir)) {
            try {
                fs.mkdirSync(visualizationsDir, { recursive: true });
            } catch (error) {
                console.error(`Error creating visualizations directory: ${error}`);
            }
        }

        // Check if visualizations already exist
        const multiFilePath = path.join(visualizationsDir, `${projectId}_multi_file_relationships.png`);
        const relationshipTypesPath = path.join(visualizationsDir, `${projectId}_relationship_types.png`);
        const visualizationsExist = fs.existsSync(multiFilePath) || fs.existsSync(relationshipTypesPath);

        // Show a message that we're visualizing
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: visualizationsExist
                ? `Showing code relationships for "${projectId}"...`
                : `Visualizing code relationships for "${projectId}"... This may take a moment.`,
            isUser: false
        });

        // If visualizations already exist, show them directly
        if (visualizationsExist) {
            console.log(`Visualizations exist at: ${multiFilePath} and/or ${relationshipTypesPath}`);

            // Show visualizations in the chat
            if (fs.existsSync(multiFilePath)) {
                this._showVisualizationInChat(webview, multiFilePath, 'Multi-File Relationships Visualization:');
            }

            // Add a small delay before showing the second visualization
            if (fs.existsSync(relationshipTypesPath)) {
                setTimeout(() => {
                    this._showVisualizationInChat(webview, relationshipTypesPath, 'Relationship Types Visualization:');
                }, 500);
            }

            return;
        }

        // Execute the command to visualize relationships
        try {
            console.log(`Generating visualizations for project: ${projectId}`);

            // Execute the command to generate visualizations
            vscode.commands.executeCommand('extension-v1.visualizeRelationships');

            // Add a message after a delay to simulate completion
            setTimeout(() => {
                // Check if visualizations were created
                if (fs.existsSync(multiFilePath) || fs.existsSync(relationshipTypesPath)) {
                    console.log(`Visualizations created at: ${multiFilePath} and/or ${relationshipTypesPath}`);

                    // Visualization completed successfully
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: 'Code relationships visualized successfully! Here are the visualizations:',
                        isUser: false
                    });

                    // Show visualizations in the chat
                    if (fs.existsSync(multiFilePath)) {
                        this._showVisualizationInChat(webview, multiFilePath, 'Multi-File Relationships Visualization:');
                    }

                    // Add a small delay before showing the second visualization
                    setTimeout(() => {
                        if (fs.existsSync(relationshipTypesPath)) {
                            this._showVisualizationInChat(webview, relationshipTypesPath, 'Relationship Types Visualization:');
                        }
                    }, 500);
                } else {
                    console.log(`Visualizations not found at: ${multiFilePath} or ${relationshipTypesPath}`);

                    // Visualizations were not created
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: 'Visualizations were generated but could not be found. Please try again later.',
                        isUser: false
                    });
                }
            }, 8000); // Increased timeout to give more time for visualization generation
        } catch (error: unknown) {
            console.error(`Error visualizing code relationships: ${error instanceof Error ? error.message : String(error)}`);

            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Error visualizing code relationships: ${error instanceof Error ? error.message : String(error)}`,
                isUser: false
            });
        }
    }

    private _showVisualizationInChat(webview: vscode.Webview, imagePath: string, caption: string) {
        // Log the visualization being shown
        console.log(`SHOWING VISUALIZATION: ${caption} - ${imagePath}`);

        // Perform thorough checks to ensure the image exists
        try {
            // Check if the file exists
            if (!fs.existsSync(imagePath)) {
                console.error(`Visualization file not found: ${imagePath}`);
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: `Could not find visualization. Please try syncing the codebase first.`,
                    isUser: false
                });
                return;
            }

            // Check if it's actually a file (not a directory)
            const stats = fs.statSync(imagePath);
            if (!stats.isFile()) {
                console.error(`Path exists but is not a file: ${imagePath}`);
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: `Visualization file is invalid. Please try regenerating visualizations.`,
                    isUser: false
                });
                return;
            }

            // Check if it has a valid image extension
            const validExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'];
            const fileExt = path.extname(imagePath).toLowerCase();
            if (!validExtensions.includes(fileExt)) {
                console.warn(`File exists but may not be an image (extension: ${fileExt}): ${imagePath}`);
                // Continue anyway, but log a warning
            }

            // Check if the file is readable
            try {
                // Try to read a small portion of the file to verify it's readable
                const fd = fs.openSync(imagePath, 'r');
                const buffer = Buffer.alloc(10);
                fs.readSync(fd, buffer, 0, 10, 0);
                fs.closeSync(fd);
            } catch (readError) {
                console.error(`File exists but is not readable: ${imagePath}`, readError);
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: `Visualization file cannot be read. Please try regenerating visualizations.`,
                    isUser: false
                });
                return;
            }

            console.log(`Visualization file verified and ready to display: ${imagePath}`);
        } catch (error) {
            console.error(`Error checking image file: ${error instanceof Error ? error.message : String(error)}`);
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Error checking visualization file. Please try syncing the codebase again.`,
                isUser: false
            });
            return;
        }

        console.log(`Sending visualization to chat: ${imagePath}`);

        // Send a message first with the caption
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: caption,
            isUser: false
        });

        try {
            // Create a URI for the image file
            const imageUri = vscode.Uri.file(imagePath);
            console.log(`DEBUG: Created image URI: ${imageUri.toString()}`);

            // Convert the URI to a webview URI
            const webviewUri = webview.asWebviewUri(imageUri);
            console.log(`DEBUG: Converted image path: ${imagePath} to webview URI: ${webviewUri}`);

            // Check if the webview URI is valid
            if (!webviewUri) {
                console.error(`DEBUG: Failed to create webview URI for ${imagePath}`);
            }

            // Send the image with additional metadata to help the frontend
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Code Visualization`,
                isUser: false,
                imagePath: imagePath, // Pass the original path for external opening (hidden from UI)
                isImage: true, // Flag to indicate this is an image message
                imageUri: webviewUri.toString(), // Pass the webview URI directly
                imageCaption: caption // Pass the caption for better display
            });
        } catch (error) {
            console.error(`Error sending image to chat: ${error instanceof Error ? error.message : String(error)}`);

            // Send an error message instead
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Error displaying visualization. Click to open externally.`,
                isUser: false,
                imagePath: imagePath // Pass the original path for external opening
            });
        }
    }

    private _handleSyncCodebase(webview: vscode.Webview) {
        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: 'Error: No workspace folder is open. Please open a folder first.',
                isUser: false
            });
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;

        // Show a message that we're syncing with a loading animation
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: `Syncing codebase from "${workspaceFolder}"... This may take a moment.`,
            isUser: false,
            isLoading: true,
            loadingType: 'sync'
        });

        // Execute the command to sync the codebase
        try {
            vscode.commands.executeCommand('extension-v1.syncCodebase');
            // Success message will be shown by the command itself
        } catch (error: unknown) {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
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
                        command: commands.ADD_MESSAGE,
                        text: `Attached file: ${fileName}`,
                        isUser: true
                    });

                    // Add the file content as a message
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `File content:\n\`\`\`\n${fileContent}\n\`\`\``,
                        isUser: false
                    });
                } catch (error: unknown) {
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
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

    /**
     * Send an image to the chat UI
     * @param imagePath Path to the image file
     * @param caption Optional caption to display with the image
     */
    public sendImageToChat(imagePath: string, caption?: string) {
        console.log(`DEBUG: sendImageToChat called with path: ${imagePath}, caption: ${caption || ''}`);

        // Check if the file exists
        if (!fs.existsSync(imagePath)) {
            console.error(`DEBUG: Image file does not exist: ${imagePath}`);
        } else {
            console.log(`DEBUG: Image file exists: ${imagePath}`);

            // Check file size
            try {
                const stats = fs.statSync(imagePath);
                console.log(`DEBUG: Image file size: ${stats.size} bytes`);
            } catch (error) {
                console.error(`DEBUG: Error checking file stats: ${error}`);
            }
        }

        if (this._view) {
            console.log(`DEBUG: View exists, calling _showVisualizationInChat`);
            this._showVisualizationInChat(this._view.webview, imagePath, caption || '');
        } else {
            console.error(`DEBUG: View does not exist, cannot show visualization`);
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
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes slideIn {
                    from { transform: translateY(10px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }

                .image-container {
                    margin: 10px 0;
                    text-align: center;
                }

                .chat-image {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                    cursor: pointer;
                    transition: transform 0.2s ease-in-out;
                }

                .chat-image:hover {
                    transform: scale(1.02);
                }
            </style>
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
                <button id="visualize-button" class="action-button">Show Visualizations</button>
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
                const visualizeButton = document.getElementById('visualize-button');

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

                visualizeButton.addEventListener('click', () => {
                    vscode.postMessage({
                        command: 'visualizeRelationships'
                    });
                });

                // Handle messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'addMessage' || message.command === '${commands.ADD_MESSAGE}') {
                        addMessage(
                            message.text,
                            message.isUser === true,
                            message.imagePath,
                            message.isImage === true,
                            message.imageUri,
                            message.imageCaption,
                            message.isLoading === true,
                            message.loadingType
                        );
                    } else if (message.command === 'openImage') {
                        vscode.postMessage({
                            command: 'openImage',
                            path: message.path
                        });
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

                function addMessage(text, isUser, imagePath, isImage, imageUri, imageCaption, isLoading, loadingType) {
                    const messageElement = document.createElement('div');
                    messageElement.className = isUser ? 'user-message' : 'assistant-message';

                    // Add a loading indicator if requested
                    if (isLoading && !isUser) {
                        // Add text with loading indicator
                        const textNode = document.createElement('div');
                        textNode.textContent = text + " (Analyzing...)";
                        textNode.style.marginBottom = '8px';
                        messageElement.appendChild(textNode);

                        // Add a simple loading indicator
                        const loadingDiv = document.createElement('div');
                        loadingDiv.style.marginTop = '10px';
                        loadingDiv.style.marginBottom = '10px';
                        loadingDiv.style.fontStyle = 'italic';
                        loadingDiv.style.color = '#666';
                        loadingDiv.textContent = 'Please wait while the codebase is being analyzed...';
                        messageElement.appendChild(loadingDiv);

                        return; // Skip the rest of the function
                    }

                    // Check if this is an image message (either by flag or content)
                    if (!isUser && (isImage || text.includes('![IMAGE]'))) {
                        // Parse the image path from the message if not directly provided
                        let imageSrc = imageUri;
                        let processedText = text;

                        if (!imageSrc) {
                            const regex = /!\[IMAGE\]\((.*?)\)/g;
                            let match;

                            while ((match = regex.exec(text)) !== null) {
                                imageSrc = match[1];
                                const imageTag = match[0];
                                // Remove the image tag from the text
                                processedText = processedText.replace(imageTag, '');
                            }
                        }

                        // If we have a caption but no processed text, use the caption
                        if (!processedText.trim() && imageCaption) {
                            processedText = imageCaption;
                        }

                        // Add the text part first if it exists
                        if (processedText.trim()) {
                            const textNode = document.createElement('div');
                            textNode.textContent = processedText.trim();
                            textNode.style.marginBottom = '8px';
                            messageElement.appendChild(textNode);
                        }

                        // Create image container and image element
                        const imageContainer = document.createElement('div');
                        imageContainer.className = 'image-container';

                        // Create a loading message
                        const loadingText = document.createElement('div');
                        loadingText.textContent = 'Loading visualization...';
                        loadingText.style.padding = '10px';
                        loadingText.style.textAlign = 'center';
                        loadingText.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                        loadingText.style.borderRadius = '4px';
                        imageContainer.appendChild(loadingText);

                        const image = document.createElement('img');
                        image.className = 'chat-image';
                        image.src = imageSrc;
                        image.alt = imageCaption || 'Code Visualization';
                        image.title = 'Click to open in external viewer';
                        image.style.maxWidth = '100%';
                        image.style.height = 'auto';
                        image.style.display = 'block';
                        image.style.margin = '0 auto';
                        image.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
                        image.style.borderRadius = '4px';

                        // Add onload event to remove loading message and show success
                        image.onload = () => {
                            if (loadingText.parentNode === imageContainer) {
                                imageContainer.removeChild(loadingText);
                            }
                            console.log('DEBUG: Image loaded successfully in webview:', imageSrc);

                            // Add a subtle animation to show the image has loaded
                            image.style.animation = 'fadeIn 0.5s';

                            // Log additional details about the loaded image
                            console.log('DEBUG: Image dimensions:', image.naturalWidth, 'x', image.naturalHeight);
                            console.log('DEBUG: Image complete:', image.complete);
                        };

                        // Add onerror event to show error message
                        image.onerror = (error) => {
                            console.error('DEBUG: Error loading image in webview:', imageSrc);
                            console.error('DEBUG: Error details:', error);

                            // Try to get more information about the image
                            const img = new Image();
                            img.onload = () => console.log('DEBUG: Image loads in separate Image object:', imageSrc);
                            img.onerror = () => console.error('DEBUG: Image also fails in separate Image object:', imageSrc);
                            img.src = imageSrc;

                            loadingText.textContent = 'Error loading visualization. Click to try opening externally.';
                            loadingText.style.color = '#ff6b6b';
                            loadingText.style.border = '1px solid #ff6b6b';
                            loadingText.style.padding = '12px';

                            // Add a retry button
                            const retryButton = document.createElement('button');
                            retryButton.textContent = 'Retry';
                            retryButton.style.marginTop = '8px';
                            retryButton.style.padding = '4px 12px';
                            retryButton.style.backgroundColor = '#0078d4';
                            retryButton.style.color = 'white';
                            retryButton.style.border = 'none';
                            retryButton.style.borderRadius = '4px';
                            retryButton.style.cursor = 'pointer';

                            retryButton.addEventListener('click', () => {
                                // Try loading the image again
                                image.src = imageSrc + '?retry=' + new Date().getTime();
                            });

                            loadingText.appendChild(document.createElement('br'));
                            loadingText.appendChild(retryButton);
                        };

                        // Use the original path for opening externally
                        const pathToOpen = imagePath || imageSrc;

                        // Add click event to open the image in external viewer
                        image.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'openImage',
                                path: pathToOpen
                            });
                        });

                        // Also make the loading text clickable
                        loadingText.style.cursor = 'pointer';
                        loadingText.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'openImage',
                                path: pathToOpen
                            });
                        });

                        imageContainer.appendChild(image);
                        messageElement.appendChild(imageContainer);

                        // Add a caption below the image if not already included in the text
                        if (imageCaption && !processedText.includes(imageCaption)) {
                            const captionElement = document.createElement('div');
                            captionElement.textContent = imageCaption;
                            captionElement.style.textAlign = 'center';
                            captionElement.style.fontStyle = 'italic';
                            captionElement.style.marginTop = '4px';
                            captionElement.style.color = '#666';
                            messageElement.appendChild(captionElement);
                        }

                        // Add a link to open externally
                        const openLink = document.createElement('div');
                        openLink.className = 'image-link';
                        openLink.textContent = 'Open visualization externally';
                        openLink.style.color = '#0078d4';
                        openLink.style.cursor = 'pointer';
                        openLink.style.marginTop = '8px';
                        openLink.style.textAlign = 'center';
                        openLink.style.fontSize = '12px';

                        openLink.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'openImage',
                                path: pathToOpen
                            });
                        });

                        messageElement.appendChild(openLink);
                    } else {
                        // Regular text message
                        messageElement.textContent = text;

                        // If there's an original image path but no image tag, add a link to open the image
                        if (!isUser && imagePath) {
                            const openLink = document.createElement('div');
                            openLink.className = 'image-link';
                            openLink.textContent = 'Click to open visualization externally';
                            openLink.style.color = '#0078d4';
                            openLink.style.cursor = 'pointer';
                            openLink.style.marginTop = '8px';
                            openLink.style.textDecoration = 'underline';

                            openLink.addEventListener('click', () => {
                                vscode.postMessage({
                                    command: 'openImage',
                                    path: imagePath
                                });
                            });

                            messageElement.appendChild(openLink);
                        }
                    }

                    messageHistory.appendChild(messageElement);

                    // Scroll to bottom
                    messageHistory.scrollTop = messageHistory.scrollHeight;

                    // Add a subtle animation to show the message has been added
                    messageElement.style.animation = 'slideIn 0.3s';
                }
            </script>
        </body>
        </html>`;
    }
}