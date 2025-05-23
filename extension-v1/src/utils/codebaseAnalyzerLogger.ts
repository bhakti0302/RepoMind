import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { logger } from './logger';

/**
 * CodebaseAnalyzerLogger class for logging codebase analyzer operations.
 * This class wraps the codebase analyzer commands and logs their execution and results.
 */
export class CodebaseAnalyzerLogger {
    private codebaseAnalyserPath: string;

    /**
     * Constructor for the CodebaseAnalyzerLogger.
     * @param codebaseAnalyserPath Path to the codebase-analyser directory
     */
    constructor(codebaseAnalyserPath: string) {
        this.codebaseAnalyserPath = codebaseAnalyserPath;
        logger.info('CodebaseAnalyzerLogger', `Initialized with path: ${codebaseAnalyserPath}`);
    }

    /**
     * Execute a Python script in the codebase analyzer and log the results.
     * @param scriptName Name of the script to execute (e.g., 'analyze_java.py')
     * @param args Arguments to pass to the script
     * @param options Additional options for execution
     * @returns Promise that resolves with the stdout or rejects with an error
     */
    public async executeScript(
        scriptName: string,
        args: string[],
        options: {
            useVenv?: boolean,
            workingDir?: string,
            projectId?: string,
            clearDb?: boolean,
            mockEmbeddings?: boolean
        } = {}
    ): Promise<string> {
        const useVenv = options.useVenv !== undefined ? options.useVenv : true;
        const workingDir = options.workingDir || this.codebaseAnalyserPath;

        // Build the command
        let command = `cd "${workingDir}" && `;

        if (useVenv) {
            command += `if [ -d "venv" ]; then
                source venv/bin/activate && `;
        }

        // Add the script path
        const scriptPath = path.join('scripts', scriptName);
        command += `python3 ${scriptPath}`;

        // Add the arguments
        if (args.length > 0) {
            command += ` ${args.join(' ')}`;
        }

        // Add project ID if provided
        if (options.projectId) {
            command += ` --project-id "${options.projectId}"`;
        }

        // Add clear-db flag if specified
        if (options.clearDb) {
            command += ' --clear-db';
        }

        // Add mock-embeddings flag if specified
        if (options.mockEmbeddings) {
            command += ' --mock-embeddings';
        }

        // Close the venv if used
        if (useVenv) {
            // Add the else part for non-venv execution
            const nonVenvCommand = `python3 ${scriptPath} ${args.join(' ')}`;

            // Add project ID if provided for non-venv
            const nonVenvProjectId = options.projectId ? ` --project-id "${options.projectId}"` : '';

            // Add clear-db flag if specified for non-venv
            const nonVenvClearDb = options.clearDb ? ' --clear-db' : '';

            // Add mock-embeddings flag if specified for non-venv
            const nonVenvMockEmbeddings = options.mockEmbeddings ? ' --mock-embeddings' : '';

            // Combine all parts for the non-venv command
            const fullNonVenvCommand = `${nonVenvCommand}${nonVenvProjectId}${nonVenvClearDb}${nonVenvMockEmbeddings}`;

            // Add the complete if-else structure
            command += ` && deactivate; else ${fullNonVenvCommand}; fi`;
        }

        // Log the command
        logger.info('CodebaseAnalyzerLogger', `Executing command: ${command}`);

        // Execute the command
        return new Promise<string>((resolve, reject) => {
            cp.exec(command, (error, stdout, stderr) => {
                if (error) {
                    logger.error('CodebaseAnalyzerLogger', `Error executing command: ${error.message}`, {
                        command,
                        stderr,
                        stdout,
                        error
                    });
                    reject(error);
                    return;
                }

                if (stderr && stderr.trim() !== '') {
                    logger.warn('CodebaseAnalyzerLogger', `Command produced stderr: ${stderr}`);
                }

                logger.info('CodebaseAnalyzerLogger', `Command executed successfully`);
                logger.debug('CodebaseAnalyzerLogger', `Command output: ${stdout}`);

                resolve(stdout);
            });
        });
    }

    /**
     * Analyze a Java codebase and log the results.
     * @param repoPath Path to the repository to analyze
     * @param projectId Project ID to use for the analysis
     * @param clearDb Whether to clear the database before analysis
     * @param mockEmbeddings Whether to use mock embeddings
     * @returns Promise that resolves with the stdout or rejects with an error
     */
    public async analyzeJava(
        repoPath: string,
        projectId: string,
        clearDb: boolean = false,
        mockEmbeddings: boolean = true
    ): Promise<string> {
        logger.info('CodebaseAnalyzerLogger', `Analyzing Java codebase: ${repoPath}`, {
            projectId,
            clearDb,
            mockEmbeddings
        });

        return this.executeScript('analyze_java.py', [
            `"${repoPath}"`
        ], {
            projectId,
            clearDb,
            mockEmbeddings
        });
    }

