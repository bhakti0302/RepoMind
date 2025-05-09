import * as vscode from 'vscode';

/**
 * Status bar item for the extension
 */
export class StatusBarItem implements vscode.Disposable {
    private static instance: StatusBarItem;
    private statusBarItem: vscode.StatusBarItem;
    
    /**
     * Private constructor to enforce singleton pattern
     */
    private constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'extension-v1.openChatView';
        this.setDefault();
        this.statusBarItem.show();
    }
    
    /**
     * Get the singleton instance
     * @returns The StatusBarItem instance
     */
    public static getInstance(): StatusBarItem {
        if (!StatusBarItem.instance) {
            StatusBarItem.instance = new StatusBarItem();
        }
        return StatusBarItem.instance;
    }
    
    /**
     * Set the status bar to default state
     */
    public setDefault(): void {
        this.statusBarItem.text = '$(robot) RepoMind';
        this.statusBarItem.tooltip = 'RepoMind';
        this.statusBarItem.backgroundColor = undefined;
    }
    
    /**
     * Set the status bar to ready state
     * @param message Optional message to display
     */
    public setReady(message?: string): void {
        this.statusBarItem.text = '$(check) RepoMind';
        this.statusBarItem.tooltip = message || 'RepoMind is ready';
        this.statusBarItem.backgroundColor = undefined;
    }
    
    /**
     * Set the status bar to working state
     * @param message Optional message to display
     */
    public setWorking(message?: string): void {
        this.statusBarItem.text = '$(sync~spin) RepoMind';
        this.statusBarItem.tooltip = message || 'RepoMind is working...';
        this.statusBarItem.backgroundColor = undefined;
    }
    
    /**
     * Set the status bar to error state
     * @param message Optional error message to display
     */
    public setError(message?: string): void {
        this.statusBarItem.text = '$(error) RepoMind';
        this.statusBarItem.tooltip = message || 'RepoMind encountered an error';
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
    
    /**
     * Dispose the status bar item
     */
    public dispose(): void {
        this.statusBarItem.dispose();
    }
}
