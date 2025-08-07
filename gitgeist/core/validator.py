# gitgeist/core/validator.py
import re
from pathlib import Path
from typing import Dict, List, Optional

from gitgeist.utils.exceptions import ValidationError


class ConfigValidator:
    """Validates configuration values"""

    @staticmethod
    def validate_model_name(model: str) -> None:
        """Validate LLM model name"""
        if not model or not isinstance(model, str):
            raise ValidationError("Model name must be a non-empty string")
        
        if len(model) > 100:
            raise ValidationError("Model name too long", "Use a shorter model name")

    @staticmethod
    def validate_host_url(host: str) -> None:
        """Validate Ollama host URL"""
        if not host or not isinstance(host, str):
            raise ValidationError("Host URL must be a non-empty string")
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(host):
            raise ValidationError(
                f"Invalid host URL: {host}",
                "Use format: http://localhost:11434"
            )

    @staticmethod
    def validate_temperature(temp: float) -> None:
        """Validate LLM temperature"""
        if not isinstance(temp, (int, float)):
            raise ValidationError("Temperature must be a number")
        
        if not 0.0 <= temp <= 2.0:
            raise ValidationError(
                f"Temperature {temp} out of range",
                "Use value between 0.0 and 2.0"
            )

    @staticmethod
    def validate_commit_style(style: str) -> None:
        """Validate commit style"""
        valid_styles = ["conventional", "semantic", "default"]
        if style not in valid_styles:
            raise ValidationError(
                f"Invalid commit style: {style}",
                f"Use one of: {', '.join(valid_styles)}"
            )

    @staticmethod
    def validate_paths(paths: List[str]) -> None:
        """Validate watch paths"""
        if not isinstance(paths, list):
            raise ValidationError("Watch paths must be a list")
        
        for path in paths:
            if not isinstance(path, str):
                raise ValidationError("All paths must be strings")
            
            if not path.strip():
                raise ValidationError("Empty path not allowed")

    @staticmethod
    def validate_ignore_patterns(patterns: List[str]) -> None:
        """Validate ignore patterns"""
        if not isinstance(patterns, list):
            raise ValidationError("Ignore patterns must be a list")
        
        for pattern in patterns:
            if not isinstance(pattern, str):
                raise ValidationError("All patterns must be strings")


class GitValidator:
    """Validates git-related operations"""

    @staticmethod
    def validate_repository(path: Path = None) -> None:
        """Validate git repository"""
        repo_path = path or Path.cwd()
        git_dir = repo_path / ".git"
        
        if not git_dir.exists():
            raise ValidationError(
                "Not a git repository",
                "Run 'git init' to initialize a repository"
            )

    @staticmethod
    def validate_commit_message(message: str) -> None:
        """Validate commit message format"""
        if not message or not message.strip():
            raise ValidationError("Commit message cannot be empty")
        
        if len(message) > 500:
            raise ValidationError(
                "Commit message too long",
                "Keep messages under 500 characters"
            )
        
        # Check for common issues
        if message.startswith(" ") or message.endswith(" "):
            raise ValidationError(
                "Commit message has leading/trailing spaces",
                "Remove extra spaces"
            )


class SystemValidator:
    """Validates system requirements"""

    @staticmethod
    def validate_dependencies() -> List[str]:
        """Check for missing dependencies"""
        missing = []
        
        try:
            import tree_sitter
        except ImportError:
            missing.append("tree-sitter")
        
        try:
            import sentence_transformers
        except ImportError:
            missing.append("sentence-transformers")
        
        try:
            import aiohttp
        except ImportError:
            missing.append("aiohttp")
        
        return missing

    @staticmethod
    def validate_disk_space(required_mb: int = 100) -> None:
        """Check available disk space"""
        import shutil
        
        free_bytes = shutil.disk_usage(Path.cwd()).free
        free_mb = free_bytes / (1024 * 1024)
        
        if free_mb < required_mb:
            raise ValidationError(
                f"Insufficient disk space: {free_mb:.1f}MB available",
                f"Need at least {required_mb}MB free space"
            )