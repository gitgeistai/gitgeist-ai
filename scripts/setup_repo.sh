#!/bin/bash

# Gitgeist Repository Setup Script

echo "🧠 Setting up Gitgeist repository..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files to git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "feat: initial release of Gitgeist v0.1.0

- Autonomous AI Git agent with local LLM integration
- Semantic code analysis using Tree-sitter
- Support for Python, JavaScript, TypeScript
- Conventional commit message generation
- Real-time file watching and change detection
- Comprehensive CLI interface
- 100% free and privacy-first"

# Create and push to main branch
echo "Setting up main branch..."
git branch -M main

echo "✅ Repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Create repository on GitHub: https://github.com/new"
echo "2. Add remote: git remote add origin https://github.com/your-username/gitgeist-ai.git"
echo "3. Push code: git push -u origin main"
echo "4. Create release: git tag v0.1.0 && git push origin v0.1.0"
echo ""
echo "🚀 Ready to launch!"