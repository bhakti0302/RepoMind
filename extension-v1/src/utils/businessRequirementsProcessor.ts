import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as cp from 'child_process';
import { logger } from './logger';
import { ErrorLogger } from './errorLogger';

/**
 * Class for processing business requirements using the nlp-analysis module
 */
export class BusinessRequirementsProcessor {
    private _extensionPath: string;
    private _workspaceRoot: string;
    private _codebaseAnalyserPath: string;
    private _nlpAnalysisPath: string;
    private _outputDir: string;
    private _requirementsDir: string;

    constructor(extensionPath: string) {
        this._extensionPath = extensionPath;
        this._workspaceRoot = path.dirname(extensionPath);
        this._codebaseAnalyserPath = path.join(this._workspaceRoot, 'codebase-analyser');
        this._nlpAnalysisPath = path.join(this._codebaseAnalyserPath, 'nlp-analysis');
        this._outputDir = path.join(this._nlpAnalysisPath, 'output');
        this._requirementsDir = path.join(this._nlpAnalysisPath, 'data', 'test');

        // Create directories if they don't exist
        this._createDirectories();
    }

    /**
     * Create the necessary directories
     */
    private _createDirectories(): void {
        try {
            if (!fs.existsSync(this._outputDir)) {
                fs.mkdirSync(this._outputDir, { recursive: true });
                logger.info('BusinessRequirementsProcessor', `Created output directory: ${this._outputDir}`);
            }

            if (!fs.existsSync(this._requirementsDir)) {
                fs.mkdirSync(this._requirementsDir, { recursive: true });
                logger.info('BusinessRequirementsProcessor', `Created requirements directory: ${this._requirementsDir}`);
            }
        } catch (error) {
            logger.error('BusinessRequirementsProcessor', `Error creating directories: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Process a business requirements file
     * @param filePath Path to the business requirements file
     * @param callback Callback function to call when processing is complete
     */
    public processRequirementsFile(filePath: string, callback: (result: any) => void): void {
        logger.info('BusinessRequirementsProcessor', `Processing requirements file: ${filePath}`);

        // Get the current workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            logger.error('BusinessRequirementsProcessor', 'No workspace folder is open');
            callback({
                status: 'error',
                message: 'No workspace folder is open. Please open a folder first.'
            });
            return;
        }

        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const projectId = path.basename(workspaceFolder);

        // Copy the file to the requirements directory
        const fileName = path.basename(filePath);
        const requirementsFilePath = path.join(this._requirementsDir, fileName);

        try {
            fs.copyFileSync(filePath, requirementsFilePath);
            logger.info('BusinessRequirementsProcessor', `Copied file to requirements directory: ${requirementsFilePath}`);
        } catch (error) {
            logger.error('BusinessRequirementsProcessor', `Error copying file to requirements directory: ${error instanceof Error ? error.message : String(error)}`);
            callback({
                status: 'error',
                message: `Error copying file to requirements directory: ${error instanceof Error ? error.message : String(error)}`
            });
            return;
        }

        // Run the nlp-analysis module
        this._runNlpAnalysis(requirementsFilePath, projectId, callback);
    }

    /**
     * Run the nlp-analysis module
     * @param filePath Path to the business requirements file
     * @param projectId Project ID
     * @param callback Callback function to call when processing is complete
     */
    private _runNlpAnalysis(filePath: string, projectId: string, callback: (result: any) => void): void {
        logger.info('BusinessRequirementsProcessor', `Running NLP analysis on file: ${filePath}`);

        // Check if the simple_processor.py script exists
        const simpleProcessorPath = path.join(this._nlpAnalysisPath, 'simple_processor.py');
        if (fs.existsSync(simpleProcessorPath)) {
            logger.info('BusinessRequirementsProcessor', `Using simple processor: ${simpleProcessorPath}`);

            // Create the command to run the simple processor
            const command = `cd "${this._nlpAnalysisPath}" && python3 simple_processor.py --file "${filePath}" --project-id "${projectId}" --output-dir "${this._outputDir}" --data-dir "../../data"`;
            logger.info('BusinessRequirementsProcessor', `Running command: ${command}`);
            return this._executeCommand(command, callback);
        }

        // Check if the process_business_requirements.py script exists
        const scriptPath = path.join(this._nlpAnalysisPath, 'process_business_requirements.py');
        if (!fs.existsSync(scriptPath)) {
            // Fall back to test_system.py if process_business_requirements.py doesn't exist
            const fallbackScriptPath = path.join(this._nlpAnalysisPath, 'test_system.py');
            if (!fs.existsSync(fallbackScriptPath)) {
                logger.error('BusinessRequirementsProcessor', `Script not found: ${scriptPath} or ${fallbackScriptPath}`);
                callback({
                    status: 'error',
                    message: `Script not found: ${scriptPath} or ${fallbackScriptPath}`
                });
                return;
            }

            logger.info('BusinessRequirementsProcessor', `Using fallback script: ${fallbackScriptPath}`);

            // Create the command to run the fallback script
            const command = `cd "${this._nlpAnalysisPath}" && python3 test_system.py --input-file "${filePath}" --output-dir "${this._outputDir}" --project-id "${projectId}"`;
            logger.info('BusinessRequirementsProcessor', `Running command: ${command}`);
            return this._executeCommand(command, callback);
        }

        // Create the command to run the script
        const command = `cd "${this._nlpAnalysisPath}" && python3 process_business_requirements.py --file "${filePath}" --project-id "${projectId}" --output-dir "${this._outputDir}" --data-dir "../../data"`;
        logger.info('BusinessRequirementsProcessor', `Running command: ${command}`);

        // Execute the command
        this._executeCommand(command, callback);
    }

    /**
     * Execute a command and handle the result
     * @param command Command to execute
     * @param callback Callback function to call when execution is complete
     */
    private _executeCommand(command: string, callback: (result: any) => void): void {
        cp.exec(command, (error, stdout, stderr) => {
            if (error) {
                logger.error('BusinessRequirementsProcessor', `Error running command: ${error.message}`);
                logger.error('BusinessRequirementsProcessor', `Stderr: ${stderr}`);

                // Log the error to a file
                const logFile = ErrorLogger.logError(error, {
                    command,
                    stderr,
                    stdout
                });

                callback({
                    status: 'error',
                    message: `Error running command: ${error.message}`,
                    logFile
                });
                return;
            }

            logger.info('BusinessRequirementsProcessor', `NLP analysis completed successfully`);
            logger.info('BusinessRequirementsProcessor', `Stdout: ${stdout}`);

            // Check for output from the simple processor
            const projectOutputDir = path.join(this._outputDir, stdout.includes('Generated code saved to:') ? stdout.split('Generated code saved to:')[1].trim().split('/').slice(-2)[0] : '');
            const generatedCodeFile = stdout.includes('Generated code saved to:') ? stdout.split('Generated code saved to:')[1].trim() : '';

            // Check if the output files exist
            const instructionsFile = path.join(this._outputDir, 'llm-instructions.txt');
            const outputFile = path.join(this._outputDir, 'llm-output.txt');

            let instructions = '';
            let generatedCode = '';

            try {
                // First try to read from the simple processor output
                if (generatedCodeFile && fs.existsSync(generatedCodeFile)) {
                    generatedCode = fs.readFileSync(generatedCodeFile, 'utf8');
                    logger.info('BusinessRequirementsProcessor', `Read generated code file: ${generatedCodeFile}`);
                }
                // Fall back to the standard output files
                else {
                    if (fs.existsSync(instructionsFile)) {
                        instructions = fs.readFileSync(instructionsFile, 'utf8');
                        logger.info('BusinessRequirementsProcessor', `Read instructions file: ${instructionsFile}`);
                    }

                    if (fs.existsSync(outputFile)) {
                        generatedCode = fs.readFileSync(outputFile, 'utf8');
                        logger.info('BusinessRequirementsProcessor', `Read output file: ${outputFile}`);
                    }
                }

                callback({
                    status: 'success',
                    message: 'NLP analysis completed successfully',
                    instructions,
                    generatedCode,
                    instructionsFile,
                    outputFile
                });
            } catch (readError) {
                logger.error('BusinessRequirementsProcessor', `Error reading output files: ${readError instanceof Error ? readError.message : String(readError)}`);
                callback({
                    status: 'error',
                    message: `Error reading output files: ${readError instanceof Error ? readError.message : String(readError)}`
                });
            }
        });
    }
}