    /**
     * Update a codebase analysis and log the results.
     * @param repoPath Path to the repository to update
     * @param projectId Project ID to use for the update
     * @param mockEmbeddings Whether to use mock embeddings
     * @returns Promise that resolves with the stdout or rejects with an error
     */
    public async updateCodebase(
        repoPath: string,
        projectId: string,
        mockEmbeddings: boolean = true
    ): Promise<string> {
        logger.info('CodebaseAnalyzerLogger', `Updating codebase analysis: ${repoPath}`, {
            projectId,
            mockEmbeddings
        });

        return this.executeScript('update_codebase.py', [
            `"${repoPath}"`
        ], {
            projectId,
            mockEmbeddings
        });
    }

    /**
     * Visualize code relationships and log the results.
     * @param repoPath Path to the repository to visualize
     * @param outputDir Directory to output visualizations to
     * @param projectId Project ID to use for the visualization
     * @param timestamp Timestamp to use for the visualization files
     * @returns Promise that resolves with the stdout or rejects with an error
     */
    public async visualizeCodeRelationships(
        repoPath: string,
        outputDir: string,
        projectId: string,
        timestamp?: string
    ): Promise<string> {
        logger.info('CodebaseAnalyzerLogger', `Visualizing code relationships: ${repoPath}`, {
            outputDir,
            projectId,
            timestamp
        });

        const args = [
            `--repo-path "${repoPath}"`,
            `--output-dir "${outputDir}"`,
        ];

        if (timestamp) {
            args.push(`--timestamp "${timestamp}"`);
        }

        return this.executeScript('visualize_code_relationships.py', args, {
            projectId
        });
    }

    /**
     * Visualize all code relationships and log the results.
     * This generates multiple visualization types including:
     * - Multi-file relationships
     * - Relationship types
     * - Class diagram
     * - Package diagram
     * - Dependency graph
     * - Inheritance hierarchy
     *
     * @param repoPath Path to the repository to visualize
     * @param outputDir Directory to output visualizations to
     * @param projectId Project ID to use for the visualization
     * @param timestamp Timestamp to use for the visualization files
     * @returns Promise that resolves with the stdout or rejects with an error
     */
    public async visualizeAllRelationships(
        repoPath: string,
        outputDir: string,
        projectId: string,
        timestamp?: string
    ): Promise<string> {
        logger.info('CodebaseAnalyzerLogger', `Visualizing all code relationships: ${repoPath}`, {
            outputDir,
            projectId,
            timestamp
        });

        const args = [
            `--repo-path "${repoPath}"`,
            `--output-dir "${outputDir}"`,
        ];

        if (timestamp) {
            args.push(`--timestamp "${timestamp}"`);
        }

        return this.executeScript('visualize_all_relationships.py', args, {
            projectId
        });
    }

    /**
     * Get the last sync time for a project and log the result.
     * @param projectId Project ID to get the last sync time for
     * @returns Promise that resolves with the last sync time or rejects with an error
     */
    public async getLastSyncTime(projectId: string): Promise<string> {
        logger.info('CodebaseAnalyzerLogger', `Getting last sync time for project: ${projectId}`);

        const command = `cd "${this.codebaseAnalyserPath}" &&
            if [ -d "venv" ]; then
                source venv/bin/activate &&
                python3 -c "from codebase_analyser.database.unified_storage import UnifiedStorage; import sys; storage = UnifiedStorage(db_path='.lancedb'); timestamp = storage.get_last_sync_time('${projectId}'); print(timestamp if timestamp else 'Unknown')" &&
                deactivate;
            else
                python3 -c "from codebase_analyser.database.unified_storage import UnifiedStorage; import sys; storage = UnifiedStorage(db_path='.lancedb'); timestamp = storage.get_last_sync_time('${projectId}'); print(timestamp if timestamp else 'Unknown')";
            fi`;

        logger.debug('CodebaseAnalyzerLogger', `Executing command: ${command}`);

        return new Promise<string>((resolve, reject) => {
            cp.exec(command, (error, stdout, stderr) => {
                if (error) {
                    logger.error('CodebaseAnalyzerLogger', `Error getting last sync time: ${error.message}`, {
                        command,
                        stderr,
                        stdout,
                        error
                    });
                    reject(error);
                    return;
                }

                const lastSyncTime = stdout.trim();
                logger.info('CodebaseAnalyzerLogger', `Last sync time: ${lastSyncTime}`);
                resolve(lastSyncTime);
            });
        });
    }
}
