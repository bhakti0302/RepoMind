import * as vscode from 'vscode';
import fetch from 'node-fetch';

type Match = {
  id: string;
  language: string;
  lines: string;
  functions: string[];
  imports: string[];
};

export function activate(context: vscode.ExtensionContext) {
  console.log('✅ Extension activated!');
  const disposable = vscode.commands.registerCommand('aiCodeAssistant.searchChunks', async () => {
    const query = await vscode.window.showInputBox({ prompt: 'What do you want help with?' });
    if (!query) return;

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!response.ok) {
        const errText = await response.text();
        vscode.window.showErrorMessage(`❌ Error ${response.status}: ${errText}`);
        return;
      }
      const json = await response.json() as { matches: Match[] };

      const output = vscode.window.createOutputChannel('AI Code Assistant');
      output.clear();
      output.appendLine('🔍 Search Results:\n');
      json.matches.forEach((match, i) => {
        output.appendLine(`#${i + 1}: ${match.language} lines ${match.lines}`);
        output.appendLine(match.functions.join('\n---\n') + '\n');
      });
      output.show();
    } catch (err: any) {
      vscode.window.showErrorMessage(`Failed to fetch search results: ${err.message}`);
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
