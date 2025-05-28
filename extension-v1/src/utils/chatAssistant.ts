/**
 * Chat assistant to provide helpful responses
 * Uses LLM for code-related questions
 */

import { detectCommand, commands } from './commands';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import * as cp from 'child_process';
import { promisify } from 'util';

const exec = promisify(cp.exec);

// Predefined responses for common queries
const responses = {
    greeting: [
        "Hello! How can I help you with your code today?",
        "Hi there! I'm RepoMind. What would you like to know about your codebase?",
        "Welcome! I'm here to help you understand your code better."
    ],
    farewell: [
        "Goodbye! Let me know if you need help later.",
        "See you later! Feel free to come back with more questions.",
        "Bye for now! I'll be here when you need assistance."
    ],
    thanks: [
        "You're welcome! Is there anything else I can help with?",
        "Happy to help! Let me know if you need anything else.",
        "No problem at all! What else would you like to know?"
    ],
    help: [
        "I can help you understand your codebase better. Try asking me to visualize code relationships, explain specific parts of your code, or help with debugging.",
        "Here are some things you can ask me:\n- Visualize code relationships\n- Show file dependencies\n- Explain how different parts of your code connect\n- Help with understanding specific code patterns\n- Ask questions about your code",
        "I'm your codebase assistant. I can help you visualize code relationships, understand dependencies, and navigate your project more effectively. You can also ask me questions about your code."
    ],
    fallback: [
        "I'm not sure I understand. Could you rephrase that?",
        "I didn't quite catch that. Could you try asking in a different way?",
        "I'm still learning. Could you clarify what you're looking for?"
    ],
    visualization: [
        "I'll show you the code relationships visualization.",
        "Here's a visualization of your code structure.",
        "Let me visualize the code relationships for you."
    ],
    processing: [
        "I'm processing your question. This may take a moment...",
        "Let me think about that. I'll have an answer for you shortly...",
        "I'm analyzing your question. Please wait a moment..."
    ]
};

/**
 * Get a random response from a category
 * @param category The category of response
 * @returns A random response from the category
 */
function getRandomResponse(category: keyof typeof responses): string {
    const options = responses[category];
    return options[Math.floor(Math.random() * options.length)];
}

/**
 * Check if a message is a greeting
 * @param message The message to check
 * @returns True if the message is a greeting
 */
function isGreeting(message: string): boolean {
    const greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'];
    return greetings.some(greeting => message.toLowerCase().includes(greeting));
}

/**
 * Check if a message is a farewell
 * @param message The message to check
 * @returns True if the message is a farewell
 */
function isFarewell(message: string): boolean {
    const farewells = ['bye', 'goodbye', 'see you', 'later', 'farewell'];
    return farewells.some(farewell => message.toLowerCase().includes(farewell));
}

/**
 * Check if a message is a thank you
 * @param message The message to check
 * @returns True if the message is a thank you
 */
function isThanks(message: string): boolean {
    const thanks = ['thanks', 'thank you', 'appreciate', 'grateful'];
    return thanks.some(thank => message.toLowerCase().includes(thank));
}

/**
 * Check if a message is asking for help
 * @param message The message to check
 * @returns True if the message is asking for help
 */
function isHelp(message: string): boolean {
    const help = ['help', 'assist', 'support', 'guide', 'what can you do', 'how do you work'];
    return help.some(h => message.toLowerCase().includes(h));
}

/**
 * Generate a response to a user message
 * @param message The user message
 * @returns The assistant's response
 */
export function generateResponse(message: string): { text: string, command: string | null } {
    // Check for commands first
    const command = detectCommand(message);

    if (command === commands.VISUALIZE_RELATIONSHIPS) {
        return {
            text: getRandomResponse('visualization'),
            command
        };
    }

    // Check for common patterns
    if (isGreeting(message)) {
        return { text: getRandomResponse('greeting'), command: null };
    }

    if (isFarewell(message)) {
        return { text: getRandomResponse('farewell'), command: null };
    }

    if (isThanks(message)) {
        return { text: getRandomResponse('thanks'), command: null };
    }

    if (isHelp(message)) {
        return { text: getRandomResponse('help'), command: null };
    }

    // For code-related questions, return a processing message
    // The actual LLM call will be handled separately
    return {
        text: getRandomResponse('processing'),
        command: commands.PROCESS_CODE_QUESTION
    };
}

