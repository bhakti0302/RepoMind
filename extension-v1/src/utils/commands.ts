/**
 * This file contains all the commands and keywords used in the extension.
 * Centralizing these makes it easier to maintain and extend the command vocabulary.
 */

/**
 * Keywords that trigger visualization of code relationships
 */
export const visualizationKeywords = [
    'visualize code relationships',
    'visualize relationships',
    'show code relationships',
    'show relationships',
    'code visualization',
    'relationship visualization',
    'show visualizations',
    'generate visualizations',
    'display code relationships',
    'display visualizations',
    'show me the code structure',
    'how does the code relate',
    'code dependencies',
    'class relationships',
    'method relationships',
    'code graph',
    'code structure',
    'code architecture',
    'visualize code',
    'visualize the codebase',
    'let\'s visualize',
    'can you visualize',
    'can you show me',
    'show me how',
    'show me the relationships',
    'show me the dependencies',
    'show me the structure',
    'show me the architecture',
    'show me the code graph',
    'show me the code relationships',
    'show me the code dependencies',
    'show me the code structure',
    'show me the code architecture',
    'show me the code graph',
    'show me the code visualization',
    'show me the relationship visualization',
    'show me the code relationships visualization',
    'show me the code dependencies visualization',
    'show me the code structure visualization',
    'show me the code architecture visualization',
    'show me the code graph visualization',
    'i want to see',
    'i want to see the code',
    'i want to see the relationships',
    'i want to see the dependencies',
    'i want to see the structure',
    'i want to see the architecture',
    'i want to see the graph',
    'i want to see the visualization',
    'visualize this',
    'visualize that',
    'visualize it',
    'visualize the code',
    'visualize the relationships',
    'visualize the dependencies',
    'visualize the structure',
    'visualize the architecture',
    'visualize the graph'
];

/**
 * Keywords that trigger multi-file relationship visualization
 */
export const multiFileKeywords = [
    'multi-file relationships',
    'file relationships',
    'file dependencies',
    'how files relate',
    'file structure',
    'file connections',
    'file imports',
    'file exports',
    'file references',
    'file usage',
    'file hierarchy',
    'file organization',
    'file architecture',
    'file graph',
    'file visualization',
    'how files connect',
    'how files depend',
    'how files relate',
    'how files are organized',
    'how files are structured',
    'how files are architected',
    'how files are related',
    'how files are dependent',
    'how files are connected',
    'how files are used',
    'how files are referenced',
    'how files are imported',
    'how files are exported'
];

/**
 * Keywords that trigger relationship types visualization
 */
export const relationshipTypesKeywords = [
    'relationship types',
    'types of relationships',
    'class hierarchy',
    'inheritance structure',
    'implementation relationships',
    'class diagram',
    'object relationships',
    'inheritance relationships',
    'implementation relationships',
    'composition relationships',
    'aggregation relationships',
    'association relationships',
    'dependency relationships',
    'realization relationships',
    'generalization relationships',
    'specialization relationships',
    'interface relationships',
    'abstract class relationships',
    'concrete class relationships',
    'parent-child relationships',
    'super-sub relationships',
    'base-derived relationships',
    'interface-implementation relationships',
    'class-object relationships',
    'object-class relationships',
    'class-interface relationships',
    'interface-class relationships',
    'class-abstract class relationships',
    'abstract class-class relationships',
    'class-concrete class relationships',
    'concrete class-class relationships',
    'uml diagram',
    'uml class diagram'
];

/**
 * Command names used in the extension
 */
export const commands = {
    // Chat view commands
    SEND_MESSAGE: 'sendMessage',
    ADD_MESSAGE: 'addMessage',
    UPDATE_MESSAGE: 'updateMessage',
    SYNC_CODEBASE: 'syncCodebase',
    ATTACH_FILE: 'attachFile',
    VISUALIZE_RELATIONSHIPS: 'visualizeRelationships',
    OPEN_IMAGE: 'openImage',
    PROCESS_CODE_QUESTION: 'processCodeQuestion',

    // Extension commands
    OPEN_CHAT_VIEW: 'extension-v1.openChatView',
    START_ASSISTANT: 'extension-v1.startAssistant',
    SYNC_CODEBASE_COMMAND: 'extension-v1.syncCodebase',
    CHAT_VIEW_FOCUS: 'workbench.view.extension.repomind-chat-view',
    PROCESS_CODE_QUESTION_COMMAND: 'extension-v1.processCodeQuestion'
};

/**
 * Check if a message contains any of the keywords
 * @param message The message to check
 * @param keywords The keywords to check against
 * @returns True if the message contains any of the keywords
 */
export function containsKeyword(message: string, keywords: string[]): boolean {
    const lowerMessage = message.toLowerCase();
    return keywords.some(keyword => lowerMessage.includes(keyword.toLowerCase()));
}

/**
 * Natural language processing helper for command detection
 * Uses the NLP module for more accurate command detection
 * @param message The user message
 * @returns The detected command or null if no command is detected
 */
export function detectCommand(message: string): string | null {
    try {
        // Try to use the NLP module if available
        const nlp = require('./nlp');
        const intent = nlp.detectVisualizationIntent(message);

        if (intent) {
            return commands.VISUALIZE_RELATIONSHIPS;
        }
    } catch (error) {
        // Fallback to simple keyword matching if NLP module is not available
        console.log('NLP module not available, falling back to simple keyword matching');

        // Check for visualization commands
        if (containsKeyword(message, visualizationKeywords)) {
            return commands.VISUALIZE_RELATIONSHIPS;
        }
    }

    // Add more command detection logic here

    return null;
}
