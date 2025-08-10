# 🧠 Gitgeist VS Code Extension

AI-powered Git commit generation directly in VS Code using local LLMs.

## Features

- **🤖 AI Commit Generation**: Generate intelligent commit messages using semantic code analysis
- **⚡ Quick Commit**: One-click commit with auto-generated messages
- **🔍 Change Analysis**: Analyze repository changes with detailed insights
- **🔒 Privacy First**: Uses local Ollama LLMs - no data sent to cloud
- **🎯 Smart Integration**: Works seamlessly with VS Code's Git interface

## Requirements

1. **Gitgeist CLI** installed: `pip install gitgeist`
2. **Ollama** running with a model (e.g., `ollama pull llama3.2`)
3. **Git repository** initialized in your workspace

## Quick Start

1. Install the extension
2. Open a Git repository in VS Code
3. Make some changes to your code
4. Use `Ctrl+Shift+P` → "Gitgeist: Generate AI Commit Message"
5. Review and commit!

## Commands

- **Generate AI Commit Message** - Analyze changes and generate commit message
- **Quick AI Commit** - Generate and commit automatically
- **Analyze Changes** - View detailed repository analysis
- **Open Settings** - Configure Gitgeist preferences

## Configuration

Access settings via `File > Preferences > Settings` and search for "Gitgeist":

- `gitgeist.ollamaHost`: Ollama server URL (default: `http://localhost:11434`)
- `gitgeist.model`: LLM model to use (default: `llama3.2`)
- `gitgeist.commitStyle`: Commit message style (`conventional`, `semantic`, `default`)
- `gitgeist.autoAnalyze`: Auto-analyze changes on file save

## Usage

### Generate Commit Message
1. Make changes to your code
2. Click the robot icon (🤖) in the Source Control panel
3. Review the generated message
4. Choose to commit, copy, or edit

### Quick Commit
1. Click the lightning icon (⚡) for instant AI commit
2. No confirmation needed - commits immediately

### Analyze Changes
1. Use Command Palette: "Gitgeist: Analyze Changes"
2. View detailed analysis in the output panel

## Installation Requirements

Before using the extension, ensure you have:

```bash
# Install Gitgeist CLI
pip install gitgeist

# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
ollama serve

# Initialize in your repository
cd your-project
gitgeist init --model llama3.2
```

## Troubleshooting

**"Gitgeist not found"**
- Install the CLI: `pip install gitgeist`
- Ensure it's in your PATH

**"No configuration found"**
- Run `gitgeist init` in your repository
- Check that `.gitgeist.json` exists

**"Ollama not responding"**
- Start Ollama: `ollama serve`
- Check the host URL in settings

## Features in Detail

### Semantic Code Analysis
- Supports 29+ programming languages
- Understands functions, classes, and structural changes
- Generates contextually appropriate commit messages

### Branch Awareness
- Adapts commit style based on branch type
- Respects protected branch rules
- Suggests appropriate commit formats

### Memory System
- Learns from your commit history
- Suggests similar past commits
- Improves over time

## Privacy & Security

- **100% Local Processing**: All analysis happens on your machine
- **No Cloud Dependencies**: Uses local Ollama LLMs only
- **No Data Collection**: Your code never leaves your computer
- **Open Source**: Full transparency in how it works

## Support

- **Documentation**: [GitHub Repository](https://github.com/gitgeistai/gitgeist-ai)
- **Issues**: [Report bugs](https://github.com/gitgeistai/gitgeist-ai/issues)
- **Discussions**: [Community support](https://github.com/gitgeistai/gitgeist-ai/discussions)

## License

MIT License - see [LICENSE](https://github.com/gitgeistai/gitgeist-ai/blob/main/LICENSE)

---

**Made with ❤️ for developers who love intelligent Git workflows**