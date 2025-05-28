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
            console.log('Received message from webview:', message);

            if (message.command === 'sendMessage') {
                console.log('Received sendMessage command with text:', message.text);
                // Handle the message directly in the chatView instead of forwarding
                this._handleUserMessage(webviewView.webview, message.text);
            } else if (message.command === 'syncCodebase') {
                console.log('Handling syncCodebase command');
                this._handleSyncCodebase(webviewView.webview);
            } else if (message.command === 'attachFile') {
                console.log('Handling attachFile command');
                this._handleAttachFile(webviewView.webview);
            } else if (message.command === commands.OPEN_IMAGE) {
                this._handleOpenImage(message.path);
            } else if (message.command === 'openFile') {
                // Handle openFile command
                vscode.commands.executeCommand(commands.OPEN_FILE, message.path);
            } else if (message.command === 'runMergeAgent') {
                // Handle runMergeAgent command
                console.log('ChatViewProvider: Executing runMergeAgent command');
                vscode.commands.executeCommand(commands.RUN_MERGE_AGENT);
            } else if (message.command === commands.CLEAR_HISTORY) {
                // Handle clearHistory command
                console.log('ChatViewProvider: Executing clearHistory command');
                this._handleClearHistory(webviewView.webview);
            } else if (message.command === commands.VISUALIZE_RELATIONSHIPS) {
                this._handleVisualizeRelationships(webviewView.webview);
            } else {
                console.log('Unknown command:', message.command);
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

    private async _handleUserMessage(webview: vscode.Webview, text: string) {
        console.log('_handleUserMessage called with text:', text);

        // First, add the user message to the UI
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: text,
            isUser: true
        });

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
            await this._processUserMessage(webview, text);
        }
    }

    private async _processUserMessage(webview: vscode.Webview, text: string) {
        console.log('_processUserMessage called with text:', text);

        // Generate a response using the chat assistant
        const response = generateResponse(text);
        console.log('Generated response:', response);

        // Handle any commands detected
        if (response.command === commands.VISUALIZE_RELATIONSHIPS) {
            // Handle visualization request
            this._handleVisualizeRelationships(webview);
        } else if (response.command === commands.PROCESS_CODE_QUESTION) {
            // Create a unique ID for the processing message
            const processingMessageId = `processing-${Date.now()}`;

            // Send the initial processing message with a loading indicator
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: response.text,
                isUser: false,
                id: processingMessageId,
                isLoading: true,
                loadingType: 'llm'
            });

            try {
                // Use the original processing directly for now (more reliable)
                console.log('Processing code question with original method');

                // Update message to show processing
                webview.postMessage({
                    command: commands.UPDATE_MESSAGE,
                    id: processingMessageId,
                    text: 'Searching codebase and generating response...',
                    isLoading: true,
                    loadingType: 'llm',
                    progress: 25,
                    stage: 'Processing'
                });

                const { processCodeQuestion } = require('../utils/chatAssistant');
                const llmResponse = await processCodeQuestion(text);

                console.log(`Received LLM response of length: ${llmResponse.length}`);

                // Update the processing message with the final LLM response
                webview.postMessage({
                    command: commands.UPDATE_MESSAGE,
                    id: processingMessageId,
                    text: llmResponse,
                    isLoading: false,
                    progress: 100,
                    stage: 'Complete'
                });

                // Log the conversation for debugging
                console.log(`Added message to conversation history: ${text.substring(0, 50)}...`);
            } catch (error) {
                console.error(`Error processing code question: ${error}`);

                // Generate enhanced error response
                const errorResponse = this._generateEnhancedErrorResponse(text, error as Error);

                // Update the processing message with the enhanced error
                webview.postMessage({
                    command: commands.UPDATE_MESSAGE,
                    id: processingMessageId,
                    text: errorResponse,
                    isLoading: false,
                    isError: true,
                    progress: 0,
                    stage: 'Error'
                });
            }
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

    private _generateEnhancedErrorResponse(_question: string, error: Error): string {
        const timestamp = new Date().toLocaleString();

        let errorResponse = `## ⚠️ Processing Error\n\n`;
        errorResponse += `I encountered an issue while processing your question at ${timestamp}.\n\n`;

        // Analyze the error type and provide specific guidance
        if (error.message.includes('ENOENT') || error.message.includes('not found')) {
            errorResponse += `**Issue**: Required files or scripts are missing.\n\n`;
            errorResponse += `**Suggestions**:\n`;
            errorResponse += `- Ensure the codebase analyzer is properly set up\n`;
            errorResponse += `- Check that all required scripts are in place\n`;
            errorResponse += `- Try running the "Sync Codebase" command first\n`;
        } else if (error.message.includes('API') || error.message.includes('key')) {
            errorResponse += `**Issue**: LLM API configuration problem.\n\n`;
            errorResponse += `**Suggestions**:\n`;
            errorResponse += `- Check your API key configuration in the .env file\n`;
            errorResponse += `- Verify your internet connection\n`;
            errorResponse += `- Ensure the API service is available\n`;
        } else if (error.message.includes('timeout')) {
            errorResponse += `**Issue**: Request timed out.\n\n`;
            errorResponse += `**Suggestions**:\n`;
            errorResponse += `- Try asking a more specific question\n`;
            errorResponse += `- Check your internet connection\n`;
            errorResponse += `- The system might be under heavy load, try again later\n`;
        } else {
            errorResponse += `**Issue**: Unexpected error occurred.\n\n`;
            errorResponse += `**Suggestions**:\n`;
            errorResponse += `- Try rephrasing your question\n`;
            errorResponse += `- Check the system logs for more details\n`;
            errorResponse += `- Contact support if the issue persists\n`;
        }

        errorResponse += `\n**Error Details**: \`${error.message}\`\n\n`;
        errorResponse += `**What you can try**:\n`;
        errorResponse += `1. Rephrase your question more specifically\n`;
        errorResponse += `2. Use the visualization features to explore the code\n`;
        errorResponse += `3. Check the project documentation\n`;
        errorResponse += `4. Try again in a few moments\n\n`;
        errorResponse += `*If this error persists, please check the extension logs or contact support.*`;

        return errorResponse;
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
            vscode.commands.executeCommand(commands.VISUALIZE_RELATIONSHIPS_COMMAND);

            // Add a message after a delay to check for completion
            setTimeout(() => {
                try {
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

                        // Try to find visualizations in alternative locations
                        const workspaceRoot = path.dirname(vscode.extensions.getExtension('extension-v1')?.extensionPath || '');
                        const dataDir = path.join(workspaceRoot, 'data');
                        const centralVisualizationsDir = path.join(dataDir, 'visualizations', projectId);

                        const centralMultiFilePath = path.join(centralVisualizationsDir, `${projectId}_multi_file_relationships.png`);
                        const centralRelationshipTypesPath = path.join(centralVisualizationsDir, `${projectId}_relationship_types.png`);

                        if (fs.existsSync(centralMultiFilePath) || fs.existsSync(centralRelationshipTypesPath)) {
                            console.log(`Visualizations found in central directory: ${centralVisualizationsDir}`);

                            webview.postMessage({
                                command: commands.ADD_MESSAGE,
                                text: 'Code relationships visualized successfully! Here are the visualizations:',
                                isUser: false
                            });

                            if (fs.existsSync(centralMultiFilePath)) {
                                this._showVisualizationInChat(webview, centralMultiFilePath, 'Multi-File Relationships Visualization:');
                            }

                            setTimeout(() => {
                                if (fs.existsSync(centralRelationshipTypesPath)) {
                                    this._showVisualizationInChat(webview, centralRelationshipTypesPath, 'Relationship Types Visualization:');
                                }
                            }, 500);
                        } else {
                            // Visualizations were not created
                            webview.postMessage({
                                command: commands.ADD_MESSAGE,
                                text: 'Visualizations were generated but could not be found. Please try again later.',
                                isUser: false
                            });

                            // Suggest using the manual visualization command
                            webview.postMessage({
                                command: commands.ADD_MESSAGE,
                                text: 'You can try using the manual visualization command by typing "visualize code" in the chat.',
                                isUser: false
                            });
                        }
                    }
                } catch (checkError) {
                    console.error(`Error checking for visualizations: ${checkError instanceof Error ? checkError.message : String(checkError)}`);
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `Error checking for visualizations: ${checkError instanceof Error ? checkError.message : String(checkError)}`,
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

            // Convert the URI to a webview URI
            const webviewUri = webview.asWebviewUri(imageUri);

            console.log(`Converted image path: ${imagePath} to webview URI: ${webviewUri}`);

            // Send the image with additional metadata to help the frontend
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Code Visualization`,
                isUser: false,
                imagePath: imagePath, // Pass the original path for external opening (hidden from UI)
                isImage: true, // Flag to indicate this is an image message
                imageUri: webviewUri.toString(), // Pass the webview URI directly
                imageCaption: caption, // Pass the caption for better display
                timestamp: Date.now() // Add timestamp to prevent caching issues
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

        // Generate a unique ID for the sync message
        const syncMessageId = `sync-${Date.now()}`;

        // Store the message ID in a global variable for later reference
        (global as any).lastSyncMessageId = syncMessageId;
        console.log(`Created sync message with ID: ${syncMessageId}`);

        // Show a message that we're syncing with a loading animation
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: `Syncing codebase from "${workspaceFolder}"... This may take a moment.`,
            isUser: false,
            isLoading: true,
            loadingType: 'sync',
            id: syncMessageId
        });

        // Execute the command to sync the codebase
        try {
            vscode.commands.executeCommand('extension-v1.syncCodebase');
            // Success message will be shown by the command itself via updateSyncMessage
        } catch (error: unknown) {
            // Update the sync message with the error
            webview.postMessage({
                command: commands.UPDATE_MESSAGE,
                id: syncMessageId,
                text: `Error syncing codebase: ${error instanceof Error ? error.message : String(error)}`
            });
        }
    }

    // Method to update the sync message with success
    public updateSyncMessage(text: string) {
        if (this._view && (global as any).lastSyncMessageId) {
            const syncMessageId = (global as any).lastSyncMessageId;
            console.log(`Updating sync message with ID: ${syncMessageId}`);

            // Update the message with success text and remove loading indicator
            this._view.webview.postMessage({
                command: commands.UPDATE_MESSAGE,
                id: syncMessageId,
                text: text + ' <span style="color: #22c55e; font-weight: bold;">✓</span>'
            });
        } else {
            console.log('No sync message ID found or view not available');

            // Fallback: add a new message if we can't update
            if (this._view) {
                this._view.webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: text,
                    isUser: false
                });
            }
        }
    }

    private _handleAttachFile(webview: vscode.Webview) {
        // Show a message that we're waiting for file selection
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: 'Please select a requirements file to attach...',
            isUser: false
        });

        // Execute the command to attach a file
        vscode.commands.executeCommand('extension-v1.attachFile');
    }

    private _handleClearHistory(webview: vscode.Webview) {
        // Import the clearConversationHistory function
        const { clearConversationHistory } = require('../utils/chatAssistant');

        // Clear the conversation history
        clearConversationHistory();

        // Show a message that the history has been cleared
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: 'Conversation history has been cleared. I\'ve forgotten our previous conversation.',
            isUser: false
        });
    }

    // Method to send a message to the webview
    public sendMessageToWebviews(message: any) {
        if (this._view) {
            // If this is an updateMessage command, add the command name from our constants
            if (message.command === 'updateMessage') {
                message.command = commands.UPDATE_MESSAGE;
            }

            this._view.webview.postMessage(message);
        }
    }

    /**
     * Send an image to the chat UI
     * @param imagePath Path to the image file
     * @param caption Optional caption to display with the image
     */
    public sendImageToChat(imagePath: string, caption?: string) {
        if (this._view) {
            this._showVisualizationInChat(this._view.webview, imagePath, caption || '');
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        // Get the local path to the HTML file
        const htmlPath = vscode.Uri.joinPath(this._extensionUri, 'media', 'chatView.html');

        // Read the HTML file
        const htmlContent = fs.readFileSync(htmlPath.fsPath, 'utf8');

        // Get the URI for the styles.css file
        const stylesUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'styles.css')
        );

        // Replace the placeholder with the actual URI
        return htmlContent.replace('styles.css', stylesUri.toString());
    }
}