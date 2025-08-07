# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-30

### Added
- Initial release of Gitgeist autonomous AI Git agent
- Local LLM integration with Ollama
- Semantic code analysis using Tree-sitter
- Support for Python, JavaScript, and TypeScript
- Conventional commit message generation
- Real-time file watching with change detection
- CLI interface with multiple commands:
  - `gitgeist init` - Initialize repository
  - `gitgeist watch` - Monitor file changes
  - `gitgeist commit` - Generate AI commits
  - `gitgeist status` - Show repository status
  - `gitgeist analyze` - Analyze code changes
  - `gitgeist config` - Manage configuration
  - `gitgeist version` - Show version info
- Configuration management with `.gitgeist.json`
- Comprehensive test suite
- Documentation and usage guides

### Features
- 🤖 Autonomous commit generation
- 🧠 Semantic understanding of code changes
- 💰 100% free with local LLMs
- 🔒 Privacy-first (no data sent to cloud)
- 📝 Smart conventional commit messages
- 👀 File system monitoring
- 🎯 Multi-language support

### Technical
- Python 3.8+ support
- Tree-sitter AST parsing
- Ollama LLM client
- Watchdog file monitoring
- Rich CLI interface
- Typer command framework
- Comprehensive logging
- Configuration validation