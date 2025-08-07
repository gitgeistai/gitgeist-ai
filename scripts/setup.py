#!/usr/bin/env python3
"""
Setup script for Gitgeist development environment
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True):
    """Run shell command"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def main():
    """Setup development environment"""
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
