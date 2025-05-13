// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as cp from 'child_process';
import { StatusBarItem } from './ui/statusBar';
import { ChatViewProvider } from './ui/chatView';
import { ErrorLogger } from './utils/errorLogger';

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

    let generateCodeCommand = vscode.commands.registerCommand('extension-v1.generateCode', (filePath?: string) => {
        statusBar.setWorking('Generating code...');
        vscode.window.showInformationMessage('Generating code from requirements...');

        // If no file path is provided, ask the user to select a file
        if (!filePath) {
            vscode.commands.executeCommand('extension-v1.attachFile');
            return;
        }

        // Get the project ID
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            statusBar.setError('No workspace folder');
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Try to find the codebase-analyser path
        let codebaseAnalyserPath = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser';
        console.log(`Using hardcoded codebase-analyser path: ${codebaseAnalyserPath}`);

        // Define the Requirements directory path - use absolute path
        const requirementsDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/Requirements';
        console.log(`Using Requirements directory path: ${requirementsDir}`);

        // Create the Requirements directory if it doesn't exist
        if (!fs.existsSync(requirementsDir)) {
            fs.mkdirSync(requirementsDir, { recursive: true });
            console.log(`Created Requirements directory: ${requirementsDir}`);
        }

        // Check if the path exists
        if (!fs.existsSync(codebaseAnalyserPath)) {
            const errorMessage = `Hardcoded codebase-analyser path not found: ${codebaseAnalyserPath}`;
            vscode.window.showErrorMessage(errorMessage);
            if (chatViewProvider) {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: errorMessage,
                    isUser: false
                });
            }
            statusBar.setError('Codebase analyser not found');
            return;
        }
        // First, check if it's directly in the workspace folder
        //const directPath = path.join(workspaceFolder, 'codebase-analyser');
        // if (fs.existsSync(directPath)) {
        //     codebaseAnalyserPath = directPath;
        // }
        // // Next, check if we're already in the codebase-analyser directory
        // else if (path.basename(workspaceFolder) === 'codebase-analyser') {
        //     codebaseAnalyserPath = workspaceFolder;
        // }
        // // Finally, check if we're in a subdirectory of codebase-analyser
        // else {
        //     const parentDir = path.dirname(workspaceFolder);
        //     const parentBasename = path.basename(parentDir);
        //     if (parentBasename === 'codebase-analyser') {
        //         codebaseAnalyserPath = parentDir;
        //     }
        // }
        // // If we still can't find it, show an error
        // if (!codebaseAnalyserPath || !fs.existsSync(codebaseAnalyserPath)) {
        //     // Show a more helpful error message
        //     const errorMessage = 'Codebase analyser directory not found. Please open a workspace that contains the codebase-analyser directory or is the codebase-analyser directory itself.';
        //     vscode.window.showErrorMessage(errorMessage);

            // if (chatViewProvider) {
            //     chatViewProvider.sendMessageToWebviews({
            //         command: 'addMessage',
            //         text: errorMessage,
            //         isUser: false
            //     });
            // }
            // statusBar.setError('Codebase analyser not found');
            // return;
        //}

        console.log(`Found codebase-analyser at: ${codebaseAnalyserPath}`);

        // Create output directory if it doesn't exist
        const outputDir = path.join(codebaseAnalyserPath, 'output');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Check if the nlp-analysis directory exists
        const nlpAnalysisPath = path.join(codebaseAnalyserPath, 'nlp-analysis');
        if (!fs.existsSync(nlpAnalysisPath)) {
            const errorMessage = `NLP analysis directory not found at ${nlpAnalysisPath}`;
            vscode.window.showErrorMessage(errorMessage);

            if (chatViewProvider) {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: errorMessage,
                    isUser: false
                });
            }

            statusBar.setError('NLP analysis not found');
            return;
        }

        // Check if the vscode_integration.py file exists
        const vscodeIntegrationPath = path.join(nlpAnalysisPath, 'src', 'vscode_integration.py');
        if (!fs.existsSync(vscodeIntegrationPath)) {
            const errorMessage = `VS Code integration script not found at ${vscodeIntegrationPath}`;
            vscode.window.showErrorMessage(errorMessage);

            if (chatViewProvider) {
                chatViewProvider.sendMessageToWebviews({
                    command: 'addMessage',
                    text: errorMessage,
                    isUser: false
                });
            }

            statusBar.setError('Integration script not found');
            return;
        }

        // Use the project-wide virtual environment
        const projectRoot = path.dirname(codebaseAnalyserPath); // Get the parent directory
        const venvPath = path.join(projectRoot, 'venv');
        const venvActivate = path.join(venvPath, 'bin', 'activate');
        const command = `cd "${codebaseAnalyserPath}" &&
        if [ -d "venv" ]; then
            source venv/bin/activate &&
            python3 nlp-analysis/src/vscode_integration.py --output-dir "${outputDir}" --requirements-dir "${requirementsDir}" process --file "${filePath}" --project-id "${projectId}" &&
            deactivate;
        else
            python3 nlp-analysis/src/vscode_integration.py --output-dir "${outputDir}" --requirements-dir "${requirementsDir}" process --file "${filePath}" --project-id "${projectId}";
        fi`;
        // const command = `cd "${codebaseAnalyserPath}" &&
        //     if [ -d "venv" ]; then
        //         source venv/bin/activate &&
        //         python3 nlp-analysis/src/vscode_integration.py process --file "${filePath}" --project-id "${projectId}" --output-dir "${outputDir}" &&
        //         deactivate;
        //     else
        //         python3 nlp-analysis/src/vscode_integration.py process --file "${filePath}" --project-id "${projectId}" --output-dir "${outputDir}";
        //     fi`;

        // const command = `cd "${projectRoot}" &&
        //     if [ -d "${venvPath}" ]; then
        //         source "${venvActivate}" &&
        //         PYTHONPATH="${projectRoot}" python3 codebase-analyser/nlp-analysis/src/vscode_integration.py process --file "${filePath}" --output-dir "${outputDir}" --project-id "${projectId}" &&
        //         deactivate;
        //     else
        //         PYTHONPATH="${projectRoot}" python3 codebase-analyser/nlp-analysis/src/vscode_integration.py process --file "${filePath}" --output-dir "${outputDir}" --project-id "${projectId}";
        //     fi`;
        // Build the command to run the code synthesis workflow
        // const command = `cd "${codebaseAnalyserPath}" &&
        //     if [ -d "venv" ]; then
        //         source venv/bin/activate &&
        //         python3 nlp-analysis/src/vscode_integration.py process --file "${filePath}" --output-dir "${outputDir}" --project-id "${projectId}" &&
        //         deactivate;
        //     else
        //         python3 nlp-analysis/src/vscode_integration.py process --file "${filePath}" --output-dir "${outputDir}" --project-id "${projectId}";
        //     fi`;

        // Log detailed information for debugging
        console.log('=== Code Generation Debug Info ===');
        console.log(`Workspace folder: ${workspaceFolder}`);
        console.log(`Project ID: ${projectId}`);
        console.log(`Codebase analyser path: ${codebaseAnalyserPath}`);
        console.log(`NLP analysis path: ${nlpAnalysisPath}`);
        console.log(`VS Code integration path: ${vscodeIntegrationPath}`);
        console.log(`Output directory: ${outputDir}`);
        console.log(`Input file: ${filePath}`);
        console.log(`Running command: ${command}`);

        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating code',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ message: 'Processing requirements...' });

            return new Promise<void>((resolve) => {
                const generateProcess = cp.exec(command, (error, stdout, stderr) => {
                    if (error) {
                        const errorMessage = `Error generating code: ${error.message}`;
                        vscode.window.showErrorMessage(errorMessage);
                        statusBar.setError('Code generation failed');

                        console.error('=== Code Generation Error ===');
                        console.error(`Error message: ${error.message}`);
                        console.error(`Error code: ${error.code}`);
                        console.error(`Command that failed: ${command}`);

                        if (stderr) {
                            console.error('=== Standard Error Output ===');
                            console.error(stderr);
                        }

                        // Provide more detailed error information in the chat
                        if (chatViewProvider) {
                            chatViewProvider.sendMessageToWebviews({
                                command: 'addMessage',
                                text: `Error generating code: ${error.message}`,
                                isUser: false
                            });

                            if (stderr) {
                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Error details:\n\`\`\`\n${stderr}\n\`\`\``,
                                    isUser: false
                                });
                            }

                            // Provide troubleshooting tips
                            chatViewProvider.sendMessageToWebviews({
                                command: 'addMessage',
                                text: `Troubleshooting tips:
1. Make sure Python 3 is installed and in your PATH
2. Check that the codebase-analyser directory structure is correct
3. Verify that all required Python packages are installed
4. Ensure your .env file is properly configured with the LLM API key`,
                                isUser: false
                            });
                        }

                        resolve();
                        return;
                    }

                    try {
                        // Parse the output
                        const outputJson = JSON.parse(stdout);
                        console.log('Code generation output:', outputJson);

                        // Check for errors
                        if (outputJson.status === 'error') {
                            vscode.window.showErrorMessage(`Error generating code: ${outputJson.message}`);
                            statusBar.setError('Code generation failed');

                            if (chatViewProvider) {
                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Error generating code: ${outputJson.message}`,
                                    isUser: false
                                });
                            }

                            resolve();
                            return;
                        }

                        // Check for output files
                        // const instructionsFile = path.join(outputDir, 'llm-instructions.txt');
                        const outputFile = path.join(outputDir, 'llm-output.txt');

                        let successMessage = 'Code generation completed!';

                        if (fs.existsSync(outputFile)) {
                            // Read the generated code
                            const generatedCode = fs.readFileSync(outputFile, 'utf8');
                            successMessage += ` Output saved to ${outputFile}`;

                            // Send the generated code to the chat view
                            if (chatViewProvider) {
                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Code generation completed! Here's the generated code:`,
                                    isUser: false
                                });

                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `\`\`\`\n${generatedCode.substring(0, 1000)}${generatedCode.length > 1000 ? '...' : ''}\n\`\`\``,
                                    isUser: false
                                });

                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Full output saved to: ${outputFile}`,
                                    isUser: false
                                });
                            }
                        } else {
                            if (chatViewProvider) {
                                chatViewProvider.sendMessageToWebviews({
                                    command: 'addMessage',
                                    text: `Code generation completed, but no output file was found.`,
                                    isUser: false
                                });
                            }
                        }

                        vscode.window.showInformationMessage(successMessage);
                        statusBar.setReady('Code generated');
                        resolve();
                    } catch (parseError) {
                        console.error(`Error parsing code generation result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                        console.error(`Raw output: ${stdout}`);
                        vscode.window.showErrorMessage('Code generation completed, but could not parse the result.');
                        statusBar.setReady('Code generated');

                        // if (chatViewProvider) {
                        //     chatViewProvider.sendMessageToWebviews({
                        //         command: 'addMessage',
                        //         text: `Code generation completed, but there was an error parsing the result.`,
                        //         isUser: false
                        //     });
                        // }

                        resolve();
                    }
                });

                token.onCancellationRequested(() => {
                    generateProcess.kill();
                    vscode.window.showInformationMessage('Code generation cancelled.');
                    statusBar.setDefault();

                    if (chatViewProvider) {
                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `Code generation cancelled.`,
                            isUser: false
                        });
                    }

                    resolve();
                });
            });
        }).then(() => {
            console.log('Code generation process completed successfully');
        }, (error: unknown) => {
            console.error(`Code generation process failed: ${error instanceof Error ? error.message : String(error)}`);
        });
    });

    let openChatViewCommand = vscode.commands.registerCommand('extension-v1.openChatView', () => {
        // Focus our chat view without affecting other extensions
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.extension-v1.chatView');

            //vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
        }, 100);
    });

    // Sync codebase command
    let syncCodebaseCommand = vscode.commands.registerCommand('extension-v1.syncCodebase', async () => {
        // Make sure we stay in our extension view
        setTimeout(() => {
            vscode.commands.executeCommand('workbench.view.extension-v1.chatView');

            //vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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

                // Get the Requirements directory path
                const requirementsDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/Requirements';
                const requirementsPath = path.join(requirementsDir, fileName);

                // Create the Requirements directory if it doesn't exist
                if (!fs.existsSync(requirementsDir)) {
                    fs.mkdirSync(requirementsDir, { recursive: true });
                    console.log(`Created Requirements directory: ${requirementsDir}`);
                }

                // Copy the file directly to the Requirements folder
                try {
                    fs.copyFileSync(filePath, requirementsPath);
                    console.log(`Copied file to Requirements folder: ${requirementsPath}`);

                    // Trigger the pipeline script with the uploaded file
                    const pipelineScriptPath = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis/run_fixed_pipeline.sh';

                    // Check if the pipeline script exists
                    if (!fs.existsSync(pipelineScriptPath)) {
                        console.error(`Pipeline script not found: ${pipelineScriptPath}`);
                        vscode.window.showErrorMessage(`Pipeline script not found: ${pipelineScriptPath}`);
                        return;
                    }

                    // Run the pipeline script with the uploaded file
                    console.log(`Running pipeline script with file: ${requirementsPath}`);

                    // Add a processing message to the chat view
                    let processingMessageId: string | null = null;
                    if (chatViewProvider) {
                        // Generate a unique message ID
                        processingMessageId = `processing-${Date.now()}`;

                        // Send initial processing message with the ID
                        chatViewProvider.sendMessageToWebviews({
                            command: 'addMessage',
                            text: `Processing file: ${fileName}...`,
                            isUser: false,
                            id: processingMessageId
                        });
                    }

                    // Show a progress indicator while the pipeline is running
                    vscode.window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: `Running pipeline with file: ${fileName}`,
                        cancellable: false
                    }, async (progress) => {
                        progress.report({ increment: 0, message: "Starting pipeline..." });

                        // Execute the pipeline script
                        return new Promise<void>((resolve, reject) => {
                            const exec = require('child_process').exec;

                            // Set up animated dots in chat
                            const updateInterval = setInterval(() => {
                                if (chatViewProvider && processingMessageId) {
                                    // Create a message with animated dots using HTML
                                    const processingMessage = `Processing file: ${fileName} <div class="loading-dots" style="display: inline-block;"><span></span><span></span><span></span></div> (still running)`;

                                    chatViewProvider.sendMessageToWebviews({
                                        command: 'updateMessage',
                                        id: processingMessageId,
                                        text: processingMessage
                                    });
                                }
                            }, 2000); // Update less frequently since animation is handled by CSS

                            const child = exec(`bash "${pipelineScriptPath}" "${requirementsPath}"`, (error: any, stdout: any, stderr: any) => {
                                // Clear the update interval when the process completes
                                clearInterval(updateInterval);
                                // Log the output and error regardless of success or failure
                                console.log(`Pipeline script output: ${stdout}`);
                                if (stderr) {
                                    console.error(`Pipeline script error: ${stderr}`);
                                }

                                if (error) {
                                    console.error(`Error running pipeline script: ${error}`);

                                    // Update the processing message with the error
                                    if (chatViewProvider && processingMessageId) {
                                        chatViewProvider.sendMessageToWebviews({
                                            command: 'updateMessage',
                                            id: processingMessageId,
                                            text: `Processing failed: ${fileName} <span style="color: #ef4444; font-weight: bold;">✗</span>`
                                        });

                                        // Add a detailed error message
                                        chatViewProvider.sendMessageToWebviews({
                                            command: 'addMessage',
                                            text: `Error running pipeline script: ${error}\n\nCheck the logs for more details.`,
                                            isUser: false
                                        });
                                    }

                                    vscode.window.showErrorMessage(`Error running pipeline script: ${error}`);
                                    reject(error);
                                    return;
                                }

                                // Show a notification that the pipeline has completed
                                vscode.window.showInformationMessage(`Pipeline completed successfully! Check the output files in the output directory.`);

                                // Update the processing message with completion status
                                if (chatViewProvider && processingMessageId) {
                                    chatViewProvider.sendMessageToWebviews({
                                        command: 'updateMessage',
                                        id: processingMessageId,
                                        text: `Processing completed: ${fileName} <span style="color: #22c55e; font-weight: bold;">✓</span>`
                                    });

                                    // Define output file paths
                                    const outputDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output';
                                    const llmInstructionsFile = path.join(outputDir, 'LLM-instructions.txt');

                                    // Create a concise message with just the file paths
                                    let outputMessage = `✅ Requirements have been analyzed successfully!\n\n`;

                                    // Check if the LLM instructions file exists
                                    if (fs.existsSync(llmInstructionsFile)) {
                                        outputMessage += `The code changes have been generated and saved to:\n`;
                                        outputMessage += `📄 ${llmInstructionsFile}\n\n`;

                                        // Add a button to open the file
                                        outputMessage += `<div style="margin-top: 10px; margin-bottom: 10px;">
                                            <button id="open-llm-file" style="background-color: #0078d4; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;"
                                                    data-path="${llmInstructionsFile.replace(/\\/g, '\\\\')}">
                                                Open LLM Instructions File
                                            </button>
                                        </div>`;

                                        // Add a fallback link in case the button doesn't work
                                        outputMessage += `Click the button above to view the detailed implementation instructions. `;
                                        outputMessage += `If the button doesn't work, you can find the file at: ${llmInstructionsFile}`;
                                    } else {
                                        outputMessage += `⚠️ LLM instructions file was not generated. Please check the logs for errors.`;
                                    }

                                    // Send the message to the chat view
                                    chatViewProvider.sendMessageToWebviews({
                                        command: 'addMessage',
                                        text: outputMessage,
                                        isUser: false
                                    });

                                    // Also add a direct message to open the file
                                    if (fs.existsSync(llmInstructionsFile)) {
                                        setTimeout(() => {
                                            chatViewProvider.sendMessageToWebviews({
                                                command: 'addMessage',
                                                text: `You can also click this link to open the file: <a href="#" style="color: #0078d4; text-decoration: underline; cursor: pointer;" data-path="${llmInstructionsFile.replace(/\\/g, '\\\\')}">Open LLM Instructions File</a>`,
                                                isUser: false
                                            });
                                        }, 500);
                                    }
                                }

                                resolve();
                            });

                            // Update progress periodically
                            let progressCounter = 0;
                            const progressInterval = setInterval(() => {
                                progressCounter += 5;
                                if (progressCounter > 95) {
                                    progressCounter = 95; // Cap at 95% until complete
                                }
                                progress.report({ increment: 5, message: `Processing... (${progressCounter}%)` });
                            }, 5000); // Update every 5 seconds

                            // Clean up interval when process completes
                            child.on('exit', () => {
                                clearInterval(progressInterval);
                                progress.report({ increment: 100 - progressCounter, message: "Completed!" });
                            });
                        });
                    });
                } catch (error) {
                    console.error(`Error copying file to Requirements folder: ${error}`);
                    vscode.window.showErrorMessage(`Error copying file to Requirements folder: ${error}`);
                }

                vscode.window.showInformationMessage(`File attached: ${fileName}`);

                // Focus our chat view without affecting other extensions
                setTimeout(() => {
                    vscode.commands.executeCommand('workbench.view.extension-v1.chatView');

                    //vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
                }, 100);

                // Send the file content to the chat view
                if (chatViewProvider) {
                    // Use the Requirements directory path we already defined
                    const requirementsPath = path.join(requirementsDir, fileName);

                    chatViewProvider.sendMessageToWebviews({
                        command: 'addMessage',
                        text: `Attached file: ${fileName}\nStored in Requirements folder: ${requirementsPath}`,
                        isUser: false
                    });

                    // Trigger code generation process
                    vscode.commands.executeCommand('extension-v1.generateCode', filePath);
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
            vscode.commands.executeCommand('workbench.view.extension.extension-v1.chatView');

            //vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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
                vscode.commands.executeCommand('workbench.view.extension.extension-v1.chatView');

                //vscode.commands.executeCommand('workbench.view.extension.repomind-chat-view');
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
                python3 scripts/fixed_visualize.py --project-id "${projectId}" --output-dir "${centralVisualizationsDir}" --timestamp "${timestamp}" &&
                # Also generate in the old location for backward compatibility
                python3 scripts/fixed_visualize.py --project-id "${projectId}" --output-dir "${visualizationsDir}" &&
                deactivate;
            else
                python3 scripts/fixed_visualize.py --project-id "${projectId}" --output-dir "${centralVisualizationsDir}" --timestamp "${timestamp}" &&
                # Also generate in the old location for backward compatibility
                python3 scripts/fixed_visualize.py --project-id "${projectId}" --output-dir "${visualizationsDir}";
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
                            const visualizeFromDbPath = path.join(codebaseAnalyserPath, 'scripts', 'fixed_visualize.py');
                            if (fs.existsSync(visualizeFromDbPath)) {
                                console.log('Trying fixed_visualize.py script as fallback...');
                                const fallbackCommand = `python "${visualizeFromDbPath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

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
                        // Parse the JSON output to get the visualization paths
                        const result = JSON.parse(stdout);

                        // Show success message with links to open the visualizations
                        vscode.window.showInformationMessage('Code relationships visualized successfully!',
                            'Open Multi-File Relationships', 'Open Relationship Types')
                            .then(selection => {
                                if (selection === 'Open Multi-File Relationships') {
                                    // Open the multi-file relationships visualization
                                    const multiFileVisualizationPath = result.multi_file_relationships;
                                    vscode.env.openExternal(vscode.Uri.file(multiFileVisualizationPath));
                                } else if (selection === 'Open Relationship Types') {
                                    // Open the relationship types visualization
                                    const relationshipTypesVisualizationPath = result.relationship_types;
                                    vscode.env.openExternal(vscode.Uri.file(relationshipTypesVisualizationPath));
                                }
                            });

                        statusBar.setReady('Visualizations created');
                        resolve();
                    } catch (parseError) {
                        console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                        vscode.window.showErrorMessage('Visualizations created, but could not parse the result.');
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

    // Command to open a file
    let openFileCommand = vscode.commands.registerCommand('extension-v1.openFile', (filePath: string) => {
        if (filePath) {
            try {
                const uri = vscode.Uri.file(filePath);
                vscode.commands.executeCommand('vscode.open', uri);
            } catch (error) {
                console.error(`Error opening file: ${error}`);
                vscode.window.showErrorMessage(`Error opening file: ${error}`);
            }
        }
    });

    // Command to process code questions
    let processCodeQuestionCommand = vscode.commands.registerCommand('extension-v1.processCodeQuestion', async (question: string) => {
        try {
            // Import the processCodeQuestion function
            const { processCodeQuestion } = require('./utils/chatAssistant');

            // Process the code question
            const response = await processCodeQuestion(question);

            // Return the response
            return response;
        } catch (error) {
            console.error(`Error processing code question: ${error}`);
            vscode.window.showErrorMessage(`Error processing code question: ${error instanceof Error ? error.message : String(error)}`);
            return `Error processing your question: ${error instanceof Error ? error.message : String(error)}`;
        }
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
                const visualizeFromDbPath = path.join(codebaseAnalyserPath, 'scripts', 'fixed_visualize.py');
                if (fs.existsSync(visualizeFromDbPath)) {
                    vscode.window.showInformationMessage('Generating visualizations...');

                    const fallbackCommand = `python "${visualizeFromDbPath}" --output-dir "${visualizationsDir}" --project-id "${projectId}"`;

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
                        // Extract JSON from the output using markers
                        let jsonOutput = stdout;
                        const beginMarker = "JSON_OUTPUT_BEGINS";
                        const endMarker = "JSON_OUTPUT_ENDS";

                        const beginIndex = stdout.indexOf(beginMarker);
                        const endIndex = stdout.indexOf(endMarker);

                        if (beginIndex !== -1 && endIndex !== -1) {
                            // Extract the JSON part between the markers
                            jsonOutput = stdout.substring(beginIndex + beginMarker.length, endIndex).trim();
                        } else {
                            // If markers not found, try to parse the whole output as JSON
                            console.log("JSON markers not found, trying to parse the entire output");
                        }

                        // Parse the JSON output to get the visualization paths
                        const result = JSON.parse(jsonOutput);

                        // Show success message with links to open the visualizations
                        vscode.window.showInformationMessage('Code relationships visualized successfully!',
                            'Open Multi-File Relationships', 'Open Relationship Types')
                            .then(selection => {
                                if (selection === 'Open Multi-File Relationships') {
                                    // Open the multi-file relationships visualization
                                    const multiFileVisualizationPath = result.multi_file_relationships;
                                    vscode.env.openExternal(vscode.Uri.file(multiFileVisualizationPath));
                                } else if (selection === 'Open Relationship Types') {
                                    // Open the relationship types visualization
                                    const relationshipTypesVisualizationPath = result.relationship_types;
                                    vscode.env.openExternal(vscode.Uri.file(relationshipTypesVisualizationPath));
                                }
                            });

                        statusBar.setReady('Visualizations created');
                        resolve();
                    } catch (parseError) {
                        console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                        console.error(`Raw output: ${stdout}`);

                        // Check if visualizations were created despite the parsing error
                        const visualizationDir = path.join(workspaceFolder, '.repomind', 'visualizations');
                        const multiFilePath = path.join(visualizationDir, `${projectId}_multi_file_relationships.png`);
                        const relationshipTypesPath = path.join(visualizationDir, `${projectId}_relationship_types.png`);

                        if (fs.existsSync(multiFilePath) || fs.existsSync(relationshipTypesPath)) {
                            vscode.window.showInformationMessage('Visualizations created, but could not parse the result.',
                                'Show in Chat')
                                .then(selection => {
                                    if (selection === 'Show in Chat') {
                                        vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                                    }
                                });
                        } else {
                            vscode.window.showErrorMessage('Failed to create visualizations.');
                        }

                        statusBar.setReady('Visualizations created');
                        resolve();
                    }
                        // try {
                        //     // Parse the JSON output to get the visualization paths
                        //     const result = JSON.parse(stdout);

                        //     // Show success message with links to open the visualizations
                        //     vscode.window.showInformationMessage(
                        //         'Visualizations generated successfully!',
                        //         'Show in Chat', 'Open Multi-File', 'Open Relationship Types'
                        //     ).then(selection => {
                        //         if (selection === 'Show in Chat') {
                        //             vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                        //         } else if (selection === 'Open Multi-File') {
                        //             vscode.env.openExternal(vscode.Uri.file(result.multi_file_relationships));
                        //         } else if (selection === 'Open Relationship Types') {
                        //             vscode.env.openExternal(vscode.Uri.file(result.relationship_types));
                        //         }
                        //     });

                        //     resolve();
                        // } catch (parseError) {
                        //     console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
                        //     vscode.window.showInformationMessage(
                        //         'Visualizations created, but could not parse the result.',
                        //         'Show in Chat'
                        //     ).then(selection => {
                        //         if (selection === 'Show in Chat') {
                        //             vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                        //         }
                        //     });
                        //     resolve();
                        // }
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
    context.subscriptions.push(openFileCommand);
    context.subscriptions.push(processCodeQuestionCommand);

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
