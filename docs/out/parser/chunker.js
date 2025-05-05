"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.chunkFunctions = chunkFunctions;
const uuid_1 = require("uuid");
function chunkFunctions(functions, imports, maxLines = 300) {
    const chunks = [];
    let current = [];
    let totalLines = 0;
    for (const fn of functions) {
        const lines = fn.endLine - fn.startLine + 1;
        if (totalLines + lines > maxLines && current.length > 0) {
            chunks.push({
                id: (0, uuid_1.v4)(),
                language: 'javascript',
                startLine: current[0].startLine,
                endLine: current[current.length - 1].endLine,
                functions: current,
                imports,
            });
            current = [];
            totalLines = 0;
        }
        current.push(fn);
        totalLines += lines;
    }
    if (current.length > 0) {
        chunks.push({
            id: (0, uuid_1.v4)(),
            language: 'javascript',
            startLine: current[0].startLine,
            endLine: current[current.length - 1].endLine,
            functions: current,
            imports,
        });
    }
    return chunks;
}
