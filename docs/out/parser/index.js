"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseSourceCode = parseSourceCode;
const tree_sitter_1 = __importDefault(require("tree-sitter"));
const JavaScript = require("tree-sitter-javascript");
const traversals_1 = require("./traversals");
const parser = new tree_sitter_1.default();
parser.setLanguage(JavaScript);
function parseSourceCode(code) {
    const tree = parser.parse(code);
    const root = tree.rootNode;
    return (0, traversals_1.getAllFunctions)(root, code);
}
