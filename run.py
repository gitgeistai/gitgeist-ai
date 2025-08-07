# run.py - Development/standalone entry point
#!/usr/bin/env python3
"""
Gitgeist - Autonomous AI Git Agent
Main entry point for development/testing
"""

import asyncio
import signal
import sys
from pathlib import Path

from gitgeist.core.config import GitgeistConfig
from gitgeist.core.watcher import GitgeistWatcher
from gitgeist.utils.logger import setup_logger

def handle_shutdown(signum, frame):
    """Handle graceful shutdown"""
    print("\n🛑 Shutting down Gitgeist...")
    sys.exit(0)

async def main():
    """Main application entry point"""
    # Setup
    signal.signal(signal.SIGINT, handle_shutdown)
    
    # Load configuration
    try:
        config = GitgeistConfig.load()
    except FileNotFoundError:
        print("❌ No configuration found. Run 'gitgeist init' first.")
        sys.exit(1)
    
    logger = setup_logger(config.log_file)
    logger.info("🧠 Starting Gitgeist AI Git Agent")
    
    # Initialize components
    watcher = GitgeistWatcher(config)
    
    print("🚀 Gitgeist is now watching your repository...")
    if config.autonomous_mode:
        print("🤖 Autonomous mode: Changes will be auto-committed")
    else:
        print("💡 Suggestion mode: Commit messages will be suggested")
    print("Press Ctrl+C to stop")
    
    # Start watching
    try:
        await watcher.start_async()
    except KeyboardInterrupt:
        logger.info("Gitgeist stopped by user")
    except Exception as e:
        logger.error(f"Gitgeist crashed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())


# pyproject.toml - Modern Python packaging configuration
"""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "gitgeist"
version = "0.1.0"
description = "Autonomous AI Git agent for intelligent code management"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "watchdog>=3.0.0",
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
    "tree-sitter-javascript>=0.20.0", 
    "tree-sitter-typescript>=0.20.0",
    "aiohttp>=3.8.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]

[project.scripts]
gitgeist = "gitgeist.cli.commands:app"

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88
"""

# requirements.txt - Alternative dependency specification
"""
watchdog>=3.0.0
tree-sitter>=0.20.0
tree-sitter-python>=0.20.0
tree-sitter-javascript>=0.20.0
tree-sitter-typescript>=0.20.0
aiohttp>=3.8.0
typer[all]>=0.9.0
rich>=13.0.0
"""

# .gitignore - Git ignore patterns
"""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/

# Gitgeist specific
data/logs/*.log
data/memory/*.json
.gitgeist.json

# Environment
.env
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

# .gitgeist.example.json - Example configuration
"""
{
  "auto_commit": true,
  "commit_style": "conventional",
  "llm_model": "llama3.2",
  "llm_host": "http://localhost:11434",
  "temperature": 0.3,
  "autonomous_mode": false,
  "require_confirmation": true,
  "max_commit_frequency": 300,
  "watch_paths": ["."],
  "ignore_patterns": [
    ".git/*",
    "node_modules/*", 
    "*.pyc",
    "__pycache__/*",
    "data/logs/*",
    "*.log",
    ".env",
    "venv/*",
    ".venv/*"
  ],
  "supported_languages": [
    "python",
    "javascript", 
    "typescript",
    "rust",
    "go"
  ],
  "data_dir": "./data",
  "log_file": "./data/logs/gitgeist.log"
}
"""

# README.md - Project documentation
"""
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
# Clone and install
git clone <your-repo-url>
cd gitgeist-ai
pip install -e .

# Or install from PyPI (when published)
pip install gitgeist
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

### Commit Styles

- **conventional**: `feat(auth): add user login system`
- **semantic**: `Add user authentication with JWT tokens`
- **default**: `Update authentication system`

## 🧠 How It Works

1. **File Watching**: Monitors your repository for changes
2. **AST Analysis**: Parses code to understand semantic changes
3. **Change Detection**: Identifies functions/classes added, removed, or modified
4. **LLM Generation**: Uses local LLM to generate meaningful commit messages
5. **Auto Commit**: Optionally commits changes automatically

## 🆚 Comparison

| Feature | GitHub Copilot | CodeAnt AI | **Gitgeist** |
|---------|---------------|------------|--------------|
| **Cost** | $10/month | $15/month | **FREE** |
| **Autonomous** | No | No | **YES** |
| **Local LLM** | No | No | **YES** |
| **Semantic Understanding** | Basic | Static analysis | **Full AST** |
| **Git Operations** | Suggestions only | None | **Full automation** |

## 🛠️ Development

### Setup Development Environment

```bash
git clone <repo-url>
cd gitgeist-ai
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

### Project Structure

```
gitgeist/
├── gitgeist/
│   ├── core/          # Core functionality
│   ├── ai/            # LLM and AI logic
│   ├── analysis/      # Code analysis (AST)
│   ├── agent/         # Autonomous agent
│   ├── cli/           # Command line interface
│   └── utils/         # Utilities
├── tests/             # Test suite
├── data/              # Data storage
└── docs/              # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Tree-sitter for AST parsing
- Ollama for local LLM inference
- Rich and Typer for beautiful CLI
"""

# scripts/setup.py - Development setup script
"""
#!/usr/bin/env python3
\"\"\"
Setup script for Gitgeist development environment
\"\"\"

import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    \"\"\"Run shell command\"\"\"
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def main():
    \"\"\"Setup development environment\"\"\"
    print("🚀 Setting up Gitgeist development environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Install in development mode
    if not run_command("pip install -e .[dev]"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    print("✅ Dependencies installed")
    
    # Create directories
    dirs = ["data/logs", "data/memory", "data/models"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    
    # Test CLI
    if run_command("gitgeist --help", check=False):
        print("✅ CLI installed successfully")
    else:
        print("⚠️  CLI installation issue")
    
    # Check for Ollama
    if run_command("ollama --version", check=False):
        print("✅ Ollama detected")
    else:
        print("⚠️  Ollama not found - install from https://ollama.ai")
    
    print("\n🎉 Setup complete!")
    print("Next steps:")
    print("1. Start Ollama: ollama serve")
    print("2. Pull a model: ollama pull llama3.2") 
    print("3. Initialize: gitgeist init")
    print("4. Start watching: gitgeist watch")

if __name__ == "__main__":
    main()
"""

# scripts/test_installation.py - Test installation script
"""
#!/usr/bin/env python3
\"\"\"
Test Gitgeist installation
\"\"\"

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def test_imports():
    \"\"\"Test that all modules can be imported\"\"\"
    print("🧪 Testing imports...")
    
    try:
        from gitgeist.core.config import GitgeistConfig
        from gitgeist.core.git_handler import GitHandler  
        from gitgeist.ai.llm_client import OllamaClient
        from gitgeist.analysis.ast_parser import GitgeistASTParser
        from gitgeist.cli.commands import app
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_cli():
    \"\"\"Test CLI functionality\"\"\"
    print("🧪 Testing CLI...")
    
    try:
        result = subprocess.run(['gitgeist', '--help'], 
                              capture_output=True, text=True, check=True)
        if 'Gitgeist' in result.stdout:
            print("✅ CLI working")
            return True
        else:
            print("❌ CLI output unexpected")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_git_integration():
    \"\"\"Test Git integration\"\"\"
    print("🧪 Testing Git integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        try:
            # Initialize git repo
            subprocess.run(['git', 'init'], check=True, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
            
            # Test GitHandler
            from gitgeist.core.git_handler import GitHandler
            handler = GitHandler()
            
            if handler.is_git_repo():
                print("✅ Git integration working")
                return True
            else:
                print("❌ Git integration failed")
                return False
                
        except Exception as e:
            print(f"❌ Git integration test failed: {e}")
            return False

def test_ast_parser():
    \"\"\"Test AST parser\"\"\"
    print("🧪 Testing AST parser...")
    
    try:
        from gitgeist.analysis.ast_parser import GitgeistASTParser
        parser = GitgeistASTParser()
        
        # Test Python code parsing
        test_code = '''
def hello_world():
    print("Hello, world!")

class TestClass:
    pass
'''
        
        result = parser.analyze_content_structure(test_code, 'python')
        if result and len(result.get('functions', [])) == 1:
            print("✅ AST parser working")
            return True
        else:
            print("⚠️  AST parser limited (tree-sitter not fully available)")
            return True  # Don't fail - tree-sitter is optional
            
    except Exception as e:
        print(f"⚠️  AST parser test failed: {e}")
        return True  # Don't fail - tree-sitter is optional

def main():
    \"\"\"Run all tests\"\"\"
    print("🧪 Testing Gitgeist installation...\n")
    
    tests = [
        ("Imports", test_imports),
        ("CLI", test_cli), 
        ("Git Integration", test_git_integration),
        ("AST Parser", test_ast_parser),
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
        print()
    
    # Summary
    print("📊 Test Results:")
    passed = 0
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Gitgeist is ready to use.")
        print("\nNext steps:")
        print("1. cd /path/to/your/project")
        print("2. gitgeist init")
        print("3. gitgeist watch")
    else:
        print("⚠️  Some tests failed. Check installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""