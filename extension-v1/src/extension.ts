// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as cp from 'child_process';
import { StatusBarItem } from './ui/statusBar';
import { ChatViewProvider } from './ui/chatView';

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
        vscode.commands.executeCommand('extension-v1.chatView.focus');
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
        vscode.commands.executeCommand('extension-v1.chatView.focus');
    });

    // Sync codebase command
    let syncCodebaseCommand = vscode.commands.registerCommand('extension-v1.syncCodebase', async () => {
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

        // Use a hardcoded path to the codebase-analyser directory
        const codebaseAnalyserPath = '/Users/shreyah/Documents/Projects/SAP/RepoMind/codebase-analyser';

        // Use analyze_java.py with the --visualize flag to generate a dependency graph
        // Activate the virtual environment if it exists, and deactivate it after running the script
        const command = `cd "${codebaseAnalyserPath}" &&
            if [ -d "venv" ]; then
                source venv/bin/activate &&
                python3 scripts/analyze_java.py "${workspaceFolder}" --clear-db --mock-embeddings --project-id "${projectId}" --visualize &&
                deactivate;
            else
                python3 scripts/analyze_java.py "${workspaceFolder}" --clear-db --mock-embeddings --project-id "${projectId}" --visualize;
            fi`;

        vscode.window.showInformationMessage(`Analyzing project: ${projectId}`);
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

                                // Create an error log file
                                const errorLogPath = path.join(codebaseAnalyserPath, 'error_log.txt');
                                try {
                                    fs.writeFileSync(errorLogPath, errorLog);
                                    vscode.window.showInformationMessage(`Error log saved to: ${errorLogPath}`);
                                } catch (logError) {
                                    console.error(`Failed to write error log: ${logError instanceof Error ? logError.message : String(logError)}`);
                                }

                                // Send error to chat view
                                vscode.commands.executeCommand('extension-v1.sendErrorToChat', errorLog, errorLogPath);
                            }

                            reject(error);
                            return;
                        }

                        if (stderr) {
                            console.error(`Stderr: ${stderr}`);
                        }

                        console.log(`Stdout: ${stdout}`);
                        vscode.window.showInformationMessage('Codebase synced successfully!');
                        statusBar.setReady('Codebase synced');
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

                // Focus the chat view
                vscode.commands.executeCommand('extension-v1.chatView.focus');

                // TODO: Add the file content to the chat
                console.log(`Attached file: ${fileName}`);
                console.log(`Content: ${fileContent.substring(0, 100)}...`);
            } catch (error) {
                vscode.window.showErrorMessage(`Error reading file: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    });

    // Command to send error to chat view
    let sendErrorToChatCommand = vscode.commands.registerCommand('extension-v1.sendErrorToChat', (_errorLog: string, errorLogPath: string) => {
        // Focus the chat view
        vscode.commands.executeCommand('extension-v1.chatView.focus');

        // Post a message to the chat view
        setTimeout(() => {
            // Create a simple notification with the error
            vscode.window.showErrorMessage('Error syncing codebase. Details have been saved to error_log.txt.');

            // Add error to the chat view
            // We'll use a simpler approach by showing a notification
            // and focusing the chat view
            vscode.window.showInformationMessage(`Error details saved to: ${errorLogPath}`);

            // Focus the chat view
            vscode.commands.executeCommand('extension-v1.chatView.focus');
        }, 1000);
    });

    // Add commands to subscriptions
    context.subscriptions.push(startAssistantCommand);
    context.subscriptions.push(analyzeRequirementsCommand);
    context.subscriptions.push(generateCodeCommand);
    context.subscriptions.push(openChatViewCommand);
    context.subscriptions.push(syncCodebaseCommand);
    context.subscriptions.push(attachFileCommand);
    context.subscriptions.push(sendErrorToChatCommand);

    // Set status
    statusBar.setReady('RepoMind is ready');
}

// This method is called when your extension is deactivated
export function deactivate() {}
