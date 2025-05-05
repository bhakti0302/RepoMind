# RepoMind - VS Code Extension

RepoMind is a VS Code extension that provides an AI-powered coding assistant interface. This project is currently in development, with the basic UI and extension structure implemented.

## Features (Implemented)

- Basic chat interface with modern UI
- Status bar integration
- Command palette integration
- Welcome message with suggestions

## Prerequisites

- Node.js (v14 or later)
- VS Code (v1.80 or later)
- npm (v6 or later)
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repomind.git
cd repomind
```

2. Install project dependencies:
```bash
cd extension-v1
npm install
```

3. Compile the extension:
```bash
npm run compile
```

4. Run the extension in development mode:
   - Press F5 in VS Code, or
   - Use the Run and Debug view (Ctrl+Shift+D), or
   - Run `npm run start` in the terminal

This will open a new VS Code window with the extension loaded.

### Additional Setup (Optional)

If you plan to develop the extension further, you might want to install:

1. Global tools:
```bash
npm install -g yo generator-code typescript @vscode/vsce
```

2. VS Code extensions:
```bash
code --install-extension dbaeumer.vscode-eslint
code --install-extension amodio.tsl-problem-matcher
code --install-extension ms-vscode.extension-test-runner
```

## Development

The project is structured as follows:

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

## Testing

To run the tests:
```bash
npm test
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