/**
 * Suggest corrections for common misspellings
 * @param message The user message
 * @returns Suggested correction or null if no correction needed
 */
export function suggestCorrection(message: string): string | null {
    // Common misspellings of visualization-related terms
    const corrections: Record<string, string> = {
        'visualise': 'visualize',
        'visualisation': 'visualization',
        'visulize': 'visualize',
        'visulization': 'visualization',
        'vizualize': 'visualize',
        'vizualization': 'visualization',
        'dependancies': 'dependencies',
        'dependancy': 'dependency',
        'relashionship': 'relationship',
        'relashionships': 'relationships',
        'relationshp': 'relationship',
        'relationshps': 'relationships',
        'relaionship': 'relationship',
        'relaionships': 'relationships',
        'struture': 'structure',
        'strutures': 'structures',
        'structre': 'structure',
        'structres': 'structures',
        'arhitecture': 'architecture',
        'arhitectures': 'architectures',
        'architecure': 'architecture',
        'architecures': 'architectures'
    };

    // Check for misspellings
    const words = message.toLowerCase().split(/\s+/);
    const correctedWords = words.map(word => corrections[word] || word);

    // If any words were corrected, return the corrected message
    if (words.some((word, i) => word !== correctedWords[i])) {
        return correctedWords.join(' ');
    }

    return null;
}

// Store conversation history in memory
let conversationHistory: { user: string, assistant: string }[] = [];

/**
 * Process a code question using the LLM
 * @param question The question to process
 * @param useHistory Whether to use conversation history
 * @returns A promise that resolves to the LLM's response
 */
export async function processCodeQuestion(question: string, useHistory: boolean = true): Promise<string> {
    try {
        // Path to the run_code_chat.sh script
        const scriptPath = '/Users/sakshi/Documents/RepoMind/codebase-analyser/nlp-analysis/run_code_chat.sh';

        // Check if the script exists
        if (!fs.existsSync(scriptPath)) {
            return `Error: Script not found at ${scriptPath}`;
        }

        // Make the script executable
        await exec(`chmod +x ${scriptPath}`);

        // Create a temporary file with conversation history if needed
        let historyArg = '';
        if (useHistory && conversationHistory.length > 0) {
            const outputDir = '/Users/sakshi/Documents/RepoMind/codebase-analyser/output';

            // Create the output directory if it doesn't exist
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            const historyFile = path.join(outputDir, 'conversation-history.json');
            fs.writeFileSync(historyFile, JSON.stringify(conversationHistory, null, 2));
            historyArg = ` --history-file "${historyFile}"`;

            console.log(`Using conversation history with ${conversationHistory.length} entries`);
        }

        // Execute the script with the question and history
        console.log(`Executing: ${scriptPath} "${question}"${historyArg}`);
        const { stdout, stderr } = await exec(`${scriptPath} "${question}"${historyArg}`);

        // Check if there was an error
        if (stderr) {
            console.error(`Error processing code question: ${stderr}`);
        }

        // Get the response from the output file
        const outputDir = '/Users/sakshi/Documents/RepoMind/codebase-analyser/output';
        const responseFile = path.join(outputDir, 'chat-response.txt');

        // Check if the response file exists
        let response: string;
        if (fs.existsSync(responseFile)) {
            // Read the response file
            response = fs.readFileSync(responseFile, 'utf8');
        } else {
            // Return the stdout if the response file doesn't exist
            response = stdout || 'No response received from the LLM.';
        }

        // Update conversation history
        conversationHistory.push({
            user: question,
            assistant: response
        });

        // Limit history to last 10 exchanges to prevent context overflow
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(conversationHistory.length - 10);
        }

        return response;
    } catch (error) {
        console.error(`Error processing code question: ${error}`);
        return `Error processing your question: ${error instanceof Error ? error.message : String(error)}`;
    }
}

/**
 * Clear the conversation history
 */
export function clearConversationHistory(): void {
    conversationHistory = [];
    console.log('Conversation history cleared');
}
