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
 * Check if a message is asking for help about the assistant itself (not code)
 * @param message The message to check
 * @returns True if the message is asking for help about the assistant
 */
function isHelp(message: string): boolean {
    const lowerMessage = message.toLowerCase();

    // Only consider it help if it's specifically asking about the assistant's capabilities
    const helpPatterns = [
        'what can you do',
        'how do you work',
        'what are your capabilities',
        'what features do you have',
        'how can you help me',
        'what commands do you support'
    ];

    // Check for exact help patterns, not just keywords
    return helpPatterns.some(pattern => lowerMessage.includes(pattern)) ||
           (lowerMessage === 'help' || lowerMessage === 'assist' || lowerMessage === 'support');
}

/**
 * Check if a message is asking about the codebase/project
 * @param message The message to check
 * @returns True if the message is about code/project
 */
function isCodeQuestion(message: string): boolean {
    const lowerMessage = message.toLowerCase();

    // Keywords that indicate code/project questions
    const codeKeywords = [
        'project', 'code', 'class', 'function', 'method', 'file', 'main.java',
        'employee', 'service', 'architecture', 'structure', 'design',
        'enhance', 'improve', 'feature', 'functionality', 'implement',
        'what does', 'how does', 'explain', 'understand', 'analyze',
        'best practice', 'recommendation', 'suggest', 'optimize'
    ];

    return codeKeywords.some(keyword => lowerMessage.includes(keyword));
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

    // Check for common patterns (but prioritize code questions)
    if (isCodeQuestion(message)) {
        // This is a code-related question, send to LLM processing
        return {
            text: getRandomResponse('processing'),
            command: commands.PROCESS_CODE_QUESTION
        };
    }

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

    // For any other questions, assume they might be code-related
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
        // First, try to get local project data for specific patterns
        const localResponse = await tryLocalProjectData(question);
        if (localResponse) {
            console.log('Using local project data for response');

            // Update conversation history
            conversationHistory.push({
                user: question,
                assistant: localResponse
            });

            // Limit history to last 10 exchanges to prevent context overflow
            if (conversationHistory.length > 10) {
                conversationHistory = conversationHistory.slice(conversationHistory.length - 10);
            }

            return localResponse;
        }

        // For generic questions, try to generate a context-aware response
        const contextAwareResponse = await generateContextAwareResponse(question);
        if (contextAwareResponse) {
            console.log('Using context-aware response for generic question');

            // Update conversation history
            conversationHistory.push({
                user: question,
                assistant: contextAwareResponse
            });

            // Limit history to last 10 exchanges to prevent context overflow
            if (conversationHistory.length > 10) {
                conversationHistory = conversationHistory.slice(conversationHistory.length - 10);
            }

            return contextAwareResponse;
        }

        // If no local response found, try LLM with codebase context
        console.log('No local response found, trying LLM with codebase context');
        const llmWithContextResponse = await processWithLLMAndContext(question);
        if (llmWithContextResponse) {
            console.log('Using LLM with codebase context');

            // Update conversation history
            conversationHistory.push({
                user: question,
                assistant: llmWithContextResponse
            });

            // Limit history to last 10 exchanges to prevent context overflow
            if (conversationHistory.length > 10) {
                conversationHistory = conversationHistory.slice(conversationHistory.length - 10);
            }

            return llmWithContextResponse;
        }

        // Path to the run_code_chat.sh script
        const scriptPath = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis/run_code_chat.sh';

        // Check if the script exists
        if (!fs.existsSync(scriptPath)) {
            return `Error: Script not found at ${scriptPath}`;
        }

        // Make the script executable
        await exec(`chmod +x ${scriptPath}`);

        // Create a temporary file with conversation history if needed
        let historyArg = '';
        if (useHistory && conversationHistory.length > 0) {
            const outputDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output';

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
        const outputDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output';
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
 * Generate context-aware responses for generic questions using project data
 * Now sends ALL questions to LLM for proper analysis - no more template responses
 */
async function generateContextAwareResponse(question: string): Promise<string | null> {
    try {
        // Send ALL questions to LLM for proper analysis with full codebase context
        // This ensures every coding question gets expert-level analysis
        // rather than generic template responses

        console.log('Sending question to LLM for comprehensive analysis:', question);
        return null; // Always trigger LLM processing for coding questions

    } catch (error) {
        console.error('Error in generateContextAwareResponse:', error);
        return null;
    }
}

/**
 * Try to answer questions using local project data when LLM is not available
 * Only handles VERY basic informational queries - everything else goes to LLM
 */
async function tryLocalProjectData(question: string): Promise<string | null> {
    try {
        const lowerQuestion = question.toLowerCase().trim();

        // Only handle extremely basic informational queries
        // Send ALL other questions to LLM for proper analysis

        // "What does this project do?" - very specific pattern only
        if (lowerQuestion === 'what does this project do?' ||
            lowerQuestion === 'what does this project do' ||
            lowerQuestion === 'what is the purpose of this project?' ||
            lowerQuestion === 'what is the purpose of this project') {
            return getProjectPurpose();
        }

        // "What are the classes in this project?" - very specific pattern only
        if (lowerQuestion === 'what are the classes in this project?' ||
            lowerQuestion === 'what are the classes in this project' ||
            lowerQuestion === 'list the classes in this project' ||
            lowerQuestion === 'show me the classes in this project') {
            return getProjectClasses();
        }

        // "What does main.java do?" - very specific pattern only
        if (lowerQuestion === 'what does main.java do?' ||
            lowerQuestion === 'what does main.java do' ||
            lowerQuestion === 'what is in main.java' ||
            lowerQuestion === 'what is in main.java?') {
            return getMainJavaInfo();
        }

        // Send EVERYTHING else to LLM for proper analysis
        // This includes:
        // - All "how" questions
        // - All "why" questions
        // - All analysis requests
        // - All implementation questions
        // - All code-related queries
        // - All technical questions
        return null;
    } catch (error) {
        console.error('Error in tryLocalProjectData:', error);
        return null;
    }
}

/**
 * Get information about what the project does
 * Generic function that works with any project
 */
function getProjectPurpose(): string | null {
    try {
        const lancedbDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb';

        if (!fs.existsSync(lancedbDir)) {
            return null;
        }

        // Find any JSON chunk file in the directory
        const files = fs.readdirSync(lancedbDir);
        const chunkFile = files.find(file => file.endsWith('_chunks.json'));

        if (!chunkFile) {
            return null;
        }

        const chunksFilePath = path.join(lancedbDir, chunkFile);
        const chunks = JSON.parse(fs.readFileSync(chunksFilePath, 'utf8'));

        // Extract project name from filename
        const projectName = chunkFile.replace('_chunks.json', '');

        // Detect primary technology
        let primaryTech = 'Software';
        if (chunks.some((chunk: any) => chunk.file_path?.endsWith('.java'))) primaryTech = 'Java';
        else if (chunks.some((chunk: any) => chunk.file_path?.endsWith('.py'))) primaryTech = 'Python';
        else if (chunks.some((chunk: any) => chunk.file_path?.endsWith('.js') || chunk.file_path?.endsWith('.ts'))) primaryTech = 'JavaScript/TypeScript';

        let response = `## 🎯 What This Project Does\n\n`;
        response += `**${projectName}** is a ${primaryTech}-based application with ${chunks.length} main components.\n\n`;

        response += `### 🏢 **Primary Purpose**\n`;
        response += `This application appears to be a ${primaryTech} project with the following characteristics:\n`;
        response += `- **Components**: ${chunks.length} main code components\n`;
        response += `- **Architecture**: Organized in a structured manner\n`;
        response += `- **Technology**: Built using ${primaryTech}\n\n`;

        response += `### 🔧 **Core Components**\n`;
        chunks.forEach((chunk: any, index: number) => {
            response += `${index + 1}. **${chunk.name}**: ${chunk.chunk_type || 'Component'}\n`;
        });
        response += `\n`;

        response += `### 🏗️ **Technical Implementation**\n`;
        response += `- **Language**: ${primaryTech}\n`;
        response += `- **Components**: ${chunks.length} main components\n`;
        response += `- **Structure**: Modular design\n\n`;

        response += `### 📋 **Project Structure**\n`;
        const packages = [...new Set(chunks.map((chunk: any) => {
            const packageMatch = chunk.content?.match(/package\s+([^;]+);/);
            return packageMatch ? packageMatch[1] : null;
        }).filter(Boolean))];

        if (packages.length > 0) {
            response += `**Packages/Modules**:\n`;
            packages.forEach(pkg => {
                response += `- \`${pkg}\`\n`;
            });
            response += `\n`;
        }

        response += `### 🎓 **Analysis**\n`;
        response += `This project demonstrates:\n`;
        response += `- Structured code organization\n`;
        response += `- Modular architecture\n`;
        response += `- ${primaryTech} development practices\n\n`;

        response += `For detailed analysis of specific components, functionality, or implementation details, please ask more specific questions about the codebase.`;

        return response;
    } catch (error) {
        console.error('Error getting project purpose:', error);
        return null;
    }
}

/**
 * Get information about classes in the project
 * Generic function that works with any project
 */
function getProjectClasses(): string | null {
    try {
        const lancedbDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb';

        if (!fs.existsSync(lancedbDir)) {
            return null;
        }

        // Find any JSON chunk file in the directory
        const files = fs.readdirSync(lancedbDir);
        const chunkFile = files.find(file => file.endsWith('_chunks.json'));

        if (!chunkFile) {
            return null;
        }

        const chunksFilePath = path.join(lancedbDir, chunkFile);
        const chunks = JSON.parse(fs.readFileSync(chunksFilePath, 'utf8'));

        // Extract project name from filename
        const projectName = chunkFile.replace('_chunks.json', '');

        let response = `## Classes in the ${projectName} Project\n\n`;
        response += `Based on the codebase analysis, here are the classes found in this project:\n\n`;

        chunks.forEach((chunk: any, index: number) => {
            response += `### ${index + 1}. **${chunk.name}**\n`;
            response += `- **Package**: ${chunk.content?.match(/package\s+([^;]+);/)?.[1] || 'N/A'}\n`;
            response += `- **Location**: \`${chunk.file_path}\`\n`;
            response += `- **Type**: ${chunk.chunk_type || 'Component'}\n`;
            response += `- **Lines**: ${chunk.start_line}-${chunk.end_line}\n\n`;

            // Generic purpose description
            response += `- **Purpose**: ${chunk.chunk_type || 'Code component'} in the ${projectName} project\n`;
            response += `\n`;
        });

        response += `### Summary\n`;
        response += `The project contains ${chunks.length} main components organized in a structured manner.\n`;

        // Show package structure if available
        const packages = [...new Set(chunks.map((chunk: any) => chunk.content?.match(/package\s+([^;]+);/)?.[1]).filter(Boolean))];
        if (packages.length > 0) {
            response += `\n**Package Structure**:\n`;
            packages.forEach(pkg => {
                response += `- \`${pkg}\`\n`;
            });
        }

        response += `\nFor detailed analysis of specific components or their relationships, please ask more specific questions about the codebase.`;

        return response;
    } catch (error) {
        console.error('Error getting project classes:', error);
        return null;
    }
}

/**
 * Get information about Main.java - Generic version for any project
 */
function getMainJavaInfo(): string | null {
    try {
        const lancedbDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb';

        if (!fs.existsSync(lancedbDir)) {
            return null;
        }

        // Find any JSON chunk file in the directory
        const files = fs.readdirSync(lancedbDir);
        const chunkFile = files.find(file => file.endsWith('_chunks.json'));

        if (!chunkFile) {
            return null;
        }

        const chunksFilePath = path.join(lancedbDir, chunkFile);
        const chunks = JSON.parse(fs.readFileSync(chunksFilePath, 'utf8'));

        // Extract project name from filename
        const projectName = chunkFile.replace('_chunks.json', '');

        const mainChunk = chunks.find((chunk: any) => chunk.name === 'Main');

        if (!mainChunk) {
            return null;
        }

        let response = `## What Main.java Does\n\n`;
        response += `**Main.java** is the entry point of the ${projectName} application.\n\n`;

        response += `### 🎯 Primary Function\n`;
        response += `Serves as the main entry point for the application.\n\n`;

        response += `### 🔍 Technical Details\n`;
        const packageMatch = mainChunk.content?.match(/package\s+([^;]+);/);
        if (packageMatch) {
            response += `- **Package**: \`${packageMatch[1]}\`\n`;
        }
        response += `- **Location**: \`${mainChunk.file_path}\`\n`;
        response += `- **Lines**: ${mainChunk.start_line}-${mainChunk.end_line}\n`;
        response += `- **Type**: ${mainChunk.chunk_type || 'Main class'}\n\n`;

        response += `### 🏗️ Architecture Role\n`;
        response += `Main.java serves as the application entry point and demonstrates the system's core functionality.\n\n`;

        response += `For detailed analysis of the main method's implementation, dependencies, or specific functionality, please ask more specific questions about the code.`;

        return response;
    } catch (error) {
        console.error('Error getting Main.java info:', error);
        return null;
    }
}

// Removed getEmployeeInfo() function - no longer needed since all questions go to LLM

/**
 * Get project context for generic question processing
 * Dynamically detects project from available chunk files
 */
async function getProjectContext(): Promise<any> {
    try {
        const lancedbDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb';

        if (!fs.existsSync(lancedbDir)) {
            return null;
        }

        // Find any JSON chunk file in the directory
        const files = fs.readdirSync(lancedbDir);
        const chunkFile = files.find(file => file.endsWith('_chunks.json'));

        if (!chunkFile) {
            return null;
        }

        const chunksFilePath = path.join(lancedbDir, chunkFile);
        const chunks = JSON.parse(fs.readFileSync(chunksFilePath, 'utf8'));

        // Extract project name from filename (remove _chunks.json)
        const projectName = chunkFile.replace('_chunks.json', '');

        // Detect technologies based on file extensions and content
        const technologies = new Set<string>();
        chunks.forEach((chunk: any) => {
            if (chunk.file_path?.endsWith('.java')) technologies.add('Java');
            if (chunk.file_path?.endsWith('.py')) technologies.add('Python');
            if (chunk.file_path?.endsWith('.js') || chunk.file_path?.endsWith('.ts')) technologies.add('JavaScript/TypeScript');
            if (chunk.file_path?.endsWith('.cpp') || chunk.file_path?.endsWith('.c')) technologies.add('C/C++');
            if (chunk.content?.includes('class ')) technologies.add('Object-Oriented Programming');
        });

        return {
            projectName: projectName,
            classes: chunks,
            totalClasses: chunks.length,
            packages: [...new Set(chunks.map((chunk: any) => chunk.content.match(/package\s+([^;]+);/)?.[1]).filter(Boolean))],
            technologies: Array.from(technologies),
            architecture: 'Layered Architecture' // Generic default
        };
    } catch (error) {
        console.error('Error getting project context:', error);
        return null;
    }
}

// Removed template generation functions - all questions now go to LLM for proper analysis

// Removed generateArchitectureAnalysis - LLM provides better analysis

// Removed generateFeatureSuggestions - LLM provides better analysis

// Removed all remaining template functions - LLM provides superior analysis

/**
 * Process question with LLM using codebase context
 */
async function processWithLLMAndContext(question: string): Promise<string | null> {
    try {
        // Get codebase context
        const projectContext = await getProjectContext();
        if (!projectContext) {
            console.log('No project context available for LLM processing');
            return null;
        }

        // Build enhanced prompt with codebase context
        let contextPrompt = `You are a helpful coding assistant analyzing a codebase. Here's the context:\n\n`;

        contextPrompt += `## Project Information\n`;
        contextPrompt += `- **Name**: ${projectContext.projectName}\n`;
        contextPrompt += `- **Type**: Java Application\n`;
        contextPrompt += `- **Architecture**: ${projectContext.architecture}\n`;
        contextPrompt += `- **Classes**: ${projectContext.totalClasses}\n\n`;

        contextPrompt += `## Codebase Structure\n`;
        projectContext.classes.forEach((chunk: any, index: number) => {
            contextPrompt += `### ${index + 1}. ${chunk.name} Class\n`;
            contextPrompt += `- **Package**: ${chunk.content.match(/package\s+([^;]+);/)?.[1] || 'N/A'}\n`;
            contextPrompt += `- **File**: ${chunk.file_path}\n`;
            contextPrompt += `- **Lines**: ${chunk.start_line}-${chunk.end_line}\n`;
            contextPrompt += `- **Code**:\n\`\`\`java\n${chunk.content}\n\`\`\`\n\n`;
        });

        contextPrompt += `## User Question\n`;
        contextPrompt += `${question}\n\n`;

        contextPrompt += `Please provide a detailed, helpful response based on the codebase context above. `;
        contextPrompt += `Format your response in markdown with clear headings and explanations.`;

        // Try to call the LLM script with the enhanced prompt
        const scriptPath = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis/run_code_chat.sh';

        if (!fs.existsSync(scriptPath)) {
            console.log('LLM script not found, cannot process with context');
            return null;
        }

        // Make the script executable
        await exec(`chmod +x ${scriptPath}`);

        // Create output directory if it doesn't exist
        const outputDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output';
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Write the enhanced prompt to a temporary file
        const promptFile = path.join(outputDir, 'enhanced-prompt.txt');
        fs.writeFileSync(promptFile, contextPrompt);

        // Execute the script with the enhanced prompt
        console.log(`Executing LLM with context: ${scriptPath} "${contextPrompt.substring(0, 100)}..."`);
        const { stdout, stderr } = await exec(`${scriptPath} "${contextPrompt}"`);

        if (stderr) {
            console.error(`LLM processing error: ${stderr}`);
        }

        // Get the response from the output file
        const responseFile = path.join(outputDir, 'chat-response.txt');

        let response: string | null = null;
        if (fs.existsSync(responseFile)) {
            response = fs.readFileSync(responseFile, 'utf8');
        } else {
            response = stdout || null;
        }

        if (response && response.trim()) {
            return `## 🤖 AI Analysis with Codebase Context\n\n${response}`;
        }

        return null;
    } catch (error) {
        console.error('Error in processWithLLMAndContext:', error);
        return null;
    }
}

/**
 * Clear the conversation history
 */
export function clearConversationHistory(): void {
    conversationHistory = [];
    console.log('Conversation history cleared');
}
