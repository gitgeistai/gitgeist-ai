# 🧠 Gitgeist - Autonomous AI Git Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
# Clone the repository
git clone https://github.com/your-username/gitgeist-ai.git
cd gitgeist-ai

# Install dependencies
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
- `gitgeist version` - Show version information

### Examples

```bash
# Initialize with autonomous mode
gitgeist init --autonomous --model llama3.2

# Watch repository (auto-commits changes)
gitgeist watch

# Generate commit message without committing
gitgeist commit --dry-run

# Commit with auto-approval
gitgeist commit --auto

# Show what Gitgeist detected
gitgeist analyze

# View current status
gitgeist status
```

## ⚙️ Configuration

Configuration is stored in `.gitgeist.json`:

```json
{
  "autonomous_mode": false,
  "commit_style": "conventional",
  "llm_model": "llama3.2",
  "llm_host": "http://localhost:11434",
  "temperature": 0.3,
  "log_level": "INFO",
  "watch_paths": ["."],
  "ignore_patterns": [
    ".git/*",
    "node_modules/*",
    "*.pyc",
    "__pycache__/*",
    ".env",
    "venv/*",
    ".venv/*"
  ]
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `autonomous_mode` | boolean | `false` | Enable automatic commits |
| `commit_style` | string | `"conventional"` | Commit message style (`conventional`, `semantic`, `default`) |
| `llm_model` | string | `"llama3.2"` | Ollama model to use |
| `llm_host` | string | `"http://localhost:11434"` | Ollama server URL |
| `temperature` | number | `0.3` | LLM temperature (0.0-2.0) |
| `log_level` | string | `"INFO"` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `watch_paths` | array | `["."]` | Directories to watch |
| `ignore_patterns` | array | See above | File patterns to ignore |

## 🧠 How It Works

1. **File Watching**: Monitors your repository for changes using Python's watchdog
2. **AST Analysis**: Parses code using Tree-sitter to understand semantic changes
3. **Change Detection**: Identifies functions/classes added, removed, or modified
4. **LLM Generation**: Uses local Ollama LLM to generate meaningful commit messages
5. **Auto Commit**: Optionally commits changes automatically in autonomous mode

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/your-username/gitgeist-ai.git
cd gitgeist-ai
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=gitgeist

# Format code
black .
isort .
```

### Project Structure

```
gitgeist-ai/
├── gitgeist/
│   ├── ai/                 # LLM integration
│   │   ├── llm_client.py   # Ollama client
│   │   ├── commit_generator.py
│   │   └── prompts.py      # LLM prompts
│   ├── analysis/           # Code analysis
│   │   └── ast_parser.py   # Tree-sitter integration
│   ├── cli/                # Command-line interface
│   │   └── commands.py     # CLI commands
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   ├── git_handler.py  # Git operations
│   │   ├── watcher.py      # File watching
│   │   └── schema.py       # Config validation
│   └── utils/              # Utilities
│       ├── logger.py       # Logging setup
│       └── exceptions.py   # Custom exceptions
├── tests/                  # Test suite
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Tree-sitter](https://tree-sitter.github.io/) for semantic code parsing
- [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

## 🔮 Roadmap

- [ ] RAG memory for better context understanding
- [ ] GitHub integration for PR/issue management
- [ ] VS Code extension
- [ ] Multi-repository support
- [ ] Team collaboration features
- [ ] Web dashboard for commit insights

---

**Made with ❤️ by developers, for developers**