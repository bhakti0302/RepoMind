import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

/**
 * A class to directly display images in a webview panel for testing purposes
 */
export class DirectImageDisplay {
    private static panel: vscode.WebviewPanel | undefined;

    /**
     * Show an image in a webview panel
     * @param imagePath Path to the image file
     * @param title Title for the webview panel
     */
    public static showImage(imagePath: string, title: string): void {
        console.log(`Showing image: ${imagePath}`);

        // Check if the file exists
        if (!fs.existsSync(imagePath)) {
            console.error(`Image file does not exist: ${imagePath}`);
            vscode.window.showErrorMessage(`Image file not found: ${imagePath}`);
            return;
        }

        // Create or show the webview panel
        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'directImageDisplay',
                title,
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [vscode.Uri.file(path.dirname(imagePath))]
                }
            );

            // Handle panel disposal
            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        } else {
            this.panel.title = title;
            this.panel.reveal();
        }

        // Get the webview
        const webview = this.panel.webview;

        // Create a URI for the image file
        const imageUri = vscode.Uri.file(imagePath);
        const webviewUri = webview.asWebviewUri(imageUri);

        // Create a data URI from the image file for direct embedding
        let dataUri = '';
        try {
            const imageBuffer = fs.readFileSync(imagePath);
            const base64Image = imageBuffer.toString('base64');
            const fileExtension = path.extname(imagePath).toLowerCase();
            const mimeType = fileExtension === '.png' ? 'image/png' :
                            fileExtension === '.jpg' || fileExtension === '.jpeg' ? 'image/jpeg' :
                            fileExtension === '.gif' ? 'image/gif' :
                            fileExtension === '.svg' ? 'image/svg+xml' :
                            'application/octet-stream';
            dataUri = `data:${mimeType};base64,${base64Image}`;
        } catch (error) {
            console.error(`Failed to create data URI: ${error}`);
        }

        // Set the HTML content
        webview.html = `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>${title}</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                }
                .image-container {
                    margin: 20px 0;
                    text-align: center;
                    background-color: #f5f5f5;
                    border-radius: 4px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    max-width: 100%;
                }
                .image {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                }
                .caption {
                    margin-top: 10px;
                    font-style: italic;
                    color: #666;
                }
                .path {
                    margin-top: 10px;
                    font-family: monospace;
                    background-color: #eee;
                    padding: 5px;
                    border-radius: 3px;
                    word-break: break-all;
                }
                .error {
                    color: red;
                    font-weight: bold;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <h1>${title}</h1>
            <div class="path">Image path: ${imagePath}</div>
            <div class="image-container">
                <img class="image" src="${webviewUri}" alt="${title}" onerror="handleImageError()">
                <div class="caption">${title}</div>
            </div>
            <div class="image-container">
                <h3>Fallback using Data URI:</h3>
                <img class="image" src="${dataUri}" alt="${title} (Data URI)" onerror="document.getElementById('dataUriError').style.display = 'block'">
                <div id="dataUriError" class="error" style="display: none;">Failed to load image using Data URI</div>
            </div>
            <script>
                function handleImageError() {
                    document.querySelector('.error').style.display = 'block';
                    document.querySelector('.error').textContent = 'Failed to load image using WebView URI';
                }
            </script>
        </body>
        </html>`;
    }
}
