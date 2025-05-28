/**
 * Enhanced Chat Assistant with caching, better context awareness, and improved error handling
 */

import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Cache interface
interface CacheEntry {
    question: string;
    response: string;
    timestamp: number;
    context_hash: string;
}

// Progress callback interface
interface ProgressCallback {
    (stage: string, progress: number, message: string): void;
}

// Enhanced conversation history
interface ConversationEntry {
    user: string;
    assistant: string;
    timestamp: number;
    context_used: string[];
    response_time: number;
}

class EnhancedChatAssistant {
    private cache: Map<string, CacheEntry> = new Map();
    private conversationHistory: ConversationEntry[] = [];
    private cacheFile: string;
    private historyFile: string;
    private maxCacheSize = 100;
    private maxHistorySize = 50;
    private cacheExpiryHours = 24;

    constructor() {
        const dataDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/data';
        this.cacheFile = path.join(dataDir, 'chat_cache.json');
        this.historyFile = path.join(dataDir, 'chat_history.json');

        // Ensure data directory exists
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }

        this.loadCache();
        this.loadHistory();
    }

    /**
     * Process a code question with enhanced features
     */
    async processCodeQuestionEnhanced(
        question: string,
        progressCallback?: ProgressCallback
    ): Promise<string> {
        const startTime = Date.now();

        try {
            // Stage 1: Check cache
            if (progressCallback) {
                progressCallback('Checking cache', 10, 'Looking for cached responses...');
            }

            const cachedResponse = this.getCachedResponse(question);
            if (cachedResponse) {
                if (progressCallback) {
                    progressCallback('Cache hit', 100, 'Found cached response');
                }
                return `${cachedResponse}\n\n*Note: This response was retrieved from cache.*`;
            }

            // Stage 2: Analyze question context
            if (progressCallback) {
                progressCallback('Analyzing context', 20, 'Understanding your question...');
            }

            const contextAnalysis = this.analyzeQuestionContext(question);

            // Stage 3: Prepare enhanced prompt with conversation history
            if (progressCallback) {
                progressCallback('Preparing context', 30, 'Gathering relevant context...');
            }

            const enhancedPrompt = this.buildEnhancedPrompt(question, contextAnalysis);

            // Stage 4: Execute the code chat script
            if (progressCallback) {
                progressCallback('Processing with LLM', 50, 'Analyzing codebase and generating response...');
            }

            const response = await this.executeCodeChat(question, enhancedPrompt, progressCallback);

            // Stage 5: Post-process and cache
            if (progressCallback) {
                progressCallback('Finalizing', 90, 'Processing response...');
            }

            const processedResponse = this.postProcessResponse(response, contextAnalysis);

            // Cache the response
            this.cacheResponse(question, processedResponse, contextAnalysis.hash);

            // Add to conversation history
            const responseTime = Date.now() - startTime;
            this.addToHistory(question, processedResponse, contextAnalysis.contextUsed, responseTime);

            if (progressCallback) {
                progressCallback('Complete', 100, 'Response ready');
            }

            return processedResponse;

        } catch (error) {
            console.error('Error in enhanced code question processing:', error);

            if (progressCallback) {
                progressCallback('Error', 0, 'Processing failed, generating fallback response...');
            }

            return this.generateEnhancedFallbackResponse(question, error as Error);
        }
    }

    /**
     * Get cached response if available and not expired
     */
    private getCachedResponse(question: string): string | null {
        const questionHash = this.hashString(question.toLowerCase().trim());
        const cached = this.cache.get(questionHash);

        if (!cached) {
            return null;
        }

        // Check if cache entry is expired
        const hoursOld = (Date.now() - cached.timestamp) / (1000 * 60 * 60);
        if (hoursOld > this.cacheExpiryHours) {
            this.cache.delete(questionHash);
            this.saveCache();
            return null;
        }

        return cached.response;
    }

    /**
     * Analyze question context to provide better responses
     */
    private analyzeQuestionContext(question: string): {
        type: string;
        keywords: string[];
        contextUsed: string[];
        hash: string;
    } {
        const lowerQuestion = question.toLowerCase();
        let type = 'general';
        const keywords: string[] = [];
        const contextUsed: string[] = [];

        // Determine question type
        if (lowerQuestion.includes('error') || lowerQuestion.includes('bug') || lowerQuestion.includes('fix')) {
            type = 'debugging';
            keywords.push('error', 'debugging', 'troubleshooting');
        } else if (lowerQuestion.includes('implement') || lowerQuestion.includes('create') || lowerQuestion.includes('add')) {
            type = 'implementation';
            keywords.push('implementation', 'development', 'coding');
        } else if (lowerQuestion.includes('explain') || lowerQuestion.includes('how') || lowerQuestion.includes('what')) {
            type = 'explanation';
            keywords.push('explanation', 'documentation', 'understanding');
        } else if (lowerQuestion.includes('optimize') || lowerQuestion.includes('improve') || lowerQuestion.includes('performance')) {
            type = 'optimization';
            keywords.push('optimization', 'performance', 'improvement');
        }

        // Extract technical keywords
        const techKeywords = ['java', 'python', 'javascript', 'class', 'method', 'function', 'api', 'database', 'sql'];
        techKeywords.forEach(keyword => {
            if (lowerQuestion.includes(keyword)) {
                keywords.push(keyword);
            }
        });

        // Add conversation context
        if (this.conversationHistory.length > 0) {
            contextUsed.push('conversation_history');
        }

        const hash = this.hashString(question + type + keywords.join(','));

        return { type, keywords, contextUsed, hash };
    }

    /**
     * Build enhanced prompt with context
     */
    private buildEnhancedPrompt(question: string, context: any): string {
        let enhancedPrompt = question;

        // Add conversation context if available
        if (this.conversationHistory.length > 0) {
            const recentHistory = this.conversationHistory.slice(-3); // Last 3 exchanges
            enhancedPrompt += '\n\nRecent conversation context:\n';
            recentHistory.forEach((entry, index) => {
                enhancedPrompt += `${index + 1}. User: ${entry.user.substring(0, 100)}...\n`;
                enhancedPrompt += `   Assistant: ${entry.assistant.substring(0, 100)}...\n`;
            });
        }

        // Add question type context
        enhancedPrompt += `\n\nQuestion type: ${context.type}`;
        if (context.keywords.length > 0) {
            enhancedPrompt += `\nRelevant keywords: ${context.keywords.join(', ')}`;
        }

        return enhancedPrompt;
    }

    /**
     * Execute the code chat script with progress updates
     */
    private async executeCodeChat(
        _question: string,
        _enhancedPrompt: string,
        progressCallback?: ProgressCallback
    ): Promise<string> {
        const scriptPath = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis/run_code_chat.sh';

        if (!fs.existsSync(scriptPath)) {
            throw new Error(`Script not found at ${scriptPath}`);
        }

        // Create history file for this session
        const historyFile = `/tmp/chat_history_${Date.now()}.json`;
        if (this.conversationHistory.length > 0) {
            fs.writeFileSync(historyFile, JSON.stringify(this.conversationHistory.slice(-5), null, 2));
        }

        const command = `"${scriptPath}" "${_question}"${this.conversationHistory.length > 0 ? ` --history-file "${historyFile}"` : ''}`;

        if (progressCallback) {
            progressCallback('Executing', 60, 'Running analysis...');
        }

        const { stdout, stderr } = await execAsync(command);

        if (stderr) {
            console.warn(`Code chat stderr: ${stderr}`);
        }

        // Clean up temporary history file
        if (fs.existsSync(historyFile)) {
            fs.unlinkSync(historyFile);
        }

        // Read response from output file
        const outputDir = '/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output';
        const responseFile = path.join(outputDir, 'chat-response.txt');

        if (fs.existsSync(responseFile)) {
            return fs.readFileSync(responseFile, 'utf8');
        } else {
            return stdout || 'No response received from the LLM.';
        }
    }

    /**
     * Post-process the response for better formatting
     */
    private postProcessResponse(response: string, context: any): string {
        let processed = response.trim();

        // Add response metadata
        const metadata = `\n\n---\n*Response generated at ${new Date().toLocaleString()}*`;
        if (context.keywords.length > 0) {
            processed += `\n*Keywords: ${context.keywords.join(', ')}*`;
        }
        processed += metadata;

        return processed;
    }

    /**
     * Generate enhanced fallback response with context
     */
    private generateEnhancedFallbackResponse(_question: string, error: Error): string {
        const context = this.analyzeQuestionContext(_question);

        let fallback = `I apologize, but I encountered an issue while processing your ${context.type} question.\n\n`;

        // Provide context-specific guidance
        switch (context.type) {
            case 'debugging':
                fallback += `For debugging questions, you might want to:\n`;
                fallback += `- Check the error logs in the logs directory\n`;
                fallback += `- Review recent code changes\n`;
                fallback += `- Verify configuration settings\n`;
                break;
            case 'implementation':
                fallback += `For implementation questions, consider:\n`;
                fallback += `- Reviewing existing code patterns\n`;
                fallback += `- Checking the project documentation\n`;
                fallback += `- Looking at similar implementations in the codebase\n`;
                break;
            case 'explanation':
                fallback += `For explanation requests, you can:\n`;
                fallback += `- Browse the codebase using the visualization features\n`;
                fallback += `- Check the project documentation\n`;
                fallback += `- Review the code structure and comments\n`;
                break;
            default:
                fallback += `Here are some general suggestions:\n`;
                fallback += `- Try rephrasing your question\n`;
                fallback += `- Check if the LLM API key is configured\n`;
                fallback += `- Review the system logs for more details\n`;
        }

        fallback += `\n**Error details:** ${error.message}\n`;
        fallback += `\n*Please try again or contact support if the issue persists.*`;

        return fallback;
    }

    // Utility methods for caching and history management
    private hashString(str: string): string {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString();
    }

    private cacheResponse(question: string, response: string, contextHash: string): void {
        const questionHash = this.hashString(question.toLowerCase().trim());

        // Remove oldest entries if cache is full
        if (this.cache.size >= this.maxCacheSize) {
            const oldestKey = this.cache.keys().next().value;
            if (oldestKey !== undefined) {
                this.cache.delete(oldestKey);
            }
        }

        this.cache.set(questionHash, {
            question,
            response,
            timestamp: Date.now(),
            context_hash: contextHash
        });

        this.saveCache();
    }

    private addToHistory(question: string, response: string, contextUsed: string[], responseTime: number): void {
        // Remove oldest entries if history is full
        if (this.conversationHistory.length >= this.maxHistorySize) {
            this.conversationHistory.shift();
        }

        this.conversationHistory.push({
            user: question,
            assistant: response,
            timestamp: Date.now(),
            context_used: contextUsed,
            response_time: responseTime
        });

        this.saveHistory();
    }

    private loadCache(): void {
        try {
            if (fs.existsSync(this.cacheFile)) {
                const data = JSON.parse(fs.readFileSync(this.cacheFile, 'utf8'));
                this.cache = new Map(Object.entries(data));
            }
        } catch (error) {
            console.warn('Failed to load cache:', error);
        }
    }

    private saveCache(): void {
        try {
            const data = Object.fromEntries(this.cache);
            fs.writeFileSync(this.cacheFile, JSON.stringify(data, null, 2));
        } catch (error) {
            console.warn('Failed to save cache:', error);
        }
    }

    private loadHistory(): void {
        try {
            if (fs.existsSync(this.historyFile)) {
                this.conversationHistory = JSON.parse(fs.readFileSync(this.historyFile, 'utf8'));
            }
        } catch (error) {
            console.warn('Failed to load history:', error);
        }
    }

    private saveHistory(): void {
        try {
            fs.writeFileSync(this.historyFile, JSON.stringify(this.conversationHistory, null, 2));
        } catch (error) {
            console.warn('Failed to save history:', error);
        }
    }

    /**
     * Clear cache and history (for maintenance)
     */
    clearCache(): void {
        this.cache.clear();
        this.conversationHistory = [];
        this.saveCache();
        this.saveHistory();
    }

    /**
     * Get cache statistics
     */
    getCacheStats(): { size: number; hitRate: number; oldestEntry: number } {
        const now = Date.now();
        let oldestTimestamp = now;

        for (const entry of this.cache.values()) {
            if (entry.timestamp < oldestTimestamp) {
                oldestTimestamp = entry.timestamp;
            }
        }

        return {
            size: this.cache.size,
            hitRate: 0, // Would need to track hits vs misses
            oldestEntry: Math.floor((now - oldestTimestamp) / (1000 * 60 * 60)) // hours
        };
    }
}

// Export singleton instance
export const enhancedChatAssistant = new EnhancedChatAssistant();

// Export the class for testing
export { EnhancedChatAssistant };
