// This is a patch for the extension-v1/src/extension.ts file
// Find the visualizeRelationshipsCommand function and replace the part that parses the JSON output

// Original code:
/*
try {
    // Parse the JSON output to get the visualization paths
    const result = JSON.parse(stdout);

    // Show success message with links to open the visualizations
    vscode.window.showInformationMessage('Code relationships visualized successfully!',
        'Open Multi-File Relationships', 'Open Relationship Types')
        .then(selection => {
            if (selection === 'Open Multi-File Relationships') {
                // Open the multi-file relationships visualization
                const multiFileVisualizationPath = result.multi_file_relationships;
                vscode.env.openExternal(vscode.Uri.file(multiFileVisualizationPath));
            } else if (selection === 'Open Relationship Types') {
                // Open the relationship types visualization
                const relationshipTypesVisualizationPath = result.relationship_types;
                vscode.env.openExternal(vscode.Uri.file(relationshipTypesVisualizationPath));
            }
        });

    statusBar.setReady('Visualizations created');
    resolve();
} catch (parseError) {
    console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
    vscode.window.showErrorMessage('Visualizations created, but could not parse the result.');
    statusBar.setReady('Visualizations created');
    resolve();
}
*/

// New code:
/*
try {
    // Extract JSON from the output using markers
    let jsonOutput = stdout;
    const beginMarker = "JSON_OUTPUT_BEGINS";
    const endMarker = "JSON_OUTPUT_ENDS";
    
    const beginIndex = stdout.indexOf(beginMarker);
    const endIndex = stdout.indexOf(endMarker);
    
    if (beginIndex !== -1 && endIndex !== -1) {
        // Extract the JSON part between the markers
        jsonOutput = stdout.substring(beginIndex + beginMarker.length, endIndex).trim();
    } else {
        // If markers not found, try to parse the whole output as JSON
        console.log("JSON markers not found, trying to parse the entire output");
    }
    
    // Parse the JSON output to get the visualization paths
    const result = JSON.parse(jsonOutput);

    // Show success message with links to open the visualizations
    vscode.window.showInformationMessage('Code relationships visualized successfully!',
        'Open Multi-File Relationships', 'Open Relationship Types')
        .then(selection => {
            if (selection === 'Open Multi-File Relationships') {
                // Open the multi-file relationships visualization
                const multiFileVisualizationPath = result.multi_file_relationships;
                vscode.env.openExternal(vscode.Uri.file(multiFileVisualizationPath));
            } else if (selection === 'Open Relationship Types') {
                // Open the relationship types visualization
                const relationshipTypesVisualizationPath = result.relationship_types;
                vscode.env.openExternal(vscode.Uri.file(relationshipTypesVisualizationPath));
            }
        });

    statusBar.setReady('Visualizations created');
    resolve();
} catch (parseError) {
    console.error(`Error parsing visualization result: ${parseError instanceof Error ? parseError.message : String(parseError)}`);
    console.error(`Raw output: ${stdout}`);
    
    // Check if visualizations were created despite the parsing error
    const visualizationDir = path.join(workspaceFolder, '.repomind', 'visualizations');
    const multiFilePath = path.join(visualizationDir, `${projectId}_multi_file_relationships.png`);
    const relationshipTypesPath = path.join(visualizationDir, `${projectId}_relationship_types.png`);
    
    if (fs.existsSync(multiFilePath) || fs.existsSync(relationshipTypesPath)) {
        vscode.window.showInformationMessage('Visualizations created, but could not parse the result.',
            'Show in Chat')
            .then(selection => {
                if (selection === 'Show in Chat') {
                    vscode.commands.executeCommand('extension-v1.showVisualizationsInChat');
                }
            });
    } else {
        vscode.window.showErrorMessage('Failed to create visualizations.');
    }
    
    statusBar.setReady('Visualizations created');
    resolve();
}
*/
