# Contributing to RepoMind

Thank you for your interest in contributing to RepoMind! This document provides guidelines and instructions for contributing to the project.

## Development Environment Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/repomind.git
cd repomind
```

2. Install dependencies:
```bash
cd extension-v1
npm install
```

3. Compile the extension:
```bash
npm run compile
```

4. Run the extension in development mode:
```bash
npm run start
```

## Project Structure

The project is currently focused on implementing the basic VS Code extension structure and UI components:

```
extension-v1/
├── src/
│   ├── extension.ts        # Main extension entry point
│   ├── ui/
│   │   ├── chatView.ts     # Chat interface implementation
│   │   └── statusBar.ts    # Status bar implementation
│   └── test/              # Test files
├── media/
│   └── styles.css         # UI styles
└── package.json           # Extension manifest
```

## Development Guidelines

1. **Code Style**:
   - Use TypeScript for all new code
   - Follow the existing code style and formatting
   - Use meaningful variable and function names
   - Add comments for complex logic

2. **Testing**:
   - Write tests for new functionality
   - Run tests before submitting changes:
     ```bash
     npm test
     ```

3. **Commits**:
   - Write clear, descriptive commit messages
   - Reference issues in commit messages when applicable
   - Keep commits focused and atomic

4. **Pull Requests**:
   - Create a new branch for each feature/fix
   - Keep PRs focused on a single feature or fix
   - Update documentation as needed
   - Ensure all tests pass

## Current Focus Areas

The project is currently implementing the basic extension structure (Epic 1 in the project plan):

- VS Code Extension Scaffolding (Story 1.1)
  - Basic activation function
  - Chat interface UI components
  - Status bar integration
  - Command palette integration

## Getting Help

If you need help or have questions:
1. Check the project documentation
2. Open an issue for discussion
3. Contact the maintainers

## License

By contributing to RepoMind, you agree that your contributions will be licensed under the project's MIT License.