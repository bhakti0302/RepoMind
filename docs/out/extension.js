"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const node_fetch_1 = __importDefault(require("node-fetch"));
function activate(context) {
    console.log('✅ Extension activated!');
    const disposable = vscode.commands.registerCommand('aiCodeAssistant.searchChunks', async () => {
        const query = await vscode.window.showInputBox({ prompt: 'What do you want help with?' });
        if (!query)
            return;
        try {
            const response = await (0, node_fetch_1.default)('http://localhost:8000/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            if (!response.ok) {
                const errText = await response.text();
                vscode.window.showErrorMessage(`❌ Error ${response.status}: ${errText}`);
                return;
            }
            const json = await response.json();
            const output = vscode.window.createOutputChannel('AI Code Assistant');
            output.clear();
            output.appendLine('🔍 Search Results:\n');
            json.matches.forEach((match, i) => {
                output.appendLine(`#${i + 1}: ${match.language} lines ${match.lines}`);
                output.appendLine(match.functions.join('\n---\n') + '\n');
            });
            output.show();
        }
        catch (err) {
            vscode.window.showErrorMessage(`Failed to fetch search results: ${err.message}`);
        }
    });
    context.subscriptions.push(disposable);
}
function deactivate() { }
