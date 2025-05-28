# RepoMind - Intelligent Coding Assistant

RepoMind is an AI-powered VS Code extension that provides intelligent code analysis, understanding, and generation capabilities. It combines advanced codebase analysis with natural language processing to help developers understand existing code and generate new implementations based on business requirements.

## 🚀 Overview

RepoMind transforms how developers interact with codebases by providing:

- **Intelligent Code Analysis**: Deep understanding of code structure, dependencies, and relationships
- **Natural Language Processing**: Convert business requirements into actionable code implementations
- **Context-Aware Code Generation**: Generate code that fits seamlessly into existing codebases
- **Interactive Chat Interface**: VS Code integrated chat for seamless developer experience
- **Multi-Language Support**: Support for Java, Python, JavaScript, and more

## 🏗️ Architecture

RepoMind consists of four main components that work together to provide a comprehensive coding assistant experience:

### 1. VS Code Extension (`extension-v1/`)
The user interface and main interaction point:
- **Chat Interface**: Interactive chat window for natural language queries
- **File Upload**: Attach business requirement files for analysis
- **Code Visualization**: Display generated code and analysis results
- **Real-time Processing**: Live updates during analysis and generation
- **Integration Hub**: Orchestrates communication between all components

### 2. Codebase Analyzer (`codebase-analyser/`)
Advanced code analysis and indexing system:
- **Multi-Language Parsing**: Tree-sitter based parsing for multiple programming languages
- **Semantic Chunking**: Intelligent code segmentation preserving context and structure
- **Vector Embeddings**: Generate embeddings using CodeBERT for semantic similarity
- **Dependency Analysis**: Build comprehensive dependency graphs and relationships
- **LanceDB Storage**: Efficient vector database for code chunk storage and retrieval

### 3. NLP Analysis Pipeline (`codebase-analyser/nlp-analysis/`)
Natural language processing and code synthesis:
- **Requirements Parsing**: Extract entities and components from business requirements
- **Vector Search**: Find relevant code chunks using semantic similarity
- **Multi-Hop RAG**: Retrieval-Augmented Generation with graph traversal
- **Context Building**: Combine multiple code contexts for comprehensive understanding
- **LLM Integration**: NVIDIA Llama 3.3 Nemotron for code generation

### 4. Merge Code Agent (`mergeCodeAgent/`)
Automated code modification and integration:
- **Instruction Parsing**: Understand natural language modification instructions
- **Code Integration**: Apply generated code to existing codebases
- **Duplicate Detection**: Prevent redundant code additions
- **User Approval**: Interactive approval process for code changes
- **Automatic Formatting**: Ensure proper code formatting and organization

## 🔄 Workflow

RepoMind follows a comprehensive workflow from code analysis to generation:

### Phase 1: Codebase Indexing
1. **Code Parsing**: Analyze repository structure using Tree-sitter
2. **Semantic Chunking**: Break code into meaningful, context-preserving chunks
3. **Embedding Generation**: Create vector embeddings for semantic search
4. **Dependency Mapping**: Build relationships between code components
5. **Database Storage**: Store in LanceDB for efficient retrieval

### Phase 2: Requirement Analysis
1. **File Upload**: User uploads business requirements via VS Code extension
2. **NLP Processing**: Extract entities, components, and relationships
3. **Query Generation**: Create search queries from requirements
4. **Vector Search**: Find relevant code chunks using semantic similarity
5. **Context Retrieval**: Use multi-hop RAG for comprehensive context gathering

### Phase 3: Code Generation
1. **Context Assembly**: Combine retrieved code contexts with requirements
2. **LLM Processing**: Generate code using NVIDIA Llama 3.3 Nemotron
3. **Output Formatting**: Structure generated code for integration
4. **Result Display**: Show results in VS Code chat interface

### Phase 4: Code Integration (Optional)
1. **Instruction Processing**: Parse generated code modification instructions
2. **User Approval**: Interactive approval for each code change
3. **Code Application**: Apply changes to target codebase
4. **Formatting**: Ensure proper code organization and style

## 🛠️ Technologies

