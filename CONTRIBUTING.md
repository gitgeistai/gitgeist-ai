# Contributing to Gitgeist

Thank you for your interest in contributing to Gitgeist! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/gitgeistai/gitgeist-ai.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate it: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
5. Install in development mode: `pip install -e ".[dev]"`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `black . && isort .`
5. Commit your changes: `git commit -m "feat: add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Create a Pull Request

## Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages
- Add type hints where possible

## Testing

- Write tests for new functionality
- Ensure all tests pass: `pytest`
- Aim for good test coverage: `pytest --cov=gitgeist`

## Areas for Contribution

### 🐛 Bug Fixes
- Check [open issues](https://github.com/gitgeistai/gitgeist-ai/issues) labeled `bug`
- Reproduce the issue and create a fix
- Add tests to prevent regression

### ✨ New Features
- RAG memory integration
- Additional language support (Rust, Go, Java)
- GitHub integration
- VS Code extension
- Web dashboard

### 📚 Documentation
- Improve README
- Add more usage examples
- Create video tutorials
- API documentation

### 🧪 Testing
- Increase test coverage
- Add integration tests
- Performance testing

## Questions?

- Open an [issue](https://github.com/gitgeistai/gitgeist-ai/issues) for questions
- Join discussions in the repository
- Check existing documentation

## Code of Conduct

Be respectful and inclusive. We're all here to build something awesome together! 🚀