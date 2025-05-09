// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
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

    // Add commands to subscriptions
    context.subscriptions.push(startAssistantCommand);
    context.subscriptions.push(analyzeRequirementsCommand);
    context.subscriptions.push(generateCodeCommand);
    context.subscriptions.push(openChatViewCommand);
    
    // Set status
    statusBar.setReady('RepoMind is ready');
}

// This method is called when your extension is deactivated
export function deactivate() {}
