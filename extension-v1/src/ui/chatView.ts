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
            console.log(`Received message from webview: ${JSON.stringify(message)}`);

            // Import logger
            const { logger } = require('../utils/logger');
            logger.info('ChatView', `Received UI action: ${message.command}`, message);

            if (message.command === commands.SEND_MESSAGE) {
                logger.info('ChatView', 'User sent a message', { text: message.text });
                this._handleUserMessage(webviewView.webview, message.text);
            } else if (message.command === commands.SYNC_CODEBASE) {
                logger.info('ChatView', 'User clicked Sync Codebase button');
                this._handleSyncCodebase(webviewView.webview);
            } else if (message.command === commands.ATTACH_FILE) {
                logger.info('ChatView', 'User clicked Attach File button');
                this._handleAttachFile(webviewView.webview);
            } else if (message.command === commands.OPEN_IMAGE) {
                logger.info('ChatView', 'User clicked to open image', { path: message.path });
                this._handleOpenImage(message.path);
            } else if (message.command === commands.VISUALIZE_RELATIONSHIPS) {
                logger.info('ChatView', 'User clicked Visualize Relationships button');
                this._handleVisualizeRelationships(webviewView.webview);
            } else if (message.command === 'showVisualizations') {
                logger.info('ChatView', 'User clicked Show Visualizations button');
                // Call the command to show all visualizations
                vscode.commands.executeCommand('extension-v1.showAllVisualizations');
            } else {
                logger.warn('ChatView', `Unknown command received: ${message.command}`, message);
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

        // Path to the project-specific visualizations directory
        const workspaceRoot = path.dirname(this._extensionUri.fsPath);
        const centralVisualizationsDir = path.join(workspaceRoot, 'data', 'projects', projectId, 'visualizations');

        // Log the paths for debugging
        console.log(`DEBUG: workspaceFolder = ${workspaceFolder}`);
        console.log(`DEBUG: projectId = ${projectId}`);
        console.log(`DEBUG: workspaceRoot = ${workspaceRoot}`);
        console.log(`DEBUG: centralVisualizationsDir = ${centralVisualizationsDir}`);

        // Create the directory if it doesn't exist
        if (!fs.existsSync(centralVisualizationsDir)) {
            try {
                fs.mkdirSync(centralVisualizationsDir, { recursive: true });
                console.log(`DEBUG: Created central visualizations directory: ${centralVisualizationsDir}`);
            } catch (error) {
                console.error(`Error creating central visualizations directory: ${error}`);
            }
        }

        // Check if visualizations already exist in the central directory
        // Look for any PNG files in the directory
        let visualizationFiles: string[] = [];
        if (fs.existsSync(centralVisualizationsDir)) {
            try {
                visualizationFiles = fs.readdirSync(centralVisualizationsDir)
                    .filter(file => file.endsWith('.png'))
                    .map(file => path.join(centralVisualizationsDir, file));

                console.log(`DEBUG: Found ${visualizationFiles.length} visualization files in central directory`);
                visualizationFiles.forEach(file => console.log(`DEBUG: Found visualization file: ${file}`));
            } catch (error) {
                console.error(`DEBUG: Error reading central visualizations directory: ${error}`);
            }
        }

        const visualizationsExist = visualizationFiles.length > 0;

        // Only show a loading message if we need to generate visualizations
        if (!visualizationsExist) {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Generating visualizations... This may take a moment.`,
                isUser: false,
                isLoading: true,
                loadingType: 'visualize'
            });
        }

        // If visualizations already exist, show them directly
        if (visualizationsExist) {
            console.log(`Visualizations exist in directory: ${centralVisualizationsDir}`);

            // Find the visualization file for each type
            const findVisualization = (pattern: string): string | null => {
                try {
                    // Look for a standardized filename first (e.g., multi_file_relationships.png)
                    const standardFileName = `${pattern}.png`;
                    const standardFilePath = path.join(centralVisualizationsDir, standardFileName);

                    if (fs.existsSync(standardFilePath)) {
                        return standardFilePath;
                    }

                    // Fall back to finding any file that includes the pattern
                    const matchingFiles = fs.readdirSync(centralVisualizationsDir)
                        .filter(file => file.includes(pattern) && file.endsWith('.png'))
                        .map(file => path.join(centralVisualizationsDir, file));

                    if (matchingFiles.length === 0) {
                        return null;
                    }

                    // Sort by timestamp (newest first)
                    matchingFiles.sort((a, b) => {
                        const statA = fs.statSync(a);
                        const statB = fs.statSync(b);
                        return statB.mtime.getTime() - statA.mtime.getTime();
                    });

                    return matchingFiles[0];
                } catch (error) {
                    console.error(`Error finding visualization for ${pattern}: ${error}`);
                    return null;
                }
            };

            // Find the visualizations
            const multiFilePath = findVisualization('multi_file_relationships');
            const relationshipTypesPath = findVisualization('relationship_types');
            const classDiagramPath = findVisualization('class_diagram');
            const packageDiagramPath = findVisualization('package_diagram');
            const dependencyGraphPath = findVisualization('dependency_graph');
            const inheritanceHierarchyPath = findVisualization('inheritance_hierarchy');

            // Log what we found
            console.log(`Found visualizations:
                Multi-File: ${multiFilePath || 'Not found'}
                Relationship Types: ${relationshipTypesPath || 'Not found'}
                Class Diagram: ${classDiagramPath || 'Not found'}
                Package Diagram: ${packageDiagramPath || 'Not found'}
                Dependency Graph: ${dependencyGraphPath || 'Not found'}
                Inheritance Hierarchy: ${inheritanceHierarchyPath || 'Not found'}
            `);

            // Show all visualizations with a small delay between each
            let delay = 0;
            const delayIncrement = 500;

            // Helper function to show a visualization with a delay
            const showWithDelay = (path: string | null, title: string, delay: number) => {
                if (path) {
                    setTimeout(() => {
                        this._showVisualizationInChat(webview, path, title);
                    }, delay);
                    return true;
                }
                return false;
            };

            // Show all visualizations with delays
            let visualizationsShown = 0;

            visualizationsShown += showWithDelay(multiFilePath, 'Multi-File Relationships', delay) ? 1 : 0;
            delay += delayIncrement;

            visualizationsShown += showWithDelay(relationshipTypesPath, 'Relationship Types', delay) ? 1 : 0;
            delay += delayIncrement;

            visualizationsShown += showWithDelay(classDiagramPath, 'Class Diagram', delay) ? 1 : 0;
            delay += delayIncrement;

            visualizationsShown += showWithDelay(packageDiagramPath, 'Package Diagram', delay) ? 1 : 0;
            delay += delayIncrement;

            visualizationsShown += showWithDelay(dependencyGraphPath, 'Dependency Graph', delay) ? 1 : 0;
            delay += delayIncrement;

            visualizationsShown += showWithDelay(inheritanceHierarchyPath, 'Inheritance Hierarchy', delay) ? 1 : 0;

            console.log(`Showing ${visualizationsShown} visualizations`);

            if (visualizationsShown === 0) {
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: 'No visualizations found. Please try syncing the codebase first.',
                    isUser: false
                });
            }

            return;
        }

        // Execute the command to visualize relationships
        try {
            console.log(`Generating visualizations for project: ${projectId}`);

            // Execute the command to generate visualizations using the manual_visualize.py script
            const extensionPath = this._extensionUri.fsPath;
            const workspaceRoot = path.dirname(extensionPath);
            const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');
            const manualVisualizePath = path.join(codebaseAnalyserPath, 'scripts', 'manual_visualize.py');

            if (!fs.existsSync(manualVisualizePath)) {
                console.error(`Manual visualization script not found at: ${manualVisualizePath}`);
                webview.postMessage({
                    command: commands.ADD_MESSAGE,
                    text: 'Visualization script not found. Please check your installation.',
                    isUser: false
                });
                return;
            }

            // Run the manual visualization script with standardized filenames
            const command = `cd "${codebaseAnalyserPath}" && python3 "${manualVisualizePath}" --output-dir "${centralVisualizationsDir}" --project-id "${projectId}" --standardized-names --replace-existing --debug`;
            console.log(`Running command: ${command}`);

            // Send a message to the user that we're generating visualizations
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Generating visualizations for ${projectId}...`,
                isUser: false
            });

            // Execute the command
            const childProcess = require('child_process');
            console.log(`DEBUG: About to execute command: ${command}`);
            childProcess.exec(command, (error: any, stdout: string, stderr: string) => {
                console.log(`DEBUG: Command execution completed`);
                console.log(`DEBUG: stdout: ${stdout}`);
                if (stderr) {
                    console.log(`DEBUG: stderr: ${stderr}`);
                }
                if (error) {
                    console.error(`Error generating visualizations: ${error.message}`);
                    console.error(`Stderr: ${stderr}`);

                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `Error generating visualizations: ${error.message}`,
                        isUser: false
                    });
                    return;
                }

                console.log(`Visualization generation succeeded`);
                console.log(`Stdout: ${stdout}`);

                // Check if visualizations were created
                if (fs.existsSync(centralVisualizationsDir)) {
                    const visualizationFiles = fs.readdirSync(centralVisualizationsDir)
                        .filter(file => file.endsWith('.png'));

                    if (visualizationFiles.length > 0) {
                        console.log(`Visualizations created in: ${centralVisualizationsDir}`);
                        console.log(`Found ${visualizationFiles.length} visualization files`);

                        // Show the visualizations
                        vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                    } else {
                        console.log(`No visualization files found in: ${centralVisualizationsDir}`);

                        webview.postMessage({
                            command: commands.ADD_MESSAGE,
                            text: 'Visualizations were generated but could not be found. Please try again later.',
                            isUser: false
                        });
                    }
                } else {
                    console.log(`Visualizations directory not found: ${centralVisualizationsDir}`);

                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: 'Visualizations directory not found. Please try again later.',
                        isUser: false
                    });
                }
            });
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

            // Get file size for debugging
            const fileSize = stats.size;
            console.log(`Visualization file size: ${fileSize} bytes`);

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

        // Don't send a separate message with the caption - we'll include it with the image

        try {
            // Create a URI for the image file
            const imageUri = vscode.Uri.file(imagePath);
            console.log(`DEBUG: Created image URI: ${imageUri.toString()}`);

            // Convert the URI to a webview URI
            const webviewUri = webview.asWebviewUri(imageUri);
            console.log(`DEBUG: Converted image path: ${imagePath} to webview URI: ${webviewUri.toString()}`);

            // Check if the webview URI is valid
            if (!webviewUri) {
                console.error(`DEBUG: Failed to create webview URI for ${imagePath}`);
            }

            // Create a data URI from the image file for direct embedding
            // This is a fallback method that should work even if the webview URI doesn't
            let dataUri = '';
            try {
                const imageBuffer = fs.readFileSync(imagePath);
                const base64Image = imageBuffer.toString('base64');
                const fileExtension = path.extname(imagePath).toLowerCase();
                const mimeType = fileExtension === '.png' ? 'image/png' :
                                fileExtension === '.jpg' || fileExtension === '.jpeg' ? 'image/jpeg' :
                                fileExtension === '.gif' ? 'image/gif' :
                                fileExtension === '.svg' ? 'image/svg+xml' :
                                'application/octet-stream';
                dataUri = `data:${mimeType};base64,${base64Image}`;
                console.log(`DEBUG: Created data URI for image (length: ${dataUri.length})`);
            } catch (dataUriError) {
                console.error(`DEBUG: Failed to create data URI: ${dataUriError}`);
            }

            // Send the image with additional metadata to help the frontend
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Code Visualization`,
                isUser: false,
                imagePath: imagePath, // Pass the original path for external opening (hidden from UI)
                isImage: true, // Flag to indicate this is an image message
                imageUri: webviewUri.toString(), // Pass the webview URI directly
                dataUri: dataUri, // Pass the data URI as a fallback
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

        // Show a message that we're syncing with a loading animation and more interactive text
        webview.postMessage({
            command: commands.ADD_MESSAGE,
            text: `Syncing codebase from "${workspaceFolder}"...`,
            isUser: false,
            isLoading: true,
            loadingType: 'sync'
        });

        // Send a more detailed message about what's happening
        setTimeout(() => {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Analyzing code structure and relationships...`,
                isUser: false
            });
        }, 1000);

        setTimeout(() => {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Extracting code chunks and building dependency graph...`,
                isUser: false
            });
        }, 3000);

        // Add a completion message after a longer delay
        setTimeout(() => {
            webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: `Great! Codebase analysis completed successfully. You can now use the "Show Visualizations" button to see code relationships.`,
                isUser: false
            });
        }, 6000);

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

        // Execute the command to attach a file
        vscode.window.showOpenDialog({
            canSelectMany: false,
            openLabel: 'Attach',
            filters: {
                'Text Files': ['txt'] // Only allow .txt files
            }
        }).then(files => {
            if (files && files.length > 0) {
                const filePath = files[0].fsPath;
                const fileName = path.basename(filePath);

                try {
                    const fileContent = fs.readFileSync(filePath, 'utf8');

                    // Get the path to the business requirements directory
                    const extensionPath = this._extensionUri.fsPath;
                    const workspaceRoot = path.dirname(extensionPath);
                    const businessReqDir = path.join(workspaceRoot, 'data', 'projects', projectId, 'requirements');

                    // Create the directory if it doesn't exist
                    if (!fs.existsSync(businessReqDir)) {
                        fs.mkdirSync(businessReqDir, { recursive: true });
                    }

                    // Save the file to the business requirements directory
                    const destPath = path.join(businessReqDir, fileName);
                    fs.writeFileSync(destPath, fileContent, 'utf8');

                    // Add a message showing the attached file
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `Attached file: ${fileName}`,
                        isUser: true
                    });

                    // Add a message showing where the file was saved
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `File saved to: ${destPath}`,
                        isUser: false
                    });

                    // Add the file content as a message
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `File content:\n\`\`\`\n${fileContent}\n\`\`\``,
                        isUser: false
                    });

                    // Process the business requirements
                    vscode.commands.executeCommand('extension-v1.processBusinessRequirements', destPath);
                } catch (error: unknown) {
                    webview.postMessage({
                        command: commands.ADD_MESSAGE,
                        text: `Error processing file: ${error instanceof Error ? error.message : String(error)}`,
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

    /**
     * Send a text message to the chat UI
     * @param text The text message to send
     * @param isUser Whether the message is from the user (default: false)
     */
    public sendTextToChat(text: string, isUser: boolean = false, isLoading: boolean = false, loadingType: string = '') {
        console.log(`DEBUG: sendTextToChat called with text: ${text}, isLoading: ${isLoading}`);

        if (this._view) {
            this._view.webview.postMessage({
                command: commands.ADD_MESSAGE,
                text: text,
                isUser: isUser,
                isLoading: isLoading,
                loadingType: loadingType
            });
        } else {
            console.error(`DEBUG: View does not exist, cannot send text message`);
        }
    }

    /**
     * Check if the view is available
     * @returns true if the view is available, false otherwise
     */
    public isViewAvailable(): boolean {
        return this._view !== undefined;
    }

    /**
     * Refresh the chat view to ensure it picks up new files
     */
    public refreshView(): void {
        if (this._view) {
            console.log('Refreshing chat view');

            // Add a small delay before refreshing to ensure files are fully written
            setTimeout(() => {
                // Post a message to the webview to refresh its content
                this._view?.webview.postMessage({
                    command: 'refresh'
                });

                console.log('Refresh message sent to webview');
            }, 1000);
        } else {
            console.error('Cannot refresh view: view is not available');
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
                    background-color: #2d2d2d;
                    border-radius: 4px;
                    padding: 10px;
                    border: 1px solid #444;
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

                .image-placeholder {
                    width: 100%;
                    height: 200px;
                    background-color: #3d3d3d;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    color: #aaa;
                    font-style: italic;
                    cursor: pointer;
                }

                .image-link {
                    display: inline-block;
                    margin-top: 8px;
                    color: #0078d4;
                    text-decoration: underline;
                    cursor: pointer;
                }

                .image-link:hover {
                    color: #2b95d6;
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
                    // First, add a loading message to indicate processing has started
                    addMessage(
                        'Processing visualizations... Please wait while I prepare the visualizations for you.',
                        false,
                        null,
                        false,
                        null,
                        null,
                        true,
                        'visualize',
                        null
                    );

                    // Then send a message to the extension to show visualizations
                    vscode.postMessage({
                        command: 'showVisualizations'
                    });
                });

                // Handle messages from the extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.command === 'addMessage' || message.command === '${commands.ADD_MESSAGE}') {
                        // Debug log the message object
                        console.log('Received message:', message);

                        addMessage(
                            message.text,
                            message.isUser === true,
                            message.imagePath,
                            message.isImage === true,
                            message.imageUri,
                            message.imageCaption,
                            message.isLoading === true,
                            message.loadingType,
                            message.dataUri
                        );
                    } else if (message.command === 'openImage') {
                        vscode.postMessage({
                            command: 'openImage',
                            path: message.path
                        });
                    } else if (message.command === 'refresh') {
                        console.log('Received refresh command');
                        // Don't automatically show visualizations on refresh
                        // Just log that we received the refresh command
                        console.log('Chat view refreshed');
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

                function addMessage(text, isUser, imagePath, isImage, imageUri, imageCaption, isLoading, loadingType, dataUri) {
                    // Debug log all parameters
                    console.log('addMessage called with:');
                    console.log('- text:', text);
                    console.log('- isUser:', isUser);
                    console.log('- imagePath:', imagePath);
                    console.log('- isImage:', isImage);
                    console.log('- imageUri:', imageUri);
                    console.log('- imageCaption:', imageCaption);
                    console.log('- isLoading:', isLoading);
                    console.log('- loadingType:', loadingType);
                    console.log('- dataUri:', dataUri ? 'present (length: ' + dataUri.length + ')' : 'not present');
                    const messageElement = document.createElement('div');
                    messageElement.className = isUser ? 'user-message' : 'assistant-message';

                    // Add a loading indicator if requested
                    if (isLoading && !isUser) {
                        // Add text with loading indicator
                        const textNode = document.createElement('div');
                        textNode.textContent = text;
                        textNode.style.marginBottom = '8px';
                        messageElement.appendChild(textNode);

                        // Add a more visible loading indicator with animation
                        const loadingDiv = document.createElement('div');
                        loadingDiv.style.marginTop = '10px';
                        loadingDiv.style.marginBottom = '10px';
                        loadingDiv.style.padding = '10px';
                        loadingDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                        loadingDiv.style.borderRadius = '4px';
                        loadingDiv.style.border = '1px solid rgba(0, 0, 0, 0.1)';

                        // Create loading dots animation
                        const loadingDotsContainer = document.createElement('div');
                        loadingDotsContainer.style.display = 'flex';
                        loadingDotsContainer.style.justifyContent = 'center';
                        loadingDotsContainer.style.marginTop = '8px';

                        // Add loading message based on type
                        const loadingMessage = document.createElement('div');
                        loadingMessage.style.fontStyle = 'italic';
                        loadingMessage.style.color = '#666';

                        if (loadingType === 'visualize') {
                            loadingMessage.textContent = 'Please wait while the visualizations are being prepared...';
                        } else if (loadingType === 'sync') {
                            loadingMessage.textContent = 'Please wait while the codebase is being analyzed...';
                        } else {
                            loadingMessage.textContent = 'Processing your request...';
                        }

                        loadingDiv.appendChild(loadingMessage);
                        loadingDiv.appendChild(loadingDotsContainer);

                        // Add animated dots
                        for (let i = 0; i < 3; i++) {
                            const dot = document.createElement('div');
                            dot.textContent = '•';
                            dot.style.fontSize = '24px';
                            dot.style.margin = '0 4px';
                            dot.style.color = '#0078d4';
                            dot.style.animation = 'dotAnimation 1.4s infinite ' + (i * 0.2) + 's';
                            loadingDotsContainer.appendChild(dot);
                        }

                        // Add animation style
                        const style = document.createElement('style');
                        style.textContent =
                            '@keyframes dotAnimation {' +
                            '0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }' +
                            '40% { transform: scale(1.2); opacity: 1; }' +
                            '}';
                        messageElement.appendChild(style);

                        messageElement.appendChild(loadingDiv);
                        messageHistory.appendChild(messageElement);
                        messageHistory.scrollTop = messageHistory.scrollHeight;

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

                        // Create image container
                        const imageContainer = document.createElement('div');
                        imageContainer.className = 'image-container';

                        // Use the original path for opening externally
                        const pathToOpen = imagePath || imageSrc;

                        // Create an image element
                        const image = document.createElement('img');
                        image.className = 'chat-image';
                        image.alt = imageCaption || 'Code Visualization';
                        image.title = 'Click to open in external viewer';

                        // Try to use the data URI first if available
                        if (typeof dataUri === 'string' && dataUri) {
                            console.log('Using data URI for image');
                            image.src = dataUri;
                        } else if (imageSrc) {
                            console.log('Using image URI for image: ' + imageSrc);
                            image.src = imageSrc;
                        } else {
                            console.log('No image source available');
                        }

                        // Add loading indicator
                        const loadingText = document.createElement('div');
                        loadingText.textContent = 'Loading visualization...';
                        loadingText.style.padding = '10px';
                        loadingText.style.textAlign = 'center';
                        loadingText.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
                        loadingText.style.borderRadius = '4px';
                        imageContainer.appendChild(loadingText);

                        // Add onload event to remove loading message
                        image.onload = () => {
                            if (loadingText.parentNode === imageContainer) {
                                imageContainer.removeChild(loadingText);
                            }
                            console.log('Image loaded successfully');
                        };

                        // Add onerror event to show placeholder instead
                        image.onerror = () => {
                            console.error('Error loading image');

                            // Remove the image if it was added
                            if (image.parentNode === imageContainer) {
                                imageContainer.removeChild(image);
                            }

                            // Update loading text to be a placeholder
                            loadingText.textContent = 'Click to view visualization';
                            loadingText.style.cursor = 'pointer';
                            loadingText.addEventListener('click', () => {
                                vscode.postMessage({
                                    command: 'openImage',
                                    path: pathToOpen
                                });
                            });
                        };

                        // Add click event to open externally
                        image.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'openImage',
                                path: pathToOpen
                            });
                        });

                        // Add the image to the container
                        imageContainer.appendChild(image);

                        // Force the image to load
                        setTimeout(() => {
                            if (image.complete) {
                                console.log('Image already loaded');
                                if (loadingText.parentNode === imageContainer) {
                                    imageContainer.removeChild(loadingText);
                                }
                            } else {
                                console.log('Image still loading, setting src again');
                                const originalSrc = image.src;
                                image.src = '';
                                setTimeout(() => {
                                    image.src = originalSrc;
                                }, 10);
                            }
                        }, 100);

                        // Add a link to open externally
                        const openLink = document.createElement('div');
                        openLink.className = 'image-link';
                        openLink.textContent = 'Open visualization externally';
                        openLink.addEventListener('click', () => {
                            vscode.postMessage({
                                command: 'openImage',
                                path: pathToOpen
                            });
                        });
                        imageContainer.appendChild(openLink);

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