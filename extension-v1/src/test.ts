import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Test extension activated!');
    
    // Create a simple status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(robot) RepoMind Test";
    statusBarItem.tooltip = "RepoMind Test Extension";
    statusBarItem.show();
    
    // Register a simple command
    let testCommand = vscode.commands.registerCommand('extension-v1.test', () => {
        vscode.window.showInformationMessage('RepoMind Test Command Executed!');
    });
    
    context.subscriptions.push(statusBarItem);
    context.subscriptions.push(testCommand);
}

export function deactivate() {}