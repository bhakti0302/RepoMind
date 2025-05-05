export interface ParsedFunction {
    name: string;
    startLine: number;
    endLine: number;
    code: string;
  }
  
  export interface CodeChunk {
    id: string;
    functions: ParsedFunction[];
    language: string;
    startLine: number;
    endLine: number;
    imports: string[];
    className?: string;  // Optional grouping
  }
  