import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { DirectImageDisplay } from '../utils/directImageDisplay';

/**
 * Test class for displaying visualizations
 */
export class TestVisualizations {
    /**
     * Display all visualizations for a project
     * @param projectId The project ID
     */
    public static displayAllVisualizations(projectId: string): void {
        // Get the workspace root
        const extensionPath = vscode.extensions.getExtension('augmentcode.repomind')?.extensionPath || '';
        const workspaceRoot = path.dirname(extensionPath);
        
        // Define the visualization directories
        const centralVisualizationsDir = path.join(workspaceRoot, 'data', 'visualizations', projectId);
        
        // Get the workspace folder
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder is open. Please open a folder first.');
            return;
        }
        
        const workspaceFolder = workspaceFolders[0].uri.fsPath;
        const workspaceVisualizationsDir = path.join(workspaceFolder, 'visualizations');
        
        // Log the directories
        console.log(`Central visualizations directory: ${centralVisualizationsDir}`);
        console.log(`Workspace visualizations directory: ${workspaceVisualizationsDir}`);
        
        // Check if the directories exist
        const centralDirExists = fs.existsSync(centralVisualizationsDir);
        const workspaceDirExists = fs.existsSync(workspaceVisualizationsDir);
        
        console.log(`Central directory exists: ${centralDirExists}`);
        console.log(`Workspace directory exists: ${workspaceDirExists}`);
        
        // Define the visualization types
        const visualizationTypes = [
            { type: 'multi_file_relationships', title: 'Multi-File Relationships' },
            { type: 'relationship_types', title: 'Relationship Types' },
            { type: 'class_diagram', title: 'Class Diagram' },
            { type: 'package_diagram', title: 'Package Diagram' },
            { type: 'dependency_graph', title: 'Dependency Graph' },
            { type: 'inheritance_hierarchy', title: 'Inheritance Hierarchy' }
        ];
        
        // Display each visualization type
        for (const viz of visualizationTypes) {
            this.displayVisualization(projectId, viz.type, viz.title, centralVisualizationsDir, workspaceVisualizationsDir);
        }
        
        // Display special visualizations
        const specialVisualizations = [
            { filename: 'customer_java_highlight.png', title: 'Customer Java Highlight' },
            { filename: 'project_graph_customer_highlight.png', title: 'Project Graph with Customer Highlight' }
        ];
        
        for (const viz of specialVisualizations) {
            this.displaySpecialVisualization(viz.filename, viz.title, centralVisualizationsDir, workspaceVisualizationsDir);
        }
    }
    
    /**
     * Display a visualization
     * @param projectId The project ID
     * @param type The visualization type
     * @param title The visualization title
     * @param centralDir The central visualizations directory
     * @param workspaceDir The workspace visualizations directory
     */
    private static displayVisualization(
        projectId: string,
        type: string,
        title: string,
        centralDir: string,
        workspaceDir: string
    ): void {
        // Try the workspace directory first
        const workspacePath = path.join(workspaceDir, `${projectId}_${type}.png`);
        if (fs.existsSync(workspacePath)) {
            console.log(`Found ${type} in workspace directory: ${workspacePath}`);
            DirectImageDisplay.showImage(workspacePath, title);
            return;
        }
        
        // Try to find the latest file in the central directory
        if (fs.existsSync(centralDir)) {
            const files = fs.readdirSync(centralDir)
                .filter(file => file.includes(`${projectId}_${type}_`) && file.endsWith('.png'))
                .sort((a, b) => {
                    // Sort by timestamp (newest first)
                    const timestampA = a.match(/(\d{14})/);
                    const timestampB = b.match(/(\d{14})/);
                    if (timestampA && timestampB) {
                        return timestampB[1].localeCompare(timestampA[1]);
                    } else {
                        return 0;
                    }
                });
            
            if (files.length > 0) {
                const latestFile = path.join(centralDir, files[0]);
                console.log(`Found ${type} in central directory: ${latestFile}`);
                DirectImageDisplay.showImage(latestFile, title);
                return;
            }
        }
        
        console.log(`No ${type} visualization found for project ${projectId}`);
        vscode.window.showInformationMessage(`No ${type} visualization found for project ${projectId}`);
    }
    
    /**
     * Display a special visualization
     * @param filename The filename
     * @param title The visualization title
     * @param centralDir The central visualizations directory
     * @param workspaceDir The workspace visualizations directory
     */
    private static displaySpecialVisualization(
        filename: string,
        title: string,
        centralDir: string,
        workspaceDir: string
    ): void {
        // Try the workspace directory first
        const workspacePath = path.join(workspaceDir, filename);
        if (fs.existsSync(workspacePath)) {
            console.log(`Found ${filename} in workspace directory: ${workspacePath}`);
            DirectImageDisplay.showImage(workspacePath, title);
            return;
        }
        
        // Try the central directory
        const centralPath = path.join(centralDir, filename);
        if (fs.existsSync(centralPath)) {
            console.log(`Found ${filename} in central directory: ${centralPath}`);
            DirectImageDisplay.showImage(centralPath, title);
            return;
        }
        
        console.log(`No ${filename} visualization found`);
        vscode.window.showInformationMessage(`No ${filename} visualization found`);
    }
}
