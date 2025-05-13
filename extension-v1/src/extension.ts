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

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {
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
            vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
        }, 100);
        statusBar.setReady('RepoMind is ready');
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
            vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
        }, 100);
    });

    // Sync codebase command
    let syncCodebaseCommand = vscode.commands.registerCommand('extension-v1.syncCodebase', async () => {
        // Make sure we stay in our extension view
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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

        // Use the appropriate script based on whether we need a full sync or incremental update
        let command;
        if (isFullSync) {
            // Use analyze_java.py for full sync
            command = `cd "${codebaseAnalyserPath}" &&
                if [ -d "venv" ]; then
                    source venv/bin/activate &&
                    python3 scripts/analyze_java.py "${workspaceFolder}" --clear-db --mock-embeddings --project-id "${projectId}" &&
                    deactivate;
                else
                    python3 scripts/analyze_java.py "${workspaceFolder}" --clear-db --mock-embeddings --project-id "${projectId}";
                fi`;

            vscode.window.showInformationMessage(`Performing full sync for project: ${projectId}`);
        } else {
            // Use update_codebase.py for incremental update
            command = `cd "${codebaseAnalyserPath}" &&
                if [ -d "venv" ]; then
                    source venv/bin/activate &&
                    python3 scripts/update_codebase.py "${workspaceFolder}" --mock-embeddings --project-id "${projectId}" &&
                    deactivate;
                else
                    python3 scripts/update_codebase.py "${workspaceFolder}" --mock-embeddings --project-id "${projectId}";
                fi`;

            vscode.window.showInformationMessage(`Performing incremental update for project: ${projectId}`);
        }

        console.log(`Workspace folder: ${workspaceFolder}`);
        console.log(`Project ID: ${projectId}`);
        console.log(`Codebase Analyser path: ${codebaseAnalyserPath}`);
        console.log(`Running command: ${command}`);

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

                    // Now run the actual command
                    console.log('Running the actual command...');
                    const syncProcess = cp.exec(command, (error, stdout, stderr) => {
                        if (error) {
                            const errorMessage = `Error syncing codebase: ${error.message}`;
                            vscode.window.showErrorMessage(errorMessage);
                            statusBar.setError('Sync failed');
                            console.error(`Error: ${error.message}`);
                            console.error(`Command that failed: ${command}`);

                            // Try to get more information about the error
                            if (stderr) {
                                console.error(`Stderr: ${stderr}`);

                                // Create a detailed error log
                                const errorLog = `
Error running codebase analysis:
- Command: ${command}
- Error message: ${error.message}
- Error details: ${stderr}
- Working directory: ${codebaseAnalyserPath}
- Project path: ${workspaceFolder}
- Project ID: ${projectId}
                                `;

                                // Log to console
                                console.error('DETAILED ERROR LOG:');
                                console.error(errorLog);

                                // Show a more detailed error message
                                vscode.window.showErrorMessage(`Error details: ${stderr.substring(0, 100)}...`);

                                // Log the error using the ErrorLogger
                                const logFile = ErrorLogger.logError(error, {
                                    command,
                                    stderr,
                                    stdout,
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
                            }

                            reject(error);
                            return;
                        }

                        if (stderr) {
                            console.error(`Stderr: ${stderr}`);
                        }

                        console.log(`Stdout: ${stdout}`);

                        // Get the last sync time from the database
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
                            console.log('Automatically regenerating visualizations after sync...');
                            vscode.commands.executeCommand('extension-v1.visualizeRelationships');
                        } catch (error) {
                            console.error(`Error getting last sync time: ${error}`);
                            vscode.window.showInformationMessage('Codebase synced successfully!');
                            statusBar.setReady('Codebase synced');
                        }

                        resolve();
                    });

                    token.onCancellationRequested(() => {
                        syncProcess.kill();
                        vscode.window.showInformationMessage('Codebase sync cancelled.');
                        statusBar.setDefault();
                        resolve();
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
                    vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
                }, 100);

                // TODO: Add the file content to the chat
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
            vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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
                vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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

        // Command to run the visualization script
        const command = `cd "${codebaseAnalyserPath}" &&
            if [ -d "venv" ]; then
                source venv/bin/activate &&
                python3 scripts/visualize_code_relationships.py --repo-path "${workspaceFolder}" --output-dir "${centralVisualizationsDir}" --project-id "${projectId}" --timestamp "${timestamp}" &&
                # Also generate in the old location for backward compatibility
                python3 scripts/visualize_code_relationships.py --repo-path "${workspaceFolder}" --output-dir "${visualizationsDir}" --project-id "${projectId}" &&
                deactivate;
            else
                python3 scripts/visualize_code_relationships.py --repo-path "${workspaceFolder}" --output-dir "${centralVisualizationsDir}" --project-id "${projectId}" --timestamp "${timestamp}" &&
                # Also generate in the old location for backward compatibility
                python3 scripts/visualize_code_relationships.py --repo-path "${workspaceFolder}" --output-dir "${visualizationsDir}" --project-id "${projectId}";
            fi`;

        vscode.window.showInformationMessage(`Visualizing code relationships for project: ${projectId}`);
        console.log(`Workspace folder: ${workspaceFolder}`);
        console.log(`Project ID: ${projectId}`);
        console.log(`Visualizations directory: ${visualizationsDir}`);
        console.log(`Running command: ${command}`);

        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Visualizing code relationships',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ message: 'Generating visualizations...' });

            return new Promise<void>((resolve, reject) => {
                // Run the visualization command
                const visualizeProcess = cp.exec(command, (error, stdout, stderr) => {
                    if (error) {
                        const errorMessage = `Error visualizing code relationships: ${error.message}`;
                        vscode.window.showErrorMessage(errorMessage);
                        statusBar.setError('Visualization failed');
                        console.error(`Error: ${error.message}`);
                        console.error(`Command that failed: ${command}`);

                        if (stderr) {
                            console.error(`Stderr: ${stderr}`);
                        }

                        // Log the error to a file
                        const logFile = ErrorLogger.logError(error, {
                            command,
                            stderr,
                            stdout,
                            workspaceFolder,
                            projectId,
                            visualizationsDir
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
                                console.log('Trying manual visualization script as fallback...');
                                const fallbackCommand = `python "${manualVisualizePath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

                                cp.exec(fallbackCommand, (fallbackError, fallbackStdout, fallbackStderr) => {
                                    if (fallbackError) {
                                        console.error(`Fallback visualization failed: ${fallbackError.message}`);
                                        if (fallbackStderr) {
                                            console.error(`Fallback stderr: ${fallbackStderr}`);
                                        }
                                    } else {
                                        console.log('Fallback visualization succeeded');
                                        console.log(`Fallback stdout: ${fallbackStdout}`);

                                        // Check if the visualization files exist
                                        const multiFilePath = path.join(visualizationsDir, `${projectId}_multi_file_relationships.png`);
                                        const relationshipTypesPath = path.join(visualizationsDir, `${projectId}_relationship_types.png`);

                                        if (fs.existsSync(multiFilePath) && fs.existsSync(relationshipTypesPath)) {
                                            vscode.window.showInformationMessage(
                                                'Visualizations created using fallback method.',
                                                'Show in Chat'
                                            ).then(selection => {
                                                if (selection === 'Show in Chat') {
                                                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                                }
                                            });

                                            // Resolve with the fallback visualization paths
                                            resolve();
                                            return;
                                        }
                                    }

                                    // If we get here, both the main and fallback methods failed
                                    reject(error);
                                });
                                return;
                            }
                        } catch (fallbackError) {
                            console.error('Error running fallback visualization:', fallbackError);
                        }

                        reject(error);
                        return;
                    }

                    if (stderr) {
                        console.error(`Stderr: ${stderr}`);
                    }

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

                        // Show visualizations in chat
                        vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');

                        resolve();
                    } catch (parseError) {
                        console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                        console.log("Raw output:", stdout);

                        // Even if parsing fails, try to show visualizations
                        vscode.window.showInformationMessage('Visualizations created successfully!', 'Show in Chat')
                            .then(selection => {
                                if (selection === 'Show in Chat') {
                                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                }
                            });

                        statusBar.setReady('Visualizations created');
                        resolve();
                    }
                });

                token.onCancellationRequested(() => {
                    visualizeProcess.kill();
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
            console.log("DEBUG: showVisualizations function called");
            let visualizationsFound = false;

            // Function to find the latest visualization file
            function findLatestVisualization(directory: string, filePattern: string): string | null {
                if (!fs.existsSync(directory)) {
                    return null;
                }

                try {
                    // Get all files in the directory
                    const files = fs.readdirSync(directory);

                    // Filter files matching the pattern
                    const matchingFiles = files.filter(file => file.includes(filePattern));

                    if (matchingFiles.length === 0) {
                        return null;
                    }

                    // Sort files by timestamp (newest first)
                    matchingFiles.sort((a, b) => {
                        // Extract timestamps if they exist
                        const timestampA = a.match(/(\d{14})/);
                        const timestampB = b.match(/(\d{14})/);

                        if (timestampA && timestampB) {
                            return timestampB[1].localeCompare(timestampA[1]);
                        } else {
                            // If no timestamps, sort by modification time
                            const statA = fs.statSync(path.join(directory, a));
                            const statB = fs.statSync(path.join(directory, b));
                            return statB.mtime.getTime() - statA.mtime.getTime();
                        }
                    });

                    // Return the path to the newest file
                    return path.join(directory, matchingFiles[0]);
                } catch (error) {
                    console.error(`Error finding latest visualization: ${error}`);
                    return null;
                }
            }

            // Try to find the latest visualizations in the central directory first
            let multiFileVisualizationPath = findLatestVisualization(centralVisualizationsDir, 'multi_file_relationships');
            let relationshipTypesVisualizationPath = findLatestVisualization(centralVisualizationsDir, 'relationship_types');

            // Check for UML-style graphs
            const customerJavaHighlightPath = path.join(centralVisualizationsDir, 'customer_java_highlight.png');
            const projectGraphCustomerHighlightPath = path.join(centralVisualizationsDir, 'project_graph_customer_highlight.png');

            const hasCustomerJavaHighlight = fs.existsSync(customerJavaHighlightPath);
            const hasProjectGraphCustomerHighlight = fs.existsSync(projectGraphCustomerHighlightPath);

            // Log what we found
            console.log('VISUALIZATION PATHS:');
            console.log(`Multi-file relationships: ${multiFileVisualizationPath}`);
            console.log(`Relationship types: ${relationshipTypesVisualizationPath}`);
            console.log(`Customer Java Highlight exists: ${hasCustomerJavaHighlight}, path: ${customerJavaHighlightPath}`);
            console.log(`Project Graph Customer Highlight exists: ${hasProjectGraphCustomerHighlight}, path: ${projectGraphCustomerHighlightPath}`);

            // Force specific paths for testing
            multiFileVisualizationPath = path.join(centralVisualizationsDir, 'testshreya_multi_file_relationships_20250512194102.png');
            relationshipTypesVisualizationPath = path.join(centralVisualizationsDir, 'testshreya_relationship_types_20250512194102.png');

            // Verify these files exist
            const forceMultiFileExists = fs.existsSync(multiFileVisualizationPath);
            const forceRelationshipTypesExists = fs.existsSync(relationshipTypesVisualizationPath);
            console.log(`Forced Multi-file relationships exists: ${forceMultiFileExists}, path: ${multiFileVisualizationPath}`);
            console.log(`Forced Relationship types exists: ${forceRelationshipTypesExists}, path: ${relationshipTypesVisualizationPath}`);

            // If not found in central directory, check the old location
            if (!multiFileVisualizationPath) {
                multiFileVisualizationPath = path.join(visualizationsDir, `${projectId}_multi_file_relationships.png`);
                if (!fs.existsSync(multiFileVisualizationPath)) {
                    multiFileVisualizationPath = null;
                }
            }

            if (!relationshipTypesVisualizationPath) {
                relationshipTypesVisualizationPath = path.join(visualizationsDir, `${projectId}_relationship_types.png`);
                if (!fs.existsSync(relationshipTypesVisualizationPath)) {
                    relationshipTypesVisualizationPath = null;
                }
            }

            // Send visualizations to chat
            if (multiFileVisualizationPath) {
                chatViewProvider.sendImageToChat(multiFileVisualizationPath, 'Multi-File Relationships Visualization:');
                visualizationsFound = true;
                console.log(`Using multi-file visualization: ${multiFileVisualizationPath}`);
            }

            if (relationshipTypesVisualizationPath) {
                chatViewProvider.sendImageToChat(relationshipTypesVisualizationPath, 'Relationship Types Visualization:');
                visualizationsFound = true;
                console.log(`Using relationship types visualization: ${relationshipTypesVisualizationPath}`);
            }

            // Send UML-style graphs to chat
            if (hasCustomerJavaHighlight) {
                chatViewProvider.sendImageToChat(customerJavaHighlightPath, 'Customer Java Highlight:');
                visualizationsFound = true;
                console.log(`Using Customer Java Highlight: ${customerJavaHighlightPath}`);
            }

            if (hasProjectGraphCustomerHighlight) {
                chatViewProvider.sendImageToChat(projectGraphCustomerHighlightPath, 'Project Graph with Customer Highlight:');
                visualizationsFound = true;
                console.log(`Using Project Graph with Customer Highlight: ${projectGraphCustomerHighlightPath}`);
            }

            if (!visualizationsFound) {
                vscode.window.showErrorMessage('No visualization files found. Please run "Visualize Code Relationships" first.');
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

        // Path to the visualizations directory
        const visualizationsDir = path.join(workspaceFolder, 'visualizations');

        // Create the directory if it doesn't exist
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
                const command = `python "${manualVisualizePath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

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
                            vscode.window.showInformationMessage(
                                'Visualizations generated successfully!',
                                'Show in Chat', 'Open Multi-File', 'Open Relationship Types'
                            ).then(selection => {
                                if (selection === 'Show in Chat') {
                                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                } else if (selection === 'Open Multi-File' && result.multi_file_relationships) {
                                    vscode.env.openExternal(vscode.Uri.file(result.multi_file_relationships));
                                } else if (selection === 'Open Relationship Types' && result.relationship_types) {
                                    vscode.env.openExternal(vscode.Uri.file(result.relationship_types));
                                }
                            });

                            resolve();
                        } catch (parseError) {
                            console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                            console.log("Raw output:", stdout);

                            // Even if parsing fails, try to show visualizations
                            vscode.window.showInformationMessage(
                                'Visualizations created successfully!',
                                'Show in Chat'
                            ).then(selection => {
                                if (selection === 'Show in Chat') {
                                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                }
                            });
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

    // Add commands to subscriptions
    context.subscriptions.push(startAssistantCommand);
    context.subscriptions.push(analyzeRequirementsCommand);
    context.subscriptions.push(generateCodeCommand);
    context.subscriptions.push(openChatViewCommand);
    context.subscriptions.push(syncCodebaseCommand);
    context.subscriptions.push(attachFileCommand);
    context.subscriptions.push(sendErrorToChatCommand);
    context.subscriptions.push(visualizeRelationshipsCommand);
    context.subscriptions.push(showVisualizationsInChatCommand);
    context.subscriptions.push(generateVisualizationsCommand);
    context.subscriptions.push(showDirectImageCommand);

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
export function deactivate() {}
