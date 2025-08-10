# 🧠 Gitgeist - AI-Powered Git Management Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/gitgeistai/gitgeist-ai/releases)
[![GitHub](https://img.shields.io/badge/GitHub-Integration-blue.svg)](https://github.com/features)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension-purple.svg)](https://marketplace.visualstudio.com/vscode)

Gitgeist is a comprehensive AI-powered Git management platform that revolutionizes how developers interact with version control. Using local LLMs and advanced semantic analysis, it provides intelligent commit generation, multi-repository management, GitHub integration, and team collaboration tools.

## ✨ Features

### 🤖 AI-Powered Intelligence
- **Semantic Code Analysis**: 29+ programming languages with Tree-sitter AST parsing
- **RAG Memory System**: Learns from your commit history using vector embeddings
- **Branch-Aware Commits**: Adapts commit styles based on branch patterns
- **Smart Templates**: Context-aware commit message generation

### 🏢 Multi-Repository Management
- **Workspace Support**: Manage multiple repositories from a single interface
- **Cross-Repo Operations**: Commit to all repositories simultaneously
- **Repository Status Tracking**: Monitor changes across all projects
- **Team Collaboration**: Shared workspace configurations

### 🔗 Integrations & Extensions
- **GitHub Integration**: Automated PR creation and issue management
- **VS Code Extension**: Native IDE support for commit generation
- **Web Dashboard**: Visual insights and real-time monitoring
- **CLI Interface**: Comprehensive command-line tools

### 🔒 Privacy & Performance
- **100% Local Processing**: Uses local LLMs (Ollama) - no API costs
- **Privacy First**: No data sent to cloud services
- **Performance Optimization**: Intelligent caching and batch processing
- **Error Recovery**: Comprehensive error handling and system repair

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
git clone https://github.com/gitgeistai/gitgeist-ai.git
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

# Basic usage
gitgeist commit --dry-run    # Preview commit
gitgeist commit              # Interactive commit
gitgeist commit --auto       # Auto-commit

# Multi-repository workspace
gitgeist workspace add /path/to/repo
gitgeist workspace commit-all

# GitHub integration
export GITHUB_TOKEN=your_token
gitgeist github pr

# Web dashboard
gitgeist web start
# Access at http://localhost:8080 for visual insights
```

## 📖 Usage

### Core Commands

- `gitgeist init` - Initialize Gitgeist in repository
- `gitgeist commit` - Generate and create intelligent commits
- `gitgeist status` - Show comprehensive system status
- `gitgeist analyze` - Analyze current changes
- `gitgeist doctor` - Diagnose and fix system issues

### Multi-Repository Management

- `gitgeist workspace add <path>` - Add repository to workspace
- `gitgeist workspace list` - List all repositories
- `gitgeist workspace status` - Check status of all repos
- `gitgeist workspace commit-all` - Commit to all repositories

### GitHub Integration

- `gitgeist github pr` - Create pull request from current branch
- `gitgeist github issues` - List repository issues
- `gitgeist github repo` - Show repository information

### Web Dashboard

- `gitgeist web start` - Launch web dashboard
- Access at `http://localhost:8080` for visual insights

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

### 🔍 Semantic Analysis Pipeline
1. **Language Detection**: Identifies 29+ programming languages automatically
2. **AST Parsing**: Uses Tree-sitter for deep semantic code understanding
3. **Change Detection**: Identifies functions, classes, and structural modifications
4. **Context Building**: Aggregates changes across multiple files and languages

### 🧠 AI-Powered Generation
5. **RAG Memory**: Retrieves similar past commits using vector embeddings
6. **Template Selection**: Chooses appropriate commit style based on branch patterns
7. **LLM Generation**: Uses local Ollama with enhanced context for intelligent messages
8. **Validation**: Ensures commit messages follow project conventions

### 🚀 Multi-Repository Orchestration
9. **Workspace Management**: Coordinates operations across multiple repositories
10. **GitHub Integration**: Automates PR creation and issue management
11. **Performance Optimization**: Caches results and processes files in parallel
12. **Error Recovery**: Provides comprehensive diagnostics and auto-repair

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/gitgeistai/gitgeist-ai.git
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

## 🎆 What's New in v0.3.0

### ✅ Completed Features
- ✅ **RAG Memory System**: Vector embeddings for commit history learning
- ✅ **GitHub Integration**: Automated PR creation and issue management
- ✅ **VS Code Extension**: Native IDE support for commit generation
- ✅ **Multi-Repository Support**: Workspace management for multiple projects
- ✅ **Team Collaboration**: Shared configurations and cross-repo operations
- ✅ **Web Dashboard**: Visual insights and real-time monitoring
- ✅ **Performance Optimization**: Caching, batch processing, and parallel analysis
- ✅ **Error Handling**: Comprehensive diagnostics and auto-repair system
- ✅ **Branch Awareness**: Context-sensitive commit strategies
- ✅ **29+ Language Support**: Comprehensive programming language detection

### 🔮 Future Roadmap
- [ ] Advanced team analytics and insights
- [ ] Slack/Discord integration for team notifications
- [ ] Custom LLM model fine-tuning
- [ ] Advanced conflict resolution assistance
- [ ] Mobile app for repository monitoring
- [ ] Enterprise SSO and user management

---

**Made with ❤️ by developers, for developers**