### Core Technologies
- **TypeScript/JavaScript**: VS Code extension development
- **Python**: Backend processing and analysis
- **Tree-sitter**: Multi-language code parsing
- **LanceDB**: Vector database for embeddings storage
- **spaCy**: Natural language processing
- **CodeBERT**: Code embedding generation

### AI/ML Stack
- **NVIDIA Llama 3.3 Nemotron**: Large language model for code generation
- **OpenRouter API**: LLM access and management
- **RAG (Retrieval-Augmented Generation)**: Context-aware generation
- **Vector Similarity Search**: Semantic code matching

### Development Tools
- **LangGraph**: Agentic AI workflow orchestration
- **NetworkX**: Graph analysis and traversal
- **Transformers**: Hugging Face model integration
- **VS Code API**: Extension development framework

## 📁 Project Structure

```
RepoMind/
├── extension-v1/                 # VS Code Extension
│   ├── src/                     # Extension source code
│   ├── media/                   # UI assets and webviews
│   └── package.json             # Extension manifest
├── codebase-analyser/           # Code Analysis System
│   ├── codebase_analyser/       # Core analysis modules
│   ├── nlp-analysis/            # NLP processing pipeline
│   ├── scripts/                 # Analysis scripts
│   └── tests/                   # Test suites
├── mergeCodeAgent/              # Code Integration Agent
│   ├── src/                     # Agent source code
│   └── examples/                # Usage examples
├── test-project-employee/       # Sample test project
├── docs/                        # Documentation
└── Requirements/                # Uploaded requirement files
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **VS Code** (latest version)
- **Git**

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/RepoMind.git
cd RepoMind
```

2. **Setup VS Code Extension**
```bash
cd extension-v1
npm install
npm run compile
```

3. **Setup Codebase Analyzer**
```bash
cd codebase-analyser
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Setup NLP Analysis Pipeline**
```bash
cd codebase-analyser/nlp-analysis
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

5. **Setup Merge Code Agent**
```bash
cd mergeCodeAgent
pip install -r requirements.txt
```

### Configuration

1. **Create Environment Files**

Create `.env` in `codebase-analyser/nlp-analysis/`:
```env
LLM_API_KEY=your_nvidia_api_key_here
LLM_MODEL_NAME=nvidia/llama-3.3-nemotron-super-49b-v1:free
OUTPUT_DIR=output
```

Create `.env` in `mergeCodeAgent/`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

2. **Install VS Code Extension**
```bash
cd extension-v1
code --install-extension .
```

## 🧪 Testing

### Test the Complete System

1. **Start VS Code** with the extension installed
2. **Open a project** you want to analyze
3. **Sync Codebase**: Click the "Sync Codebase" button to index your code
4. **Upload Requirements**: Use the attach button to upload a requirements file
5. **Review Results**: Generated code will appear in the chat interface

### Test Individual Components

**Codebase Analysis:**
```bash
cd codebase-analyser
python scripts/run_codebase_analysis.py --repo-path ../test-project-employee --clear-db --mock-embeddings
```

**NLP Pipeline:**
```bash
cd codebase-analyser/nlp-analysis
python src/code_synthesis_workflow.py --input-file data/test/test_requirements.txt --output-dir output
```

**Merge Agent:**
```bash
cd mergeCodeAgent
python run_agent.py examples/test_instructions.txt ../test-project-employee
```

## 📖 Documentation

- **[Project Plan](docs/PLAN.MD)**: Detailed project roadmap and features
- **[Codebase Analyzer Guide](docs/README.md)**: Complete analysis system documentation
- **[NLP Pipeline Guide](codebase-analyser/nlp-analysis/README.md)**: NLP processing documentation
- **[Extension Guide](extension-v1/README.md)**: VS Code extension documentation
- **[Merge Agent Guide](mergeCodeAgent/README.md)**: Code integration documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tree-sitter** for multi-language parsing capabilities
- **NVIDIA** for Llama 3.3 Nemotron model access
- **Hugging Face** for CodeBERT and transformer models
- **LanceDB** for efficient vector storage
- **VS Code** for the excellent extension API
