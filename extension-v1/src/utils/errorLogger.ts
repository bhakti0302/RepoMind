import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Utility class for logging errors in the extension
 */
export class ErrorLogger {
    private static readonly LOG_DIR = 'logs';
    private static readonly MAX_LOG_FILES = 10;

    /**
     * Log an error to a file
     * @param error The error to log
     * @param context Additional context information
     * @returns The path to the log file
     */
    public static logError(error: Error | string, context: Record<string, any> = {}): string {
        try {
            // Get the extension directory
            const extensionDir = vscode.extensions.getExtension('extension-v1')?.extensionUri.fsPath;
            if (!extensionDir) {
                console.error('Could not determine extension directory');
                return '';
            }

            // Create logs directory if it doesn't exist
            const logsDir = path.join(extensionDir, this.LOG_DIR);
            if (!fs.existsSync(logsDir)) {
                fs.mkdirSync(logsDir, { recursive: true });
            }

            // Create log file name with timestamp
            const timestamp = new Date().toISOString().replace(/:/g, '-');
            const logFile = path.join(logsDir, `error_${timestamp}.log`);

            // Format error message
            const errorMessage = typeof error === 'string' ? error : error.message;
            const errorStack = error instanceof Error ? error.stack : '';

            // Create log content
            const logContent = `
ERROR LOG: ${timestamp}
-----------------
ERROR MESSAGE: ${errorMessage}
ERROR STACK: ${errorStack}
CONTEXT: ${JSON.stringify(context, null, 2)}
-----------------
`;

            // Write to log file
            fs.writeFileSync(logFile, logContent);

            // Clean up old log files
            this.cleanupOldLogs(logsDir);

            console.log(`Error logged to: ${logFile}`);
            return logFile;
        } catch (e) {
            console.error('Error while logging error:', e);
            return '';
        }
    }

    /**
     * Clean up old log files to prevent disk space issues
     * @param logsDir The directory containing log files
     */
    private static cleanupOldLogs(logsDir: string): void {
        try {
            const files = fs.readdirSync(logsDir)
                .filter(file => file.startsWith('error_') && file.endsWith('.log'))
                .map(file => ({
                    name: file,
                    path: path.join(logsDir, file),
                    time: fs.statSync(path.join(logsDir, file)).mtime.getTime()
                }))
                .sort((a, b) => b.time - a.time); // Sort by time, newest first

            // Delete old files if there are more than MAX_LOG_FILES
            if (files.length > this.MAX_LOG_FILES) {
                files.slice(this.MAX_LOG_FILES).forEach(file => {
                    try {
                        fs.unlinkSync(file.path);
                    } catch (e) {
                        console.error(`Failed to delete old log file: ${file.path}`, e);
                    }
                });
            }
        } catch (e) {
            console.error('Error cleaning up old log files:', e);
        }
    }

    /**
     * Show the error log in VS Code
     * @param logFile Path to the log file
     */
    public static showErrorLog(logFile: string): void {
        if (logFile && fs.existsSync(logFile)) {
            vscode.workspace.openTextDocument(logFile).then(doc => {
                vscode.window.showTextDocument(doc);
            });
        }
    }
}
