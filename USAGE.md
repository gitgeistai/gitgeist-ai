# 📖 Gitgeist Usage Guide

## Getting Started

### 1. First-time Setup

```bash
# Make sure Ollama is running
ollama serve

# Navigate to your project
cd /path/to/your/project

# Initialize Gitgeist
gitgeist init --autonomous --model llama3.2
```

### 2. Basic Workflow

```bash
# Option 1: Watch mode (monitors files automatically)
gitgeist watch

# Option 2: Manual commits
gitgeist commit

# Option 3: Preview without committing
gitgeist commit --dry-run
```

## Command Reference

### `gitgeist init`

Initialize Gitgeist in your repository.

```bash
# Basic initialization
gitgeist init

# With autonomous mode
gitgeist init --autonomous

# With specific model
gitgeist init --model llama3.2

# With custom commit style
gitgeist init --style semantic
```

**Options:**
- `--autonomous` / `-a`: Enable autonomous commits
- `--model` / `-m`: Specify LLM model (default: llama3.2)
- `--host`: Ollama host URL (default: http://localhost:11434)
- `--style` / `-s`: Commit style (conventional/semantic/default)

### `gitgeist watch`

Monitor repository for changes and log semantic analysis.

```bash
gitgeist watch
```

**Note:** In current version, autonomous commits are disabled in watch mode for stability. Use `gitgeist commit` for actual commits.

### `gitgeist commit`

Generate and create intelligent commits.

```bash
# Interactive commit (asks for confirmation)
gitgeist commit

# Auto-commit without confirmation
gitgeist commit --auto

# Preview commit message only
gitgeist commit --dry-run

# Custom commit message
gitgeist commit -m "feat: add new feature"
```

**Options:**
- `--auto`: Automatically commit without confirmation
- `--dry-run`: Show analysis and generated message without committing
- `--message` / `-m`: Use custom commit message

### `gitgeist status`

Show repository and Gitgeist status.

```bash
gitgeist status
```

Shows:
- Configuration status
- Git repository status
- Ollama connection status
- Model availability
- Recent commits

### `gitgeist analyze`

Analyze current repository changes without committing.

```bash
gitgeist analyze
```

Shows:
- Files changed
- Semantic analysis (functions/classes added/removed)
- Languages detected
- Change statistics

### `gitgeist config` 

Manage configuration.

```bash
# Show current configuration
gitgeist config --show

# Edit configuration file
gitgeist config --edit

# Reset to defaults
gitgeist config --reset
```

### `gitgeist version`

Show version and system information.

```bash
gitgeist version
```

## Configuration

### Configuration File (`.gitgeist.json`)

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
  ],
  "supported_languages": ["python", "javascript", "typescript"],
  "require_confirmation": true,
  "max_commit_frequency": 300
}
```

### Environment Variables

You can also configure Gitgeist using environment variables:

```bash
export GITGEIST_AUTO_COMMIT=true
export GITGEIST_LLM_MODEL=llama3.2
export GITGEIST_AUTONOMOUS=false
```

## Commit Styles

### Conventional Commits (default)

Generates commits following the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat(auth): add user login functionality
fix(api): resolve null pointer exception
refactor(database): extract connection pooling
docs(readme): update installation instructions
```

### Semantic Commits

Focuses on functional impact:

```
Add user authentication with JWT tokens
Fix crash when processing empty requests
Restructure database layer for better performance
```

### Default Style

Simple, descriptive messages:

```
Update user authentication system
Fix API error handling
Refactor database connections
```

## Troubleshooting

### Common Issues

1. **"Model not found" error**
   ```bash
   ollama pull llama3.2
   ```

2. **"Ollama not responding" error**
   ```bash
   ollama serve
   ```

3. **"Not a git repository" error**
   ```bash
   git init
   ```

4. **Tree-sitter errors**
   ```bash
   pip install --upgrade tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Edit .gitgeist.json
{
  "log_level": "DEBUG"
}
```

Or set environment variable:
```bash
export GITGEIST_LOG_LEVEL=DEBUG
```

## Best Practices

1. **Start with dry-run**: Always test with `--dry-run` first
2. **Review generated commits**: Check the generated messages before auto-committing
3. **Configure ignore patterns**: Add project-specific patterns to avoid noise
4. **Use appropriate commit style**: Choose the style that fits your project
5. **Monitor logs**: Check logs for any issues or improvements

## Advanced Usage

### Custom Ignore Patterns

Add patterns to ignore specific files or directories:

```json
{
  "ignore_patterns": [
    ".git/*",
    "node_modules/*",
    "dist/*",
    "build/*",
    "*.log",
    "*.tmp",
    ".DS_Store"
  ]
}
```

### Multiple Watch Paths

Monitor specific directories:

```json
{
  "watch_paths": ["src/", "lib/", "tests/"]
}
```

### Temperature Tuning

Adjust LLM creativity:

```json
{
  "temperature": 0.1  // More focused
  "temperature": 0.7  // More creative
}
```

## Integration with Git Hooks

You can integrate Gitgeist with Git hooks for automated workflows:

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
gitgeist analyze
```

### Post-commit Hook

```bash
#!/bin/sh
# .git/hooks/post-commit
echo "Commit created with Gitgeist AI assistance"
```