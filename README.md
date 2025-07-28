# 🧠 Gitgeist - Autonomous AI Git Agent

Gitgeist is an intelligent, autonomous Git agent that uses local LLMs to understand your code changes semantically and generate meaningful commit messages automatically.

## ✨ Features

- **🤖 Autonomous Commits**: Automatically commits changes with intelligent messages
- **🧠 Semantic Understanding**: Uses AST parsing to understand what your code actually does
- **💰 100% Free**: Uses local LLMs (Ollama) - no API costs
- **🔒 Privacy First**: Everything runs locally, no data sent to cloud
- **📝 Smart Messages**: Generates conventional commit messages based on actual code changes
- **👀 File Watching**: Monitors your repository and commits changes automatically
- **🎯 Language Support**: Python, JavaScript, TypeScript, and more

## 🚀 Quick Start

### Prerequisites

1. **Git** repository
2. **Python 3.8+**
3. **Ollama** with a model (e.g., llama3.2)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2

# Start Ollama server
ollama serve
```

### Installation

```bash
# Install from this directory
pip install -e .

# Or install development version
pip install -e ".[dev]"
```

### Setup

```bash
# Initialize in your repository
cd /path/to/your/project
gitgeist init --autonomous --model llama3.2

# Start watching (autonomous mode)
gitgeist watch

# Or generate single commit
gitgeist commit
```

## 📖 Usage

### Commands

- `gitgeist init` - Initialize Gitgeist in current repository
- `gitgeist watch` - Start watching for changes
- `gitgeist commit` - Generate and create a commit
- `gitgeist status` - Show repository and Gitgeist status
- `gitgeist analyze` - Analyze current changes
- `gitgeist config` - Manage configuration

### Examples

```bash
# Initialize with autonomous mode
gitgeist init --autonomous --model llama3.2

# Watch repository (auto-commits changes)
gitgeist watch

# Generate commit message without committing
gitgeist commit --dry-run

# Commit with custom message
gitgeist commit -m "feat: add user authentication"

# Show what Gitgeist detected
gitgeist analyze
```

## ⚙️ Configuration

Configuration is stored in `.gitgeist.json`:

```json
{
  "autonomous_mode": false,
  "commit_style": "conventional",
  "llm_model": "llama3.2",
  "llm_host": "http://localhost:11434",
  "temperature": 0.3
}
```

## 🧠 How It Works

1. **File Watching**: Monitors your repository for changes
2. **AST Analysis**: Parses code to understand semantic changes
3. **Change Detection**: Identifies functions/classes added, removed, or modified
4. **LLM Generation**: Uses local LLM to generate meaningful commit messages
5. **Auto Commit**: Optionally commits changes automatically

## 🛠️ Development

### Setup Development Environment

```bash
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

## 📄 License

MIT License - see LICENSE file for details.
