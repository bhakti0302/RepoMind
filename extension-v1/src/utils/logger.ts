import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

/**
 * Log levels for the logger.
 */
export enum LogLevel {
    ERROR = 0,
    WARN = 1,
    INFO = 2,
    DEBUG = 3,
    TRACE = 4
}

/**
 * Logger class for the RepoMind extension.
 * Handles logging to a file and console with different log levels.
 */
export class Logger {
    private static instance: Logger;
    private logFile: string;
    private logStream: fs.WriteStream | null = null;
    private logLevel: LogLevel = LogLevel.INFO;
    private maxLogFileSize: number = 10 * 1024 * 1024; // 10MB
    private logDir: string;
    private sessionStartTime: Date;

    /**
     * Log levels for the logger.
     */
    public static readonly LogLevel = LogLevel;

    /**
     * Private constructor to enforce singleton pattern.
     */
    private constructor() {
        this.sessionStartTime = new Date();
        this.logDir = this.getLogDirectory();
        this.logFile = this.getLogFilePath();

        // Print log directory and file path to console for debugging
        console.log(`Logger initialized with log directory: ${this.logDir}`);
        console.log(`Log file path: ${this.logFile}`);

        this.ensureLogDirectoryExists();
        this.initLogStream();
    }

    /**
     * Get the singleton instance of the logger.
     */
    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    /**
     * Set the log level.
     * @param level The log level to set.
     */
    public setLogLevel(level: LogLevel): void {
        this.logLevel = level;
        this.log(LogLevel.INFO, 'Logger', `Log level set to ${LogLevel[level]}`);
    }

    /**
     * Log a message with the specified level.
     * @param level The log level.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param data Additional data to log.
     */
    public log(level: LogLevel, source: string, message: string, data?: any): void {
        if (level < this.logLevel) {
            return;
        }

        const timestamp = new Date().toISOString();
        const levelStr = LogLevel[level].padEnd(5);
        let logMessage = `[${timestamp}] [${levelStr}] [${source}] ${message}`;

        if (data) {
            try {
                if (typeof data === 'object') {
                    logMessage += `\nData: ${JSON.stringify(data, null, 2)}`;
                } else {
                    logMessage += `\nData: ${data}`;
                }
            } catch (error) {
                logMessage += `\nData: [Could not stringify data: ${error}]`;
            }
        }

        // Log to console
        switch (level) {
            case LogLevel.ERROR:
                console.error(logMessage);
                break;
            case LogLevel.WARN:
                console.warn(logMessage);
                break;
            case LogLevel.INFO:
                console.info(logMessage);
                break;
            case LogLevel.DEBUG:
                console.debug(logMessage);
                break;
            case LogLevel.TRACE:
                console.log(logMessage);
                break;
        }

        // Log to file
        this.logToFile(logMessage);

        // Check log file size and rotate if necessary
        this.checkLogFileSize();
    }

    /**
     * Log an error message.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param error The error to log.
     */
    public error(source: string, message: string, error?: any): void {
        this.log(LogLevel.ERROR, source, message, error);
    }

    /**
     * Log a warning message.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param data Additional data to log.
     */
    public warn(source: string, message: string, data?: any): void {
        this.log(LogLevel.WARN, source, message, data);
    }

    /**
     * Log an info message.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param data Additional data to log.
     */
    public info(source: string, message: string, data?: any): void {
        this.log(LogLevel.INFO, source, message, data);
    }

    /**
     * Log a debug message.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param data Additional data to log.
     */
    public debug(source: string, message: string, data?: any): void {
        this.log(LogLevel.DEBUG, source, message, data);
    }

    /**
     * Log a trace message.
     * @param source The source of the log message.
     * @param message The message to log.
     * @param data Additional data to log.
     */
    public trace(source: string, message: string, data?: any): void {
        this.log(LogLevel.TRACE, source, message, data);
    }

    /**
     * Log a function call.
     * @param className The name of the class.
     * @param functionName The name of the function.
     * @param args The arguments passed to the function.
     */
    public logFunctionCall(className: string, functionName: string, args?: any): void {
        this.debug(className, `Function call: ${functionName}()`, args);
    }

    /**
     * Log a function result.
     * @param className The name of the class.
     * @param functionName The name of the function.
     * @param result The result of the function.
     */
    public logFunctionResult(className: string, functionName: string, result?: any): void {
        this.debug(className, `Function result: ${functionName}()`, result);
    }

    /**
     * Close the log stream.
     */
    public close(): void {
        if (this.logStream) {
            this.logStream.end();
            this.logStream = null;
        }
    }

    /**
     * Reset the log file.
     */
    public resetLogFile(): void {
        this.close();
        this.sessionStartTime = new Date();
        this.logFile = this.getLogFilePath();
        this.initLogStream();
        this.info('Logger', 'Log file reset');
    }

    /**
     * Show the log file in VS Code.
     */
    public showLogFile(): void {
        vscode.workspace.openTextDocument(this.logFile).then(doc => {
            vscode.window.showTextDocument(doc);
        });
    }

