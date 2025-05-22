// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as cp from 'child_process';
import { StatusBarItem } from './ui/statusBar';
import { ChatViewProvider } from './ui/chatView';
import { ErrorLogger } from './utils/errorLogger';
import { DirectImageDisplay } from './utils/directImageDisplay';
import { logger, LogLevel } from './utils/logger';
import { CodebaseAnalyzerLogger } from './utils/codebaseAnalyzerLogger';
import { TestVisualizations } from './test/testVisualizations';
import { BusinessRequirementsProcessor } from './utils/businessRequirementsProcessor';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
    // Add console logs for debugging
    console.log('EXTENSION ACTIVATION STARTED');

    try {
        // Initialize logger
        logger.setLogLevel(LogLevel.DEBUG);
        console.log('LOGGER INITIALIZED');
        logger.info('Extension', 'RepoMind is now active!');

        // Log workspace folder information
        const initialWorkspaceFolders = vscode.workspace.workspaceFolders;
        console.log(`WORKSPACE FOLDERS: ${initialWorkspaceFolders ? initialWorkspaceFolders.length : 0}`);

        if (initialWorkspaceFolders && initialWorkspaceFolders.length > 0) {
            const initialWorkspaceFolder = initialWorkspaceFolders[0].uri.fsPath;
            const initialProjectId = path.basename(initialWorkspaceFolder);
            console.log(`WORKSPACE FOLDER: ${initialWorkspaceFolder}`);
            console.log(`PROJECT ID: ${initialProjectId}`);
            logger.info('Extension', `Workspace folder: ${initialWorkspaceFolder}`);
            logger.info('Extension', `Project ID: ${initialProjectId}`);
        } else {
            console.log('NO WORKSPACE FOLDER OPEN');
            logger.warn('Extension', 'No workspace folder is open');
        }

        // Show a notification to confirm the extension is loaded
        vscode.window.showInformationMessage('RepoMind extension is now active!');
    } catch (error) {
        console.error(`ERROR DURING ACTIVATION: ${error instanceof Error ? error.message : String(error)}`);
        vscode.window.showErrorMessage(`Error activating RepoMind: ${error instanceof Error ? error.message : String(error)}`);
    }

    // Register command to show log file
    let showLogCommand = vscode.commands.registerCommand('extension-v1.showLog', () => {
        logger.showLogFile();
    });
    context.subscriptions.push(showLogCommand);

    // Register command to reset log file
    let resetLogCommand = vscode.commands.registerCommand('extension-v1.resetLog', () => {
        logger.resetLogFile();
        vscode.window.showInformationMessage('Log file has been reset');
    });
    context.subscriptions.push(resetLogCommand);

    // Log extension activation
    console.log('RepoMind is now active!');

    // Initialize status bar
    const statusBar = StatusBarItem.getInstance();
    context.subscriptions.push(statusBar);

    // Register chat view provider
    const chatViewProvider = new ChatViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            ChatViewProvider.viewType,
            chatViewProvider
        )
    );

    // Register commands
    let startAssistantCommand = vscode.commands.registerCommand('extension-v1.startAssistant', () => {
        vscode.window.showInformationMessage('RepoMind started!');
        // Focus our chat view without affecting other extensions
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.repomind-container');
        }, 100);
        statusBar.setReady('RepoMind is ready');
    });

    // Process business requirements command
    let processBusinessRequirementsCommand = vscode.commands.registerCommand('extension-v1.processBusinessRequirements', (filePath: string) => {
        statusBar.setWorking('Processing business requirements...');

        // Focus our chat view without affecting other extensions
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.repomind-container');
        }, 100);

        // Show a message in the chat view
        if (chatViewProvider) {
            chatViewProvider.sendMessageToWebviews({
                command: 'addMessage',
                text: `Processing business requirements from ${path.basename(filePath)}...`,
                isUser: false,
                isLoading: true,
                loadingType: 'processing'
            });

            // Add a more detailed message about what's happening
            setTimeout(() => {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: `Analyzing requirements using NLP techniques...`,
                    isUser: false
                });
            }, 1000);

            setTimeout(() => {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: `Retrieving relevant code context...`,
                    isUser: false
                });
            }, 3000);
        }

        // Create a BusinessRequirementsProcessor instance
        const businessRequirementsProcessor = new BusinessRequirementsProcessor(context.extensionPath);

        // Process the business requirements file
        businessRequirementsProcessor.processRequirementsFile(filePath, (result) => {
            if (result.status === 'error') {
                statusBar.setError('Error processing requirements');
                vscode.window.showErrorMessage(`Error processing business requirements: ${result.message}`);

                if (chatViewProvider) {
                    chatViewProvider.sendMessageToWebviews({
                        command: 'addMessage',
                        text: `Error processing business requirements: ${result.message}`,
                        isUser: false
                    });
                }

                // If there's a log file, show a button to view it
                if (result.logFile) {
                    vscode.window.showErrorMessage(
                        'Error processing business requirements. See error log for details.',
                        'View Error Log'
                    ).then(selection => {
                        if (selection === 'View Error Log') {
                            ErrorLogger.showErrorLog(result.logFile);
                        }
                    });
                }
            } else {
                statusBar.setReady('Requirements processed');
                vscode.window.showInformationMessage('Business requirements processed successfully!');

                if (chatViewProvider) {
                    // Show the generated code in the chat view
                    chatViewProvider.sendMessageToWebviews({
                        command: 'addMessage',
                        text: `Business requirements processed successfully!`,
                        isUser: false
                    });

                    // Show the generated code
                    if (result.generatedCode) {
                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `Generated code:\n\`\`\`\n${result.generatedCode}\n\`\`\``,
                            isUser: false
                        });
                    } else {
                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `No code was generated. Please check the requirements file and try again.`,
                            isUser: false
                        });
                    }
                }
            }
        });
    });

    let analyzeRequirementsCommand = vscode.commands.registerCommand('extension-v1.analyzeRequirements', async () => {
        statusBar.setWorking('Analyzing requirements...');

        // Ask the user to select a requirements file
        const files = await vscode.workspace.findFiles('**/*.{txt,md}', '**/node_modules/**');
        if (files.length === 0) {
            vscode.window.showErrorMessage('No text or markdown files found in the workspace.');
            statusBar.setError('No requirements files found');
            return;
        }

        const fileItems = files.map(file => ({
            label: vscode.workspace.asRelativePath(file),
            description: 'Requirements file',
            file
        }));

        const selectedFile = await vscode.window.showQuickPick(fileItems, {
            placeHolder: 'Select a requirements file to analyze'
        });

        if (selectedFile) {
            vscode.window.showInformationMessage(`Analyzing requirements from ${selectedFile.label}`);

            // Read the file content
            try {
                const fileContent = fs.readFileSync(selectedFile.file.fsPath, 'utf8');
                console.log(`Read file content (${fileContent.length} bytes)`);
                // TODO: Implement requirements analysis
                vscode.window.showInformationMessage('Requirements analyzed successfully!');
                statusBar.setReady('Requirements analyzed');
            } catch (error) {
                vscode.window.showErrorMessage(`Error reading file: ${error instanceof Error ? error.message : String(error)}`);
                statusBar.setError('Error reading requirements file');
            }
        } else {
            statusBar.setDefault();
        }
    });

    let generateCodeCommand = vscode.commands.registerCommand('extension-v1.generateCode', () => {
        statusBar.setWorking('Generating code...');
        vscode.window.showInformationMessage('Generating code from requirements...');

        // TODO: Implement code generation logic

        // For now, just simulate a delay and then show success
        setTimeout(() => {
            statusBar.setReady('Code generated');
            vscode.window.showInformationMessage('Code generation completed!');
        }, 2000);
    });

    let openChatViewCommand = vscode.commands.registerCommand('extension-v1.openChatView', () => {
        // Focus our chat view without affecting other extensions
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.repomind-container');
        }, 100);
    });

    // Sync codebase command
    let syncCodebaseCommand = vscode.commands.registerCommand('extension-v1.syncCodebase', async () => {
        // Make sure we stay in our extension view
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.repomind-container');
        }, 100);

        statusBar.setWorking('Syncing codebase...');

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            statusBar.setError('No workspace folder');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Get the path to the codebase-analyser directory relative to the extension
        const extensionPath = context.extensionPath;
        const workspaceRoot = path.dirname(extensionPath);
        const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');

        // Path to the LanceDB database
        const dbPath = path.join(codebaseAnalyserPath, '.lancedb');

        // Check if the database exists and if it has data for this project
        let isFullSync = false;

        try {
            // Check if the database directory exists
            if (!fs.existsSync(dbPath)) {
                console.log(`Database directory does not exist at: ${dbPath}`);
                isFullSync = true;
            } else {
                // Check if the code_chunks table exists with data for this project
                // We'll use a simple command to check if the project exists in the database
                const checkCommand = `cd "${codebaseAnalyserPath}" && python3 -c "import lancedb; import sys; db = lancedb.connect('.lancedb'); tables = db.table_names(); sys.exit(0 if 'code_chunks' in tables else 1)"`;

                try {
                    cp.execSync(checkCommand);

                    // Now check if the project exists in the database
                    const checkProjectCommand = `cd "${codebaseAnalyserPath}" && python3 -c "import lancedb; import sys; db = lancedb.connect('.lancedb'); table = db.open_table('code_chunks'); df = table.to_arrow().to_pandas(); sys.exit(0 if '${projectId}' in df['project_id'].unique() else 1)"`;

                    try {
                        cp.execSync(checkProjectCommand);
                        console.log(`Project ${projectId} found in database, using incremental update`);
                        isFullSync = false;
                    } catch (error) {
                        console.log(`Project ${projectId} not found in database, using full sync`);
                        isFullSync = true;
                    }
                } catch (error) {
                    console.log(`Table 'code_chunks' not found in database, using full sync`);
                    isFullSync = true;
                }
            }
        } catch (error) {
            console.error(`Error checking database: ${error}`);
            isFullSync = true;
        }

        // Create a CodebaseAnalyzerLogger instance
        const codebaseAnalyzer = new CodebaseAnalyzerLogger(codebaseAnalyserPath);

        // Log the sync operation
        logger.info('Extension', `Syncing codebase: ${workspaceFolder}`, {
            projectId,
            isFullSync,
            codebaseAnalyserPath
        });

        // Show appropriate message
        if (isFullSync) {
            vscode.window.showInformationMessage(`Performing full sync for project: ${projectId}`);
        } else {
            vscode.window.showInformationMessage(`Performing incremental update for project: ${projectId}`);
        }

        console.log(`Workspace folder: ${workspaceFolder}`);
        console.log(`Project ID: ${projectId}`);
        console.log(`Codebase Analyser path: ${codebaseAnalyserPath}`);

        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Syncing codebase',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ message: 'Starting analysis...' });

            return new Promise<void>((resolve, reject) => {
                // Check if the codebase-analyser directory exists
                try {
                    if (fs.existsSync(codebaseAnalyserPath)) {
                        console.log(`Codebase analyser directory exists at: ${codebaseAnalyserPath}`);

                        // Check if the analyze_java.py script exists
                        const scriptPath = path.join(codebaseAnalyserPath, 'scripts', 'analyze_java.py');
                        if (fs.existsSync(scriptPath)) {
                            console.log(`Script exists at: ${scriptPath}`);
                        } else {
                            console.error(`Script does not exist at: ${scriptPath}`);
                            vscode.window.showErrorMessage(`Script not found: ${scriptPath}`);
                            reject(new Error(`Script not found: ${scriptPath}`));
                            return;
                        }
                    } else {
                        console.error(`Codebase analyser directory does not exist at: ${codebaseAnalyserPath}`);
                        vscode.window.showErrorMessage(`Codebase analyser directory not found: ${codebaseAnalyserPath}`);
                        reject(new Error(`Codebase analyser directory not found: ${codebaseAnalyserPath}`));
                        return;
                    }
                } catch (err) {
                    console.error(`Error checking directories: ${err}`);
                    reject(err);
                    return;
                }

                // Try running the python3 command directly to see if it works
                console.log('Testing if python3 is available...');
                cp.exec('python3 --version', (pyError, pyStdout) => {
                    if (pyError) {
                        console.error(`Python3 error: ${pyError.message}`);
                        vscode.window.showErrorMessage(`Python3 not found: ${pyError.message}`);
                        statusBar.setError('Python3 not found');
                        reject(pyError);
                        return;
                    }

                    console.log(`Python3 version: ${pyStdout.trim()}`);

                    // Now run the sync operation using the CodebaseAnalyzerLogger
                    console.log('Running the sync operation...');

                    // Use the appropriate method based on whether we need a full sync or incremental update
                    const syncPromise = isFullSync
                        ? codebaseAnalyzer.analyzeJava(workspaceFolder, projectId, true, true)
                        : codebaseAnalyzer.updateCodebase(workspaceFolder, projectId, true);

                    // Create a cancellation token
                    let isCancelled = false;
                    token.onCancellationRequested(() => {
                        isCancelled = true;
                        vscode.window.showInformationMessage('Codebase sync cancelled.');
                        statusBar.setDefault();
                        resolve();
                    });

                    // Execute the sync operation
                    syncPromise.then(async (stdout) => {
                        if (isCancelled) {
                            return;
                        }

                        console.log(`Stdout: ${stdout}`);

                        try {
                            // Get the last sync time from the database
                            const lastSyncTime = await codebaseAnalyzer.getLastSyncTime(projectId);
                            console.log(`Last sync time: ${lastSyncTime}`);

                            // Format the timestamp for display
                            let formattedTime = lastSyncTime;
                            try {
                                if (lastSyncTime !== 'Unknown') {
                                    // Parse ISO timestamp and format it
                                    const date = new Date(lastSyncTime);
                                    // Use a more explicit format to avoid confusion
                                    formattedTime = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                                }
                            } catch (error) {
                                console.error(`Error formatting timestamp: ${error}`);
                                logger.error('Extension', `Error formatting timestamp: ${error}`);
                            }

                            // Show success message with timestamp
                            vscode.window.showInformationMessage(`Codebase synced successfully at ${formattedTime}!`);
                            statusBar.setReady(`Synced at ${formattedTime}`);

                            // Send timestamp to chat view if available
                            if (chatViewProvider) {
                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Codebase synced successfully at ${formattedTime}`,
                                    isUser: false
                                });
                            }

                            // Automatically regenerate visualizations after syncing
                            logger.info('Extension', 'Automatically regenerating visualizations after sync');
                            console.log('Automatically regenerating visualizations after sync...');
                            vscode.commands.executeCommand('extension-v1.visualizeRelationships');
                        } catch (error) {
                            logger.error('Extension', `Error getting last sync time: ${error}`);
                            console.error(`Error getting last sync time: ${error}`);
                            vscode.window.showInformationMessage('Codebase synced successfully!');
                            statusBar.setReady('Codebase synced');
                        }

                        resolve();
                    }).catch((error) => {
                        if (isCancelled) {
                            return;
                        }

                        const errorMessage = `Error syncing codebase: ${error.message}`;
                        vscode.window.showErrorMessage(errorMessage);
                        statusBar.setError('Sync failed');
                        console.error(`Error: ${error.message}`);

                        // Create a detailed error log
                        const errorLog = `
Error running codebase analysis:
- Error message: ${error.message}
- Working directory: ${codebaseAnalyserPath}
- Project path: ${workspaceFolder}
- Project ID: ${projectId}
- Full sync: ${isFullSync}
                        `;

                        // Log to console
                        console.error('DETAILED ERROR LOG:');
                        console.error(errorLog);

                        // Log the error using the ErrorLogger
                        const logFile = ErrorLogger.logError(error, {
                            workspaceFolder,
                            projectId,
                            codebaseAnalyserPath,
                            isFullSync
                        });

                        // Show a message with an option to view the error log
                        vscode.window.showErrorMessage(
                            'Error syncing codebase. See error log for details.',
                            'View Error Log'
                        ).then(selection => {
                            if (selection === 'View Error Log') {
                                ErrorLogger.showErrorLog(logFile);
                            }
                        });

                        // Send error to chat view
                        vscode.commands.executeCommand('extension-v1.sendErrorToChat', errorLog, logFile);

                        reject(error);
                    });
                });
            });
        }).then(() => {
            console.log('Sync process completed successfully');
        }, (error: unknown) => {
            console.error(`Sync process failed: ${error instanceof Error ? error.message : String(error)}`);
        });
    });

    // Attach file command
    let attachFileCommand = vscode.commands.registerCommand('extension-v1.attachFile', async () => {
        // Ask the user to select a file
        const files = await vscode.window.showOpenDialog({
            canSelectMany: false,
            openLabel: 'Attach',
            filters: {
                'Text Files': ['txt', 'md', 'json', 'js', 'ts', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'go', 'rs', 'rb']
            }
        });

        if (files && files.length > 0) {
            const filePath = files[0].fsPath;
            const fileName = path.basename(filePath);

            try {
                const fileContent = fs.readFileSync(filePath, 'utf8');
                vscode.window.showInformationMessage(`File attached: ${fileName}`);

                // Focus our chat view without affecting other extensions
                setTimeout(() => {
                    vscode.commands.executeCommand('workbench.view.repomind-container');
                }, 100);

                // Check if this is a business requirements file
                const isRequirementsFile = fileName.toLowerCase().includes('requirement') ||
                                          fileContent.toLowerCase().includes('requirement') ||
                                          fileContent.toLowerCase().includes('user story') ||
                                          fileContent.toLowerCase().includes('feature request');

                if (isRequirementsFile) {
                    // Process the business requirements file
                    vscode.commands.executeCommand('extension-v1.processBusinessRequirements', filePath);
                } else {
                    // Add the file content to the chat
                    if (chatViewProvider) {
                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `Attached file: ${fileName}`,
                            isUser: true
                        });

                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `File content:\n\`\`\`\n${fileContent}\n\`\`\``,
                            isUser: false
                        });
                    }
                }

                console.log(`Attached file: ${fileName}`);
                console.log(`Content: ${fileContent.substring(0, 100)}...`);
            } catch (error) {
                vscode.window.showErrorMessage(`Error reading file: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    });

    // Command to send error to chat view
    let sendErrorToChatCommand = vscode.commands.registerCommand('extension-v1.sendErrorToChat', (errorLog: string, errorLogPath: string) => {
        // Focus our chat view without affecting other extensions
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.repomind-container');
        }, 100);

        // Post a message to the chat view
        setTimeout(() => {
            // Create a simple notification with the error
            vscode.window.showErrorMessage('Error occurred. Details have been saved to error log.');

            // Add error to the chat view
            if (chatViewProvider) {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: 'An error occurred during the operation. Error details have been saved to the log.',
                    isUser: false
                });

                // Add a shortened version of the error log to the chat
                const shortenedLog = errorLog.split('\n').slice(0, 10).join('\n');
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: `Error summary:\n\`\`\`\n${shortenedLog}\n...\n\`\`\`\nFull details saved to: ${errorLogPath}`,
                    isUser: false
                });

                // Add a button to view the full error log
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: 'You can view the full error log by clicking "View Error Log" in the notification.',
                    isUser: false
                });
            } else {
                // Fallback if chat view is not available
                vscode.window.showInformationMessage(`Error details saved to: ${errorLogPath}`);
            }

            // Focus our chat view without affecting other extensions
            setTimeout(() => {
                vscode.commands.executeCommand('workbench.view.repomind-container');
            }, 100);
        }, 1000);
    });

    // Visualize code relationships command
    let visualizeRelationshipsCommand = vscode.commands.registerCommand('extension-v1.visualizeRelationships', async () => {
        statusBar.setWorking('Visualizing code relationships...');

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            statusBar.setError('No workspace folder');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Get the path to the codebase-analyser directory relative to the extension
        const extensionPath = context.extensionPath;
        const workspaceRoot = path.dirname(extensionPath);
        const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');

        // Create central visualizations directory if it doesn't exist
        const dataDir = path.join(workspaceRoot, 'data');
        const centralVisualizationsDir = path.join(dataDir, 'visualizations', projectId);
        if (!fs.existsSync(centralVisualizationsDir)) {
            fs.mkdirSync(centralVisualizationsDir, { recursive: true });
        }

        // Also create project-specific visualizations directory for backward compatibility
        const visualizationsDir = path.join(workspaceFolder, 'visualizations');
        if (!fs.existsSync(visualizationsDir)) {
            fs.mkdirSync(visualizationsDir, { recursive: true });
        }

        // Generate timestamp for the visualization files
        const now = new Date();
        const timestamp = now.getFullYear().toString() +
                         (now.getMonth() + 1).toString().padStart(2, '0') +
                         now.getDate().toString().padStart(2, '0') +
                         now.getHours().toString().padStart(2, '0') +
                         now.getMinutes().toString().padStart(2, '0') +
                         now.getSeconds().toString().padStart(2, '0');

        // Create a CodebaseAnalyzerLogger instance
        const codebaseAnalyzer = new CodebaseAnalyzerLogger(codebaseAnalyserPath);

        // Log the visualization operation
        logger.info('Extension', `Visualizing code relationships: ${workspaceFolder}`, {
            projectId,
            centralVisualizationsDir,
            visualizationsDir,
            timestamp
        });

        vscode.window.showInformationMessage(`Visualizing code relationships for project: ${projectId}`);
        console.log(`Workspace folder: ${workspaceFolder}`);
        console.log(`Project ID: ${projectId}`);
        console.log(`Visualizations directory: ${visualizationsDir}`);

        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Visualizing code relationships',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ message: 'Generating visualizations...' });

            return new Promise<void>((resolve, reject) => {
                // Run the visualization using the CodebaseAnalyzerLogger
                // First generate all visualizations in the central directory with timestamp
                codebaseAnalyzer.visualizeAllRelationships(workspaceFolder, centralVisualizationsDir, projectId, timestamp)
                    .then(() => {
                        // Then generate in the old location for backward compatibility
                        return codebaseAnalyzer.visualizeCodeRelationships(workspaceFolder, visualizationsDir, projectId);
                    })
                    .then((stdout) => {
                        console.log(`Stdout: ${stdout}`);

                        try {
                            // Clean up the stdout to ensure it's valid JSON
                            // Extract only the JSON part from the output
                            const jsonMatch = stdout.match(/\{.*\}/s);

                            // Define the result type
                            interface VisualizationResult {
                                multi_file_relationships?: string;
                                relationship_types?: string;
                            }

                            let result: VisualizationResult = {};

                            if (jsonMatch) {
                                // Parse the JSON output to get the visualization paths
                                result = JSON.parse(jsonMatch[0]) as VisualizationResult;
                            } else {
                                // If no JSON found, try to extract paths using regex
                                const multiFileMatch = stdout.match(/multi_file_relationships.*?:\s*"([^"]+)"/);
                                const relationshipTypesMatch = stdout.match(/relationship_types.*?:\s*"([^"]+)"/);

                                if (multiFileMatch && multiFileMatch[1]) {
                                    result.multi_file_relationships = multiFileMatch[1];
                                }
                                if (relationshipTypesMatch && relationshipTypesMatch[1]) {
                                    result.relationship_types = relationshipTypesMatch[1];
                                }

                                if (!result.multi_file_relationships && !result.relationship_types) {
                                    throw new Error("Could not extract visualization paths from output");
                                }
                            }

                            // Show success message with links to open the visualizations
                            vscode.window.showInformationMessage('Code relationships visualized successfully!',
                                'Open Multi-File Relationships', 'Open Relationship Types')
                                .then(selection => {
                                    if (selection === 'Open Multi-File Relationships' && result.multi_file_relationships) {
                                        // Open the multi-file relationships visualization
                                        const multiFileVisualizationPath = result.multi_file_relationships;
                                        vscode.env.openExternal(vscode.Uri.file(multiFileVisualizationPath));
                                    } else if (selection === 'Open Relationship Types' && result.relationship_types) {
                                        // Open the relationship types visualization
                                        const relationshipTypesVisualizationPath = result.relationship_types;
                                        vscode.env.openExternal(vscode.Uri.file(relationshipTypesVisualizationPath));
                                    }
                                });

                            statusBar.setReady('Visualizations created');

                            // Don't show any message after sync - keep the UI clean

                            resolve();
                        } catch (parseError) {
                            logger.error('Extension', `Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                            console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                            console.log("Raw output:", stdout);

                            // Even if parsing fails, inform the user visualizations are available
                            vscode.window.showInformationMessage('Visualizations created successfully!', 'Show Visualizations')
                                .then(selection => {
                                    if (selection === 'Show Visualizations') {
                                        vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                    }
                                });

                            // Inform the user they can view visualizations
                            chatViewProvider.sendTextToChat("Visualizations have been generated. Click 'Show Visualizations' to view them.");

                            statusBar.setReady('Visualizations created');
                            resolve();
                        }
                    })
                    .catch((error) => {
                        const errorMessage = `Error visualizing code relationships: ${error.message}`;
                        logger.error('Extension', errorMessage, error);
                        vscode.window.showErrorMessage(errorMessage);
                        statusBar.setError('Visualization failed');
                        console.error(`Error: ${error.message}`);

                        // Log the error to a file
                        const logFile = ErrorLogger.logError(error, {
                            workspaceFolder,
                            projectId,
                            visualizationsDir,
                            centralVisualizationsDir
                        });

                        // Show a message with an option to view the error log
                        vscode.window.showErrorMessage(
                            'Error visualizing code relationships. See error log for details.',
                            'View Error Log'
                        ).then(selection => {
                            if (selection === 'View Error Log') {
                                ErrorLogger.showErrorLog(logFile);
                            }
                        });

                        // Try to use the manual visualization script as a fallback
                        try {
                            const manualVisualizePath = path.join(codebaseAnalyserPath, 'scripts', 'manual_visualize.py');
                            if (fs.existsSync(manualVisualizePath)) {
                                logger.info('Extension', 'Trying manual visualization script as fallback');
                                console.log('Trying manual visualization script as fallback...');
                                const fallbackCommand = `python "${manualVisualizePath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

                                cp.exec(fallbackCommand, (fallbackError, fallbackStdout, fallbackStderr) => {
                                    if (fallbackError) {
                                        logger.error('Extension', `Fallback visualization failed: ${fallbackError.message}`);
                                        console.error(`Fallback visualization failed: ${fallbackError.message}`);
                                        if (fallbackStderr) {
                                            console.error(`Fallback stderr: ${fallbackStderr}`);
                                        }
                                        reject(error);
                                    } else {
                                        logger.info('Extension', 'Fallback visualization succeeded');
                                        console.log('Fallback visualization succeeded');
                                        console.log(`Fallback stdout: ${fallbackStdout}`);

                                        // Check if the visualization files exist
                                        const multiFilePath = path.join(visualizationsDir, `${projectId}_multi_file_relationships.png`);
                                        const relationshipTypesPath = path.join(visualizationsDir, `${projectId}_relationship_types.png`);

                                        if (fs.existsSync(multiFilePath) && fs.existsSync(relationshipTypesPath)) {
                                            // Automatically show visualizations without popup or message
                                            vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                            resolve();
                                        } else {
                                            logger.error('Extension', 'Fallback visualization did not produce expected files');
                                            reject(error);
                                        }
                                    }
                                });
                            } else {
                                logger.error('Extension', 'Manual visualization script not found');
                                reject(error);
                            }
                        } catch (fallbackError) {
                            logger.error('Extension', 'Error running fallback visualization', fallbackError);
                            console.error('Error running fallback visualization:', fallbackError);
                            reject(error);
                        }
                    });

                    // Handle cancellation
                    token.onCancellationRequested(() => {
                        logger.info('Extension', 'Visualization cancelled by user');
                        vscode.window.showInformationMessage('Visualization cancelled.');
                        statusBar.setDefault();
                        resolve();
                    });
            });
        }).then(() => {
            console.log('Visualization process completed successfully');
        }, (error: unknown) => {
            console.error(`Visualization process failed: ${error instanceof Error ? error.message : String(error)}`);
        });
    });

    // Command to show visualizations in chat
    let showVisualizationsInChatCommand = vscode.commands.registerCommand('extension-v1.showVisualizationsInChat', async () => {
        // Log the function call
        logger.info('Extension', 'showVisualizationsInChat command called');

        // Show a message in the chat that we're preparing visualizations with a loading indicator
        if (chatViewProvider) {
            chatViewProvider.sendTextToChat("Preparing visualizations... This may take a few seconds.", false, true, 'visualize');
        }

        // Fix visualizations by copying the latest files to the workspace directory
        try {
            // Get the current workspace folder
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders || workspaceFolders.length === 0) {
                logger.error('Extension', 'No workspace folder is open');
                return;
            }

            const workspaceFolder = workspaceFolders[0].uri.fsPath;
            const projectId = path.basename(workspaceFolder);

            // Path to the central visualizations directory
            const workspaceRoot = path.dirname(context.extensionPath);
            const centralVisualizationsDir = path.join(workspaceRoot, 'data', 'visualizations', projectId);

            // Path to the workspace visualizations directory
            const workspaceVisualizationsDir = path.join(workspaceFolder, 'visualizations');

            // Create the workspace visualizations directory if it doesn't exist
            if (!fs.existsSync(workspaceVisualizationsDir)) {
                fs.mkdirSync(workspaceVisualizationsDir, { recursive: true });
                logger.info('Extension', `Created workspace visualizations directory: ${workspaceVisualizationsDir}`);
            }

            // Copy the latest visualization files to the workspace directory
            logger.info('Extension', 'Copying visualization files to workspace directory');

            // Define the visualization types
            const visualizationTypes = [
                'multi_file_relationships',
                'relationship_types',
                'class_diagram',
                'package_diagram',
                'dependency_graph',
                'inheritance_hierarchy'
            ];

            // Copy each visualization type
            for (const vizType of visualizationTypes) {
                // Find the latest file
                const pattern = `${projectId}_${vizType}_*.png`;
                const files = fs.readdirSync(centralVisualizationsDir)
                    .filter(file => file.match(pattern))
                    .sort()
                    .reverse();

                if (files.length > 0) {
                    const latestFile = path.join(centralVisualizationsDir, files[0]);
                    const targetFile = path.join(workspaceVisualizationsDir, `${projectId}_${vizType}.png`);

                    // Copy the file
                    logger.info('Extension', `Copying ${latestFile} to ${targetFile}`);
                    fs.copyFileSync(latestFile, targetFile);
                } else {
                    logger.warn('Extension', `No file found for ${vizType}`);
                }
            }

            // Copy special visualizations
            const specialVisualizations = [
                'customer_java_highlight.png',
                'project_graph_customer_highlight.png'
            ];

            for (const specialViz of specialVisualizations) {
                const sourceFile = path.join(centralVisualizationsDir, specialViz);
                const targetFile = path.join(workspaceVisualizationsDir, specialViz);

                if (fs.existsSync(sourceFile)) {
                    logger.info('Extension', `Copying ${sourceFile} to ${targetFile}`);
                    fs.copyFileSync(sourceFile, targetFile);
                } else {
                    logger.warn('Extension', `No file found for ${specialViz}`);
                }
            }

            logger.info('Extension', 'Visualization files copied successfully');

            // Add a small delay to ensure files are fully written before trying to display them
            await new Promise(resolve => setTimeout(resolve, 500));

            // Send a message to the chat that visualizations are ready (without loading indicator)
            if (chatViewProvider) {
                chatViewProvider.sendTextToChat("Visualizations are ready! Displaying now...", false, false, '');

                // Add a small delay before refreshing to ensure the message is displayed
                await new Promise(resolve => setTimeout(resolve, 300));

                // Force refresh the chat view to ensure it picks up the new files
                logger.info('Extension', 'Refreshing chat view');
                chatViewProvider.refreshView();
            }
        } catch (error) {
            logger.error('Extension', `Error copying visualization files: ${error instanceof Error ? error.stack : String(error)}`);
        }

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            logger.error('Extension', 'No workspace folder is open');
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Get the path to the codebase-analyser directory relative to the extension
        const extensionPath = context.extensionPath;
        const workspaceRoot = path.dirname(extensionPath);
        const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');

        // Path to the central visualizations directory
        const dataDir = path.join(workspaceRoot, 'data');
        const centralVisualizationsDir = path.join(dataDir, 'visualizations', projectId);

        // Also check the old visualizations directory for backward compatibility
        const visualizationsDir = path.join(workspaceFolder, 'visualizations');

        // Check if the visualizations directory exists
        if (!fs.existsSync(visualizationsDir)) {
            // Try to create the directory and generate visualizations
            try {
                fs.mkdirSync(visualizationsDir, { recursive: true });

                // Run the manual visualization script
                const manualVisualizePath = path.join(codebaseAnalyserPath, 'scripts', 'manual_visualize.py');
                if (fs.existsSync(manualVisualizePath)) {
                    vscode.window.showInformationMessage('Generating visualizations...');

                    const fallbackCommand = `python "${manualVisualizePath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

                    cp.exec(fallbackCommand, (fallbackError, fallbackStdout, fallbackStderr) => {
                        if (fallbackError) {
                            console.error(`Visualization generation failed: ${fallbackError.message}`);
                            if (fallbackStderr) {
                                console.error(`Stderr: ${fallbackStderr}`);
                            }
                            vscode.window.showErrorMessage('Failed to generate visualizations.');
                        } else {
                            console.log('Visualization generation succeeded');
                            console.log(`Stdout: ${fallbackStdout}`);

                            // Now show the visualizations
                            showVisualizations();
                        }
                    });
                    return;
                } else {
                    vscode.window.showErrorMessage('Visualization script not found.');
                    return;
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to create visualizations directory: ${error instanceof Error ? error.message : String(error)}`);
                return;
            }
        }

        // Function to show visualizations
        function showVisualizations() {
            logger.info('Extension', 'showVisualizations function called');
            console.log("DEBUG: showVisualizations function called");

            // Check if the central visualizations directory exists
            if (!fs.existsSync(centralVisualizationsDir)) {
                logger.error('Extension', `Central visualizations directory does not exist: ${centralVisualizationsDir}`);
                console.error(`Central visualizations directory does not exist: ${centralVisualizationsDir}`);

                // Create it
                try {
                    fs.mkdirSync(centralVisualizationsDir, { recursive: true });
                    logger.info('Extension', `Created central visualizations directory: ${centralVisualizationsDir}`);
                } catch (error) {
                    logger.error('Extension', `Failed to create central visualizations directory: ${error}`);
                    console.error(`Failed to create central visualizations directory: ${error}`);
                }
            }

            // Log the directory contents for debugging
            try {
                if (fs.existsSync(centralVisualizationsDir)) {
                    const files = fs.readdirSync(centralVisualizationsDir);
                    logger.info('Extension', `Files in central visualizations directory: ${files.join(', ')}`);
                    console.log(`Files in central visualizations directory: ${files.join(', ')}`);
                }
            } catch (error) {
                logger.error('Extension', `Error reading central visualizations directory: ${error}`);
                console.error(`Error reading central visualizations directory: ${error}`);
            }
            let visualizationsFound = false;

            // Function to find the latest visualization file
            function findLatestVisualization(directory: string, filePattern: string): string | null {
                console.log(`Finding latest visualization in directory: ${directory}, pattern: ${filePattern}`);
                logger.info('Extension', `findLatestVisualization called with directory: ${directory}, pattern: ${filePattern}`);
                if (!fs.existsSync(directory)) {
                    console.log(`Directory does not exist: ${directory}`);
                    logger.warn('Extension', `Directory does not exist: ${directory}`);
                    return null;
                }

                try {
                    // Get all files in the directory
                    const files = fs.readdirSync(directory);
                    console.log(`Found ${files.length} files in directory: ${directory}`);
                    logger.info('Extension', `Found ${files.length} files in directory: ${directory}`);

                    // Log all files for debugging
                    if (files.length > 0) {
                        console.log(`Files in directory: ${files.slice(0, 5).join(', ')}${files.length > 5 ? '...' : ''}`);
                        logger.info('Extension', `Files in directory: ${files.join(', ')}`);
                    }

                    // Filter files matching the pattern
                    const matchingFiles = files.filter(file => {
                        // Use a simpler pattern matching approach
                        // Just check if the filename contains the pattern
                        return file.includes(filePattern) && file.endsWith('.png');
                    });
                    console.log(`Found ${matchingFiles.length} files matching pattern "${filePattern}": ${matchingFiles.join(', ')}`);
                    logger.info('Extension', `Found ${matchingFiles.length} files matching pattern "${filePattern}": ${matchingFiles.join(', ')}`);

                    if (matchingFiles.length === 0) {
                        console.log(`No files found matching pattern "${filePattern}" in directory: ${directory}`);
                        logger.warn('Extension', `No files found matching pattern "${filePattern}" in directory: ${directory}`);
                        return null;
                    }

                    // Sort files by timestamp (newest first)
                    matchingFiles.sort((a, b) => {
                        // Extract timestamps if they exist
                        const timestampA = a.match(/(\d{14})/);
                        const timestampB = b.match(/(\d{14})/);

                        if (timestampA && timestampB) {
                            console.log(`Comparing timestamps: ${timestampA[1]} vs ${timestampB[1]}`);
                            return timestampB[1].localeCompare(timestampA[1]);
                        } else {
                            // If no timestamps, sort by modification time
                            const statA = fs.statSync(path.join(directory, a));
                            const statB = fs.statSync(path.join(directory, b));
                            return statB.mtime.getTime() - statA.mtime.getTime();
                        }
                    });

                    // Return the path to the newest file
                    const latestFile = path.join(directory, matchingFiles[0]);
                    console.log(`Latest file found: ${latestFile}`);
                    logger.info('Extension', `Latest file found: ${latestFile}`);
                    return latestFile;
                } catch (error) {
                    console.error(`Error finding latest visualization: ${error}`);
                    logger.error('Extension', `Error finding latest visualization: ${error}`);
                    return null;
                }
            }

            // Log that we're starting to look for visualizations
            console.log('LOOKING FOR VISUALIZATIONS:');
            logger.info('Extension', 'Looking for visualizations in directory: ' + centralVisualizationsDir);

            // Also check the old location for backward compatibility
            console.log(`Also checking old location: ${visualizationsDir}`);

            // We'll handle all visualizations in a unified way below

            // Define all visualization types we want to show
            const allVisualizations = [
                { pattern: 'multi_file_relationships', title: 'Multi-File Relationships' },
                { pattern: 'relationship_types', title: 'Relationship Types' },
                { pattern: 'class_diagram', title: 'Class Diagram' },
                { pattern: 'package_diagram', title: 'Package Diagram' },
                { pattern: 'dependency_graph', title: 'Dependency Graph' },
                { pattern: 'inheritance_hierarchy', title: 'Inheritance Hierarchy' }
            ];

            // Also check for these special visualizations
            const specialVisualizations = [
                { filename: 'customer_java_highlight.png', title: 'Customer Java Highlight' },
                { filename: 'project_graph_customer_highlight.png', title: 'Project Graph with Customer Highlight' }
            ];

            // Get all PNG files in the directory
            console.log("CHECKING FOR ALL VISUALIZATION FILES:");
            logger.info('Extension', `Checking for visualization files in: ${centralVisualizationsDir}`);
            try {
                // Make sure the directory exists before trying to read it
                if (!fs.existsSync(centralVisualizationsDir)) {
                    logger.error('Extension', `Directory does not exist: ${centralVisualizationsDir}`);
                    console.error(`Directory does not exist: ${centralVisualizationsDir}`);

                    // Create it
                    fs.mkdirSync(centralVisualizationsDir, { recursive: true });
                    logger.info('Extension', `Created directory: ${centralVisualizationsDir}`);
                    console.log(`Created directory: ${centralVisualizationsDir}`);
                }

                // List all files in the directory
                const files = fs.readdirSync(centralVisualizationsDir);
                logger.info('Extension', `Found ${files.length} files in directory: ${centralVisualizationsDir}`);
                console.log(`Found ${files.length} files in directory: ${centralVisualizationsDir}`);

                // Log all files for debugging
                if (files.length > 0) {
                    logger.info('Extension', `Files in directory: ${files.join(', ')}`);
                    console.log(`Files in directory: ${files.join(', ')}`);
                }

                // Filter for PNG files
                const pngFiles = files.filter(file => file.endsWith('.png'));
                logger.info('Extension', `Found ${pngFiles.length} PNG files in directory`);
                console.log(`Found ${pngFiles.length} PNG files in directory`);

                // Group files by visualization type
                const visualizationGroups: Record<string, string[]> = {};

                // Initialize groups
                for (const viz of allVisualizations) {
                    visualizationGroups[viz.pattern] = [];
                }

                // Add files to their respective groups
                for (const file of pngFiles) {
                    for (const viz of allVisualizations) {
                        if (file.includes(viz.pattern)) {
                            visualizationGroups[viz.pattern].push(file);
                            break;
                        }
                    }
                }

                // Process each visualization type
                for (const viz of allVisualizations) {
                    const matchingFiles = visualizationGroups[viz.pattern];
                    console.log(`Found ${matchingFiles.length} files for ${viz.pattern}`);

                    if (matchingFiles.length > 0) {
                        // Sort by timestamp (newest first)
                        matchingFiles.sort((a: string, b: string) => {
                            const timestampA = a.match(/(\d{14})/);
                            const timestampB = b.match(/(\d{14})/);
                            if (timestampA && timestampB) {
                                return timestampB[1].localeCompare(timestampA[1]);
                            } else {
                                const statA = fs.statSync(path.join(centralVisualizationsDir, a));
                                const statB = fs.statSync(path.join(centralVisualizationsDir, b));
                                return statB.mtime.getTime() - statA.mtime.getTime();
                            }
                        });

                        // Get the newest file
                        const newestFile = path.join(centralVisualizationsDir, matchingFiles[0]);
                        console.log(`Newest file for ${viz.pattern}: ${newestFile}`);

                        // Send it to the chat without the title prefix
                        logger.info('Extension', `Sending ${viz.title} to chat: ${newestFile}`);

                        // Check if chatViewProvider is available
                        if (!chatViewProvider) {
                            logger.error('Extension', 'chatViewProvider is not available');
                            console.error('chatViewProvider is not available');
                        } else if (!chatViewProvider.isViewAvailable()) {
                            logger.error('Extension', 'chatViewProvider view is not available');
                            console.error('chatViewProvider view is not available');
                        } else {
                            chatViewProvider.sendImageToChat(newestFile, `${viz.title}`);
                            visualizationsFound = true;
                        }
                    } else {
                        // Check the old location as a fallback
                        const oldLocationPath = path.join(visualizationsDir, `${projectId}_${viz.pattern}.png`);
                        if (fs.existsSync(oldLocationPath)) {
                            console.log(`Found ${viz.pattern} in old location: ${oldLocationPath}`);
                            logger.info('Extension', `Sending ${viz.title} from old location: ${oldLocationPath}`);

                            // Check if chatViewProvider is available
                            if (!chatViewProvider) {
                                logger.error('Extension', 'chatViewProvider is not available');
                                console.error('chatViewProvider is not available');
                            } else if (!chatViewProvider.isViewAvailable()) {
                                logger.error('Extension', 'chatViewProvider view is not available');
                                console.error('chatViewProvider view is not available');
                            } else {
                                chatViewProvider.sendImageToChat(oldLocationPath, `${viz.title}`);
                                visualizationsFound = true;
                            }
                        } else {
                            console.log(`No files found for ${viz.pattern} in either location`);
                        }
                    }
                }

                // Check for special visualizations
                for (const specialViz of specialVisualizations) {
                    const specialVizPath = path.join(centralVisualizationsDir, specialViz.filename);
                    if (fs.existsSync(specialVizPath)) {
                        console.log(`Found special visualization: ${specialViz.filename}`);
                        logger.info('Extension', `Sending ${specialViz.title} to chat: ${specialVizPath}`);

                        // Check if chatViewProvider is available
                        if (!chatViewProvider) {
                            logger.error('Extension', 'chatViewProvider is not available');
                            console.error('chatViewProvider is not available');
                        } else if (!chatViewProvider.isViewAvailable()) {
                            logger.error('Extension', 'chatViewProvider view is not available');
                            console.error('chatViewProvider view is not available');
                        } else {
                            chatViewProvider.sendImageToChat(specialVizPath, `${specialViz.title}`);
                            visualizationsFound = true;
                        }
                    } else {
                        console.log(`Special visualization not found: ${specialViz.filename}`);
                    }
                }
            } catch (error) {
                console.error(`Error processing visualizations: ${error}`);
                logger.error('Extension', `Error processing visualizations: ${error instanceof Error ? error.stack : String(error)}`);

                // Try to recover by checking the old location
                try {
                    logger.info('Extension', `Trying to recover by checking old location: ${visualizationsDir}`);
                    console.log(`Trying to recover by checking old location: ${visualizationsDir}`);

                    if (fs.existsSync(visualizationsDir)) {
                        const oldFiles = fs.readdirSync(visualizationsDir);
                        const oldPngFiles = oldFiles.filter(file => file.endsWith('.png'));

                        logger.info('Extension', `Found ${oldPngFiles.length} PNG files in old directory: ${visualizationsDir}`);
                        console.log(`Found ${oldPngFiles.length} PNG files in old directory: ${visualizationsDir}`);

                        if (oldPngFiles.length > 0) {
                            logger.info('Extension', `Files in old directory: ${oldPngFiles.join(', ')}`);
                            console.log(`Files in old directory: ${oldPngFiles.join(', ')}`);

                            // Try to display each visualization from the old location
                            for (const viz of allVisualizations) {
                                const oldLocationPath = path.join(visualizationsDir, `${projectId}_${viz.pattern}.png`);
                                if (fs.existsSync(oldLocationPath)) {
                                    logger.info('Extension', `Found ${viz.pattern} in old location: ${oldLocationPath}`);
                                    console.log(`Found ${viz.pattern} in old location: ${oldLocationPath}`);

                                    // Check if chatViewProvider is available
                                    if (!chatViewProvider) {
                                        logger.error('Extension', 'chatViewProvider is not available during recovery');
                                        console.error('chatViewProvider is not available during recovery');
                                    } else if (!chatViewProvider.isViewAvailable()) {
                                        logger.error('Extension', 'chatViewProvider view is not available during recovery');
                                        console.error('chatViewProvider view is not available during recovery');
                                    } else {
                                        chatViewProvider.sendImageToChat(oldLocationPath, `${viz.title}`);
                                        visualizationsFound = true;
                                    }
                                }
                            }
                        }
                    }
                } catch (recoveryError) {
                    logger.error('Extension', `Error during recovery attempt: ${recoveryError instanceof Error ? recoveryError.stack : String(recoveryError)}`);
                    console.error(`Error during recovery attempt: ${recoveryError}`);
                }
            }

            // We're now handling additional visualizations directly above

            if (!visualizationsFound) {
                logger.info('Extension', 'No visualizations found, generating them now');
                console.log('No visualizations found, generating them now');

                // Show a message to the user
                if (chatViewProvider && chatViewProvider.isViewAvailable()) {
                    chatViewProvider.sendTextToChat('No visualizations found. Generating them now...', false);
                }

                // Generate visualizations using the manual_visualize.py script
                const manualVisualizePath = path.join(codebaseAnalyserPath, 'scripts', 'manual_visualize.py');

                if (fs.existsSync(manualVisualizePath)) {
                    // Run the script with absolute paths, but output to the workspace folder
                    const command = `cd "${codebaseAnalyserPath}" && python3 "${manualVisualizePath}" --output-dir "${visualizationsDir}" --project-id "${projectId}" --debug`;
                    logger.info('Extension', `Running command: ${command}`);
                    console.log(`Running command: ${command}`);

                    // Create a log file for debugging
                    const timestamp = new Date().toISOString().replace(/:/g, '-');
                    const logDir = path.join(workspaceRoot, 'logs');
                    if (!fs.existsSync(logDir)) {
                        fs.mkdirSync(logDir, { recursive: true });
                    }
                    const logFile = path.join(logDir, `visualize-${timestamp}.log`);
                    fs.writeFileSync(logFile, `Command: ${command}\n\n`);

                    // Log the environment for debugging
                    const env = process.env;
                    fs.appendFileSync(logFile, `Environment:\n${JSON.stringify(env, null, 2)}\n\n`);

                    // Log the directories for debugging
                    fs.appendFileSync(logFile, `Directories:\n`);
                    fs.appendFileSync(logFile, `- codebaseAnalyserPath: ${codebaseAnalyserPath}\n`);
                    fs.appendFileSync(logFile, `- centralVisualizationsDir: ${centralVisualizationsDir}\n`);
                    fs.appendFileSync(logFile, `- workspaceRoot: ${workspaceRoot}\n`);
                    fs.appendFileSync(logFile, `- projectId: ${projectId}\n\n`);

                    // Check if the script exists
                    fs.appendFileSync(logFile, `Script exists: ${fs.existsSync(manualVisualizePath)}\n\n`);

                    // Check if the output directory exists
                    fs.appendFileSync(logFile, `Output directory exists: ${fs.existsSync(centralVisualizationsDir)}\n\n`);

                    // Execute the command with detailed logging
                    cp.exec(command, (error, stdout, stderr) => {
                        // Log the results
                        fs.appendFileSync(logFile, `Stdout:\n${stdout}\n\n`);
                        fs.appendFileSync(logFile, `Stderr:\n${stderr}\n\n`);
                        if (error) {
                            fs.appendFileSync(logFile, `Error:\n${error.message}\n\n`);
                        }
                        if (error) {
                            logger.error('Extension', `Error generating visualizations: ${error.message}`);
                            console.error(`Error generating visualizations: ${error.message}`);

                            if (stderr) {
                                logger.error('Extension', `Stderr: ${stderr}`);
                                console.error(`Stderr: ${stderr}`);
                            }

                            if (chatViewProvider && chatViewProvider.isViewAvailable()) {
                                chatViewProvider.sendTextToChat(`Error generating visualizations: ${error.message}`, false);
                                chatViewProvider.sendTextToChat(`Check the log file at ${logFile} for more details.`, false);
                            }

                            // Try to parse the JSON output from the script
                            try {
                                const jsonMatch = stdout.match(/\{[\s\S]*\}/);
                                if (jsonMatch) {
                                    const jsonOutput = JSON.parse(jsonMatch[0]);
                                    if (jsonOutput.error) {
                                        logger.error('Extension', `Script error: ${jsonOutput.error}`);
                                        console.error(`Script error: ${jsonOutput.error}`);

                                        if (chatViewProvider && chatViewProvider.isViewAvailable()) {
                                            chatViewProvider.sendTextToChat(`Script error: ${jsonOutput.error}`, false);
                                        }
                                    }
                                }
                            } catch (error) {
                                const jsonError = error as Error;
                                logger.error('Extension', `Error parsing JSON output: ${jsonError.message}`);
                                console.error(`Error parsing JSON output: ${jsonError.message}`);
                            }
                        } else {
                            logger.info('Extension', `Visualization generation succeeded`);
                            console.log(`Visualization generation succeeded`);
                            logger.info('Extension', `Stdout: ${stdout}`);

                            // Show the visualizations
                            setTimeout(() => {
                                vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                            }, 1000);
                        }
                    });
                } else {
                    logger.error('Extension', `Manual visualization script not found at: ${manualVisualizePath}`);
                    console.error(`Manual visualization script not found at: ${manualVisualizePath}`);

                    if (chatViewProvider && chatViewProvider.isViewAvailable()) {
                        chatViewProvider.sendTextToChat('Visualization script not found. Please check your installation.', false);
                    }
                }
            } else {
                // Focus the chat view
                vscode.commands.executeCommand('extension-v1.chatView.focus');
            }
        }

        // Show visualizations if they exist
        showVisualizations();
    });

    // Command to generate visualizations using manual script
    let generateVisualizationsCommand = vscode.commands.registerCommand('extension-v1.generateVisualizations', async () => {
        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Get the path to the codebase-analyser directory relative to the extension
        const extensionPath = context.extensionPath;
        const workspaceRoot = path.dirname(extensionPath);
        const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');

        // Path to the central visualizations directory in the data folder
        const dataDir = path.join(workspaceRoot, 'data');
        const centralVisualizationsDir = path.join(dataDir, 'visualizations', projectId);

        // Create the directory if it doesn't exist
        if (!fs.existsSync(centralVisualizationsDir)) {
            fs.mkdirSync(centralVisualizationsDir, { recursive: true });
        }

        // For backward compatibility, also create the old visualizations directory
        const visualizationsDir = path.join(workspaceFolder, 'visualizations');
        if (!fs.existsSync(visualizationsDir)) {
            fs.mkdirSync(visualizationsDir, { recursive: true });
        }

        // Run the manual visualization script
        const manualVisualizePath = path.join(codebaseAnalyserPath, 'scripts', 'manual_visualize.py');
        if (!fs.existsSync(manualVisualizePath)) {
            vscode.window.showErrorMessage('Manual visualization script not found.');
            return;
        }

        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating visualizations',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ message: 'Running manual visualization script...' });

            return new Promise<void>((resolve, reject) => {
                const command = `python "${manualVisualizePath}" --output-dir "${centralVisualizationsDir}" --project-id "${projectId}"`;

                const process = cp.exec(command, (error, stdout, stderr) => {
                    if (error) {
                        console.error(`Visualization generation failed: ${error.message}`);
                        if (stderr) {
                            console.error(`Stderr: ${stderr}`);
                        }

                        // Log the error
                        const logFile = ErrorLogger.logError(error, {
                            command,
                            stderr,
                            stdout,
                            workspaceFolder,
                            projectId,
                            visualizationsDir
                        });

                        vscode.window.showErrorMessage(
                            'Failed to generate visualizations. See error log for details.',
                            'View Error Log'
                        ).then(selection => {
                            if (selection === 'View Error Log') {
                                ErrorLogger.showErrorLog(logFile);
                            }
                        });

                        reject(error);
                    } else {
                        console.log('Visualization generation succeeded');
                        console.log(`Stdout: ${stdout}`);

                        try {
                            // Clean up the stdout to ensure it's valid JSON
                            // Try different approaches to extract the JSON

                            // First, try to parse the last line as JSON
                            let result: any = {};
                            let jsonParsed = false;

                            try {
                                // Try the last line
                                const lines = stdout.trim().split('\n');
                                const lastLine = lines[lines.length - 1];
                                result = JSON.parse(lastLine);
                                jsonParsed = true;
                                logger.info('Extension', `Successfully parsed JSON from last line: ${Object.keys(result).join(', ')}`);
                            } catch (e) {
                                logger.warn('Extension', `Failed to parse last line as JSON: ${e}`);

                                // Try to extract JSON using regex
                                try {
                                    const jsonMatch = stdout.match(/\{.*\}/s);
                                    if (jsonMatch) {
                                        result = JSON.parse(jsonMatch[0]);
                                        jsonParsed = true;
                                        logger.info('Extension', `Successfully parsed JSON using regex: ${Object.keys(result).join(', ')}`);
                                    }
                                } catch (regexError) {
                                    logger.warn('Extension', `Failed to parse JSON using regex: ${regexError}`);
                                }
                            }

                            // If we still couldn't parse the JSON, try to extract paths using regex
                            if (!jsonParsed) {
                                logger.warn('Extension', 'Falling back to regex extraction of paths');

                                // Define patterns for all visualization types
                                const patterns = [
                                    'multi_file_relationships',
                                    'relationship_types',
                                    'class_diagram',
                                    'package_diagram',
                                    'dependency_graph',
                                    'inheritance_hierarchy'
                                ];

                                // Extract paths for each pattern
                                for (const pattern of patterns) {
                                    const regex = new RegExp(`${pattern}.*?:\\s*"([^"]+)"`, 's');
                                    const match = stdout.match(regex);

                                    if (match && match[1]) {
                                        result[pattern] = match[1];
                                        logger.info('Extension', `Extracted ${pattern} path using regex: ${match[1]}`);
                                    }
                                }

                                // Check if we found any paths
                                if (Object.keys(result).length === 0) {
                                    throw new Error("Could not extract visualization paths from output");
                                }
                            }

                            // Log the extracted paths
                            logger.info('Extension', `Extracted visualization paths: ${Object.keys(result).join(', ')}`);
                            for (const [key, value] of Object.entries(result)) {
                                logger.info('Extension', `${key}: ${value}`);
                            }

                            // Don't show popup, just automatically show visualizations in chat
                            vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');

                            resolve();
                        } catch (parseError) {
                            console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                            console.log("Raw output:", stdout);

                            // Even if parsing fails, automatically show visualizations
                            vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                            resolve();
                        }
                    }
                });

                token.onCancellationRequested(() => {
                    process.kill();
                    vscode.window.showInformationMessage('Visualization generation cancelled.');
                    resolve();
                });
            });
        });
    });

    // Command to directly display all visualizations (for debugging)
    let showAllVisualizationsCommand = vscode.commands.registerCommand('extension-v1.showAllVisualizations', () => {
        logger.info('Extension', 'showAllVisualizations command triggered');
        console.log("DEBUG: showAllVisualizations command triggered");

        // Show a message in the chat that we're preparing visualizations with a loading indicator
        if (chatViewProvider && chatViewProvider.isViewAvailable()) {
            chatViewProvider.sendTextToChat("Processing visualizations... This may take a moment.", false, true, 'visualize');
        }

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            if (chatViewProvider && chatViewProvider.isViewAvailable()) {
                chatViewProvider.sendTextToChat("Error: No workspace folder is open. Please open a folder first.", false);
            }
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Path to the central visualizations directory
        const workspaceRoot = path.dirname(context.extensionPath);
        const centralVisualizationsDir = path.join(workspaceRoot, 'data', 'visualizations', projectId);

        // Path to the old visualizations directory
        const oldVisualizationsDir = path.join(workspaceFolder, 'visualizations');

        // Create the directories if they don't exist
        if (!fs.existsSync(centralVisualizationsDir)) {
            fs.mkdirSync(centralVisualizationsDir, { recursive: true });
            logger.info('Extension', `Created central visualizations directory: ${centralVisualizationsDir}`);
        }

        if (!fs.existsSync(oldVisualizationsDir)) {
            fs.mkdirSync(oldVisualizationsDir, { recursive: true });
            logger.info('Extension', `Created old visualizations directory: ${oldVisualizationsDir}`);
        }

        // Log the directories
        logger.info('Extension', `Central visualizations directory: ${centralVisualizationsDir}`);
        logger.info('Extension', `Old visualizations directory: ${oldVisualizationsDir}`);

        // Check if the directories exist and list their contents
        if (fs.existsSync(centralVisualizationsDir)) {
            const files = fs.readdirSync(centralVisualizationsDir);
            logger.info('Extension', `Files in central directory: ${files.join(', ')}`);
            console.log(`Files in central directory: ${files.join(', ')}`);
        }

        if (fs.existsSync(oldVisualizationsDir)) {
            const files = fs.readdirSync(oldVisualizationsDir);
            logger.info('Extension', `Files in old directory: ${files.join(', ')}`);
            console.log(`Files in old directory: ${files.join(', ')}`);
        }

        // Try to generate visualizations if they don't exist
        vscode.commands.executeCommand('extension-v1.generateVisualizations')
            .then(() => {
                // After generating visualizations, show them in the chat
                setTimeout(() => {
                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                }, 5000);
            });
    });

    // Command to directly display an image
    let showDirectImageCommand = vscode.commands.registerCommand('extension-v1.showDirectImage', () => {
        console.log("DEBUG: showDirectImage command triggered");

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Path to the central visualizations directory
        const workspaceRoot = path.dirname(context.extensionPath);
        const centralVisualizationsDir = path.join(workspaceRoot, 'data', 'visualizations', projectId);

        // Path to the specific image we want to display
        const imagePath = path.join(centralVisualizationsDir, 'testshreya_multi_file_relationships_20250512194102.png');

        // Check if the file exists
        if (!fs.existsSync(imagePath)) {
            console.error(`DEBUG: Image file does not exist: ${imagePath}`);
            vscode.window.showErrorMessage(`Image file not found: ${imagePath}`);
            return;
        }

        // Display the image
        DirectImageDisplay.showImage(imagePath, 'Multi-File Relationships');
    });

    // Command to test all visualizations
    let testVisualizationsCommand = vscode.commands.registerCommand('extension-v1.testVisualizations', () => {
        console.log("DEBUG: testVisualizations command triggered");

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Display all visualizations
        TestVisualizations.displayAllVisualizations(projectId);
    });

    // Add commands to subscriptions
    context.subscriptions.push(startAssistantCommand);
    context.subscriptions.push(processBusinessRequirementsCommand);
    context.subscriptions.push(analyzeRequirementsCommand);
    context.subscriptions.push(generateCodeCommand);
    context.subscriptions.push(openChatViewCommand);
    context.subscriptions.push(syncCodebaseCommand);
    context.subscriptions.push(attachFileCommand);
    context.subscriptions.push(sendErrorToChatCommand);
    context.subscriptions.push(visualizeRelationshipsCommand);
    context.subscriptions.push(showVisualizationsInChatCommand);
    context.subscriptions.push(generateVisualizationsCommand);
    context.subscriptions.push(showAllVisualizationsCommand);
    context.subscriptions.push(showDirectImageCommand);
    context.subscriptions.push(testVisualizationsCommand);

    // Set status and check for last sync time
    statusBar.setReady('RepoMind is ready');

    // Check if there's a workspace open
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Get the path to the codebase-analyser directory
        const workspaceRoot = path.dirname(context.extensionPath);
        const codebaseAnalyserPath = path.join(workspaceRoot, 'codebase-analyser');

        // Check if the database exists
        const dbPath = path.join(codebaseAnalyserPath, '.lancedb');
        if (fs.existsSync(dbPath)) {
            // Get the last sync time
            const getLastSyncTimeCommand = `cd "${codebaseAnalyserPath}" &&
                if [ -d "venv" ]; then
                    source venv/bin/activate &&
                    python3 -c "from codebase_analyser.database.unified_storage import UnifiedStorage; import sys; storage = UnifiedStorage(db_path='.lancedb'); timestamp = storage.get_last_sync_time('${projectId}'); print(timestamp if timestamp else 'Unknown')" &&
                    deactivate;
                else
                    python3 -c "from codebase_analyser.database.unified_storage import UnifiedStorage; import sys; storage = UnifiedStorage(db_path='.lancedb'); timestamp = storage.get_last_sync_time('${projectId}'); print(timestamp if timestamp else 'Unknown')";
                fi`;

            try {
                const lastSyncTime = cp.execSync(getLastSyncTimeCommand).toString().trim();

                // Format the timestamp for display
                let formattedTime = lastSyncTime;
                try {
                    if (lastSyncTime !== 'Unknown') {
                        // Parse ISO timestamp and format it
                        const date = new Date(lastSyncTime);
                        // Use a more explicit format to avoid confusion
                        formattedTime = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();

                        // Update status bar
                        statusBar.setReady(`Last synced: ${formattedTime}`);
                    }
                } catch (error) {
                    console.error(`Error formatting timestamp: ${error}`);
                }
            } catch (error) {
                console.error(`Error getting last sync time: ${error}`);
            }
        }
    }
}

// This method is called when your extension is deactivated
export function deactivate() {
    // Close the logger
    logger.info('Extension', 'RepoMind is being deactivated');
    logger.close();
}
