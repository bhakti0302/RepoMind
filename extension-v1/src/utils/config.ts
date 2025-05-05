import * as vscode from 'vscode';

/**
 * Configuration utility functions for the extension
 */
export class ConfigUtil {
    /**
     * Get the configured LLM provider
     * @returns The configured LLM provider name
     */
    static getLlmProvider(): string {
        const config = vscode.workspace.getConfiguration('extension-v1');
        return config.get<string>('llmProvider') || 'openrouter';
    }
    
    /**
     * Get the configured model name
     * @returns The configured model name
     */
    static getModelName(): string {
        const config = vscode.workspace.getConfiguration('extension-v1');
        return config.get<string>('modelName') || 'llama';
    }
    
    /**
     * Get the configured API key
     * @returns The configured API key
     */
    static getApiKey(): string {
        const config = vscode.workspace.getConfiguration('extension-v1');
        return config.get<string>('apiKey') || '';
    }
    
    /**
     * Check if the extension is configured with an API key
     * @returns True if the API key is configured, false otherwise
     */
    static isConfigured(): boolean {
        return !!ConfigUtil.getApiKey();
    }
    
    /**
     * Update a configuration setting
     * @param key The configuration key
     * @param value The configuration value
     * @param target The configuration target (Global, Workspace, or WorkspaceFolder)
     */
    static updateConfig(key: string, value: any, target: vscode.ConfigurationTarget = vscode.ConfigurationTarget.Global): Thenable<void> {
        const config = vscode.workspace.getConfiguration('extension-v1');
        return config.update(key, value, target);
    }
}
