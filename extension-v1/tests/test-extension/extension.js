const vscode = require('vscode');

function activate(context) {
    console.log('Test extension activated!');
    
    // Show a notification
    vscode.window.showInformationMessage('Test extension activated!');
    
    // Register a command
    let disposable = vscode.commands.registerCommand('test-extension.helloWorld', function () {
        vscode.window.showInformationMessage('Hello World from test extension!');
    });
    
    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
