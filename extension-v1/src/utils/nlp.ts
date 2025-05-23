/**
 * Natural Language Processing utilities for command detection
 *
 * This file contains utilities for detecting commands from natural language input.
 * It uses a simple approach that can be extended with more sophisticated NLP libraries in the future.
 */

import { visualizationKeywords, multiFileKeywords, relationshipTypesKeywords } from './commands';

/**
 * Preprocess text for better matching
 * @param text The text to preprocess
 * @returns The preprocessed text
 */
export function preprocessText(text: string): string {
    return text.toLowerCase().trim();
}

/**
 * Tokenize text into words
 * @param text The text to tokenize
 * @returns An array of tokens
 */
export function tokenizeText(text: string): string[] {
    return text.toLowerCase().split(/\s+/).filter(Boolean);
}

/**
 * Calculate the similarity between two texts
 * @param text1 First text
 * @param text2 Second text
 * @returns Similarity score between 0 and 1
 */
export function calculateSimilarity(text1: string, text2: string): number {
    const tokens1 = tokenizeText(preprocessText(text1));
    const tokens2 = tokenizeText(preprocessText(text2));

    // Use a simple word overlap measure
    let matches = 0;
    for (const token of tokens1) {
        if (tokens2.includes(token)) {
            matches++;
        }
    }

    // Return the proportion of matching words
    return matches / Math.max(tokens1.length, tokens2.length);
}

/**
 * Check if text contains any of the keywords
 * @param text The text to check
 * @param keywords The keywords to check against
 * @returns True if the text contains any of the keywords
 */
export function containsAnyKeyword(text: string, keywords: string[]): boolean {
    const processedText = preprocessText(text);
    return keywords.some(keyword => processedText.includes(preprocessText(keyword)));
}

/**
 * Detect visualization intent from text
 * @param text The text to analyze
 * @returns The type of visualization or null
 */
export function detectVisualizationIntent(text: string): 'general' | 'multiFile' | 'relationshipTypes' | null {
    // Check for multi-file keywords
    if (containsAnyKeyword(text, multiFileKeywords)) {
        return 'multiFile';
    }

    // Check for relationship types keywords
    if (containsAnyKeyword(text, relationshipTypesKeywords)) {
        return 'relationshipTypes';
    }

    // Check for general visualization keywords
    if (containsAnyKeyword(text, visualizationKeywords)) {
        return 'general';
    }

    return null;
}
