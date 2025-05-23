/**
 * Simple chat assistant to provide helpful responses
 */

import { detectCommand, commands } from './commands';

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
        "Here are some things you can ask me:\n- Visualize code relationships\n- Show file dependencies\n- Explain how different parts of your code connect\n- Help with understanding specific code patterns",
        "I'm your codebase assistant. I can help you visualize code relationships, understand dependencies, and navigate your project more effectively."
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
    
    // Default response
    return { 
        text: `I received your message: "${message}". How can I help you understand your codebase better?`, 
        command: null 
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
