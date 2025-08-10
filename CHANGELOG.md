# Changelog

All notable changes to Gitgeist will be documented in this file.

## [0.3.0] - 2024-01-15

### 🚀 Major Features Added

#### 🎨 Visual Identity & Branding
- **Official Logo**: Professional Gitgeist logo integrated across all platforms
- **README Enhancement**: Logo prominently displayed in main documentation
- **VS Code Extension**: Logo included for marketplace presentation
- **Web Dashboard**: Logo integrated in dashboard header for brand consistency

#### Multi-Repository Management
- **Workspace System**: Centralized management of multiple git repositories
- **Cross-Repository Operations**: Commit to all repositories simultaneously
- **Repository Status Tracking**: Monitor changes across all projects
- **Workspace CLI Commands**: `workspace add/remove/list/activate/status/commit-all`

#### GitHub Integration
- **Automated PR Creation**: Create pull requests directly from CLI
- **Issue Management**: List and interact with repository issues
- **Repository Detection**: Automatic GitHub repo detection from git remote
- **GitHub CLI Commands**: `github pr/issues/repo`

#### VS Code Extension
- **Native IDE Support**: Generate commit messages directly in VS Code
- **Git Panel Integration**: Seamless integration with VS Code's Git interface
- **Configurable Settings**: VS Code settings for Ollama host, model, commit style
- **Command Palette**: Access Gitgeist features through VS Code commands

#### Web Dashboard
- **Visual Insights**: Real-time system metrics and repository overview
- **Multi-Repository Monitoring**: Track status across all workspace repositories
- **FastAPI Backend**: Modern web API with automatic documentation
- **Live Updates**: 30-second refresh for real-time monitoring

### 🔧 Enhanced Core Features

#### RAG Memory System
- **Vector Embeddings**: Store commit history using sentence-transformers
- **Semantic Similarity**: Find similar past commits for better context
- **Automatic Learning**: Populate memory from existing git history
- **SQLite Storage**: Persistent vector database for commit patterns

#### Performance Optimization
- **Intelligent Caching**: Cache file analysis results for faster processing
- **Batch Processing**: Process multiple files in parallel
- **Performance Monitoring**: Track operation timing and bottlenecks
- **Memory Management**: Efficient handling of large codebases

#### Error Handling & Recovery
- **System Diagnostics**: Comprehensive `doctor` command for troubleshooting
- **Auto-Repair**: Automatic recovery from corrupted configurations
- **User-Friendly Errors**: Clear error messages with actionable suggestions
- **Backup & Restore**: Configuration backup and restoration system

#### Branch-Aware Intelligence
- **Branch Pattern Recognition**: Adapt commit styles based on branch names
- **Protected Branch Handling**: Extra confirmation for main/master branches
- **Commit Validation**: Ensure messages follow branch-specific conventions
- **Template System**: Context-aware commit message templates

### 🌐 Language & Integration Support

#### Extended Language Support
- **29+ Programming Languages**: Comprehensive language detection system
- **Enhanced AST Analysis**: Better semantic understanding across languages
- **File Categorization**: Classify files as code, docs, config, test, build
- **Language-Specific Templates**: Tailored commit messages per language

#### Integration Ecosystem
- **CLI Subcommands**: Organized command structure with `workspace`, `github`, `web`
- **Environment Variables**: Comprehensive configuration through env vars
- **Git Hooks Integration**: Examples for pre-commit and post-commit hooks
- **CI/CD Support**: GitHub Actions integration examples

### 🛠️ Developer Experience

#### Enhanced CLI
- **Rich Output**: Beautiful terminal output with colors and formatting
- **Progress Indicators**: Visual feedback for long-running operations
- **Interactive Confirmations**: Smart prompts for destructive operations
- **Help System**: Comprehensive help text and examples

#### Configuration Management
- **Workspace Configuration**: Separate config for multi-repo management
- **Validation System**: Comprehensive input validation with helpful errors
- **Migration Support**: Automatic config migration between versions
- **Default Handling**: Sensible defaults for all configuration options

### 📊 System Improvements

#### Architecture
- **Modular Design**: Clean separation of concerns across modules
- **Plugin Architecture**: Extensible system for future integrations
- **Type Safety**: Comprehensive type hints throughout codebase
- **Error Boundaries**: Isolated error handling per component

#### Testing & Quality
- **Comprehensive Testing**: Unit tests for all major components
- **Code Quality**: Black formatting, isort imports, mypy type checking
- **CI/CD Pipeline**: Automated testing and quality checks
- **Documentation**: Complete API documentation and usage guides

## [0.2.0] - 2024-01-10

### Added
- RAG memory system with vector embeddings
- Intelligent commit planning and analysis
- Performance optimization and caching
- Branch-aware commit strategies
- Enhanced error handling and recovery
- Comprehensive validation system

## [0.1.0] - 2024-01-05

### Added
- Initial release with basic commit generation
- Tree-sitter AST parsing for Python, JavaScript, TypeScript
- Ollama LLM integration
- File watching and change detection
- Conventional commit message generation
- Basic CLI interface

---

## Release Notes

### Installation

```bash
# Install latest version
pip install gitgeist

# Install with optional dependencies
pip install gitgeist[web,github,dev]

# Upgrade from previous version
pip install --upgrade gitgeist
```

### Migration Guide

#### From v0.2.x to v0.3.0

1. **Configuration**: Existing `.gitgeist.json` files are automatically compatible
2. **New Features**: Run `gitgeist doctor` to check system health
3. **Workspace**: Initialize workspace with `gitgeist workspace add .`
4. **GitHub**: Set `GITHUB_TOKEN` environment variable for GitHub features
5. **Web Dashboard**: Install web dependencies with `pip install gitgeist[web]`

#### Breaking Changes

- None. Version 0.3.0 is fully backward compatible with 0.2.x configurations.

### Known Issues

- VS Code extension requires manual installation (not yet in marketplace)
- Web dashboard requires additional dependencies (`fastapi`, `uvicorn`)
- GitHub integration requires personal access token

### Support

- **Documentation**: [Usage Guide](USAGE.md)
- **Issues**: [GitHub Issues](https://github.com/gitgeistai/gitgeist-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gitgeistai/gitgeist-ai/discussions)