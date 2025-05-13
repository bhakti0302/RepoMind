import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Utility class for directly displaying images in the UI
 */
export class DirectImageDisplay {
    /**
     * Display an image directly in a webview panel
     * @param imagePath Path to the image file
     * @param title Title for the webview panel
     */
    public static showImage(imagePath: string, title: string = 'Image Viewer'): void {
        console.log(`DirectImageDisplay: Showing image at ${imagePath}`);
        
        // Check if the file exists
        if (!fs.existsSync(imagePath)) {
            console.error(`DirectImageDisplay: Image file does not exist: ${imagePath}`);
            vscode.window.showErrorMessage(`Image file not found: ${imagePath}`);
            return;
        }
        
        // Get file stats
        try {
            const stats = fs.statSync(imagePath);
            console.log(`DirectImageDisplay: Image file size: ${stats.size} bytes`);
            
            if (stats.size === 0) {
                console.error(`DirectImageDisplay: Image file is empty: ${imagePath}`);
                vscode.window.showErrorMessage(`Image file is empty: ${imagePath}`);
                return;
            }
        } catch (error) {
            console.error(`DirectImageDisplay: Error checking file stats: ${error}`);
            vscode.window.showErrorMessage(`Error checking image file: ${error}`);
            return;
        }
        
        // Create and show a webview panel
        const panel = vscode.window.createWebviewPanel(
            'imageViewer',
            title,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.file(path.dirname(imagePath))
                ]
            }
        );
        
        // Get the image URI
        const imageUri = vscode.Uri.file(imagePath);
        const webviewUri = panel.webview.asWebviewUri(imageUri);
        
        console.log(`DirectImageDisplay: Image URI: ${imageUri.toString()}`);
        console.log(`DirectImageDisplay: Webview URI: ${webviewUri.toString()}`);
        
        // Set the HTML content
        panel.webview.html = this.getWebviewContent(webviewUri.toString(), path.basename(imagePath));
        
        // Handle messages from the webview
        panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'imageLoaded':
                        console.log(`DirectImageDisplay: Image loaded successfully in webview: ${message.dimensions}`);
                        break;
                    case 'imageError':
                        console.error(`DirectImageDisplay: Error loading image in webview: ${message.error}`);
                        vscode.window.showErrorMessage(`Error loading image: ${message.error}`);
                        break;
                }
            },
            undefined,
            []
        );
    }
    
    /**
     * Get the HTML content for the webview
     * @param imageUri URI of the image to display
     * @param imageName Name of the image file
     */
    private static getWebviewContent(imageUri: string, imageName: string): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Image Viewer: ${imageName}</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                }
                
                h1 {
                    margin-bottom: 20px;
                }
                
                .image-container {
                    max-width: 100%;
                    text-align: center;
                    margin-bottom: 20px;
                }
                
                img {
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ccc;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }
                
                .error {
                    color: #ff0000;
                    padding: 20px;
                    border: 1px solid #ff0000;
                    background-color: #ffeeee;
                    margin-top: 20px;
                }
                
                .info {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #f0f0f0;
                    border-radius: 4px;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <h1>Image Viewer: ${imageName}</h1>
            
            <div class="image-container">
                <img src="${imageUri}" alt="${imageName}" id="image" />
            </div>
            
            <div class="info" id="info">Loading image...</div>
            
            <script>
                const vscode = acquireVsCodeApi();
                const image = document.getElementById('image');
                const info = document.getElementById('info');
                
                image.onload = () => {
                    info.textContent = \`Image loaded successfully. Dimensions: \${image.naturalWidth} x \${image.naturalHeight} pixels\`;
                    vscode.postMessage({
                        command: 'imageLoaded',
                        dimensions: \`\${image.naturalWidth} x \${image.naturalHeight}\`
                    });
                };
                
                image.onerror = (error) => {
                    info.textContent = 'Error loading image.';
                    info.className = 'error';
                    vscode.postMessage({
                        command: 'imageError',
                        error: error.toString()
                    });
                };
            </script>
        </body>
        </html>`;
    }
}