    /**
     * Get the path to the log directory.
     * Uses a common log folder in the root directory.
     */
    private getLogDirectory(): string {
        console.log('Getting log directory...');

        // Get the extension path
        const extensionPath = vscode.extensions.getExtension('extension-v1')?.extensionPath;
        console.log(`Extension path: ${extensionPath || 'not found'}`);

        if (!extensionPath) {
            // Fallback to workspace path
            const workspaceFolders = vscode.workspace.workspaceFolders;
            console.log(`Workspace folders: ${workspaceFolders ? workspaceFolders.length : 0}`);

            if (!workspaceFolders || workspaceFolders.length === 0) {
                // Fallback to temp directory
                const tempDir = path.join(require('os').tmpdir(), 'repomind-logs');
                console.log(`Using temp directory: ${tempDir}`);
                return tempDir;
            }

            const workspacePath = workspaceFolders[0].uri.fsPath;
            console.log(`Workspace path: ${workspacePath}`);

            // Try to find the root directory (parent of workspace)
            try {
                const workspaceRoot = path.dirname(workspacePath);
                console.log(`Workspace root: ${workspaceRoot}`);

                // Check if this is the RepoMind project by looking for key directories
                const extensionPath = path.join(workspaceRoot, 'extension-v1');
                const analyserPath = path.join(workspaceRoot, 'codebase-analyser');

                console.log(`Checking for extension-v1: ${fs.existsSync(extensionPath)}`);
                console.log(`Checking for codebase-analyser: ${fs.existsSync(analyserPath)}`);

                if (fs.existsSync(extensionPath) && fs.existsSync(analyserPath)) {
                    const rootLogsDir = path.join(workspaceRoot, 'logs');
                    console.log(`Using root logs directory: ${rootLogsDir}`);
                    return rootLogsDir;
                }
            } catch (error) {
                // If any error occurs, fall back to workspace logs
                console.error(`Error finding root directory: ${error}`);
            }

            // Fallback to logs in the workspace
            const workspaceLogsDir = path.join(workspacePath, 'logs');
            console.log(`Using workspace logs directory: ${workspaceLogsDir}`);
            return workspaceLogsDir;
        }

        // Get the workspace root (parent of extension path)
        const workspaceRoot = path.dirname(extensionPath);
        console.log(`Using extension parent directory: ${workspaceRoot}`);
        const logsDir = path.join(workspaceRoot, 'logs');
        console.log(`Final logs directory: ${logsDir}`);
        return logsDir;
    }

    /**
     * Get the path to the log file.
     * Includes project ID in the filename if available.
     */
    private getLogFilePath(): string {
        const timestamp = this.sessionStartTime.toISOString().replace(/:/g, '-').replace(/\..+/, '');

        // Try to get the project ID from the workspace
        let projectId = 'unknown';
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                projectId = path.basename(workspaceFolders[0].uri.fsPath);
            }
        } catch (error) {
            console.error(`Error getting project ID: ${error}`);
        }

        return path.join(this.logDir, `repomind-${projectId}-${timestamp}.log`);
    }

    /**
     * Ensure the log directory exists.
     */
    private ensureLogDirectoryExists(): void {
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }
    }

    /**
     * Initialize the log stream.
     */
    private initLogStream(): void {
        this.logStream = fs.createWriteStream(this.logFile, { flags: 'a' });
        this.logStream.on('error', (error) => {
            console.error(`Error writing to log file: ${error}`);
        });
    }

    /**
     * Log a message to the log file.
     * @param message The message to log.
     */
    private logToFile(message: string): void {
        if (this.logStream) {
            this.logStream.write(message + '\n');
        }
    }

    /**
     * Check the log file size and rotate if necessary.
     */
    private checkLogFileSize(): void {
        try {
            const stats = fs.statSync(this.logFile);
            if (stats.size > this.maxLogFileSize) {
                this.rotateLogFile();
            }
        } catch (error) {
            console.error(`Error checking log file size: ${error}`);
        }
    }

    /**
     * Rotate the log file.
     */
    private rotateLogFile(): void {
        this.close();

        // Rename the current log file
        const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
        const rotatedLogFile = path.join(this.logDir, `repomind-${timestamp}-rotated.log`);

        try {
            fs.renameSync(this.logFile, rotatedLogFile);
        } catch (error) {
            console.error(`Error rotating log file: ${error}`);
        }

        // Create a new log file
        this.initLogStream();
        this.info('Logger', `Log file rotated to ${rotatedLogFile}`);
    }
}

// Export a singleton instance
export const logger = Logger.getInstance();

/**
 * Decorator for logging function calls and results.
 * @param _target The target object (unused).
 * @param propertyKey The property key.
 * @param descriptor The property descriptor.
 */
export function logMethod(_target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = function(...args: any[]) {
        const className = this.constructor.name || 'Unknown';
        const logger = Logger.getInstance();

        // Log function call
        logger.logFunctionCall(className, propertyKey, args);

        try {
            // Call the original method
            const result = originalMethod.apply(this, args);

            // Handle promises
            if (result instanceof Promise) {
                return result.then((resolvedResult) => {
                    // Log function result
                    logger.logFunctionResult(className, propertyKey, resolvedResult);
                    return resolvedResult;
                }).catch((error) => {
                    // Log error
                    logger.error(className, `Error in ${propertyKey}()`, error);
                    throw error;
                });
            } else {
                // Log function result
                logger.logFunctionResult(className, propertyKey, result);
                return result;
            }
        } catch (error) {
            // Log error
            logger.error(className, `Error in ${propertyKey}()`, error);
            throw error;
        }
    };

    return descriptor;
}

