# gitgeist/core/branch_manager.py
import subprocess
from typing import Dict, List, Optional

from gitgeist.utils.exceptions import GitError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class BranchManager:
    """Manages branch-aware commit strategies"""

    def __init__(self):
        self.branch_patterns = {
            "feature/": {
                "style": "conventional",
                "prefix": "feat",
                "require_scope": True,
                "max_length": 72
            },
            "fix/": {
                "style": "conventional", 
                "prefix": "fix",
                "require_scope": True,
                "max_length": 72
            },
            "hotfix/": {
                "style": "conventional",
                "prefix": "fix",
                "require_scope": False,
                "max_length": 50,
                "urgent": True
            },
            "release/": {
                "style": "semantic",
                "prefix": "release",
                "require_scope": False,
                "max_length": 60
            },
            "docs/": {
                "style": "conventional",
                "prefix": "docs",
                "require_scope": False,
                "max_length": 72
            },
            "main": {
                "style": "conventional",
                "prefix": None,
                "require_scope": False,
                "max_length": 72
            },
            "develop": {
                "style": "conventional",
                "prefix": None,
                "require_scope": True,
                "max_length": 72
            }
        }

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get current branch: {e}")
            return None

    def get_branch_config(self, branch_name: str = None) -> Dict:
        """Get configuration for current or specified branch"""
        if not branch_name:
            branch_name = self.get_current_branch()
        
        if not branch_name:
            return self.branch_patterns["main"]
        
        # Check for exact match first
        if branch_name in self.branch_patterns:
            return self.branch_patterns[branch_name]
        
        # Check for pattern matches
        for pattern, config in self.branch_patterns.items():
            if branch_name.startswith(pattern):
                return config
        
        # Default to main branch config
        return self.branch_patterns["main"]

    def should_auto_commit(self, branch_name: str = None) -> bool:
        """Check if branch allows auto-commits"""
        config = self.get_branch_config(branch_name)
        
        # Never auto-commit on main/master
        current_branch = branch_name or self.get_current_branch()
        if current_branch in ["main", "master", "production"]:
            return False
        
        # Check for urgent branches
        return not config.get("urgent", False)

    def get_commit_style(self, branch_name: str = None) -> str:
        """Get preferred commit style for branch"""
        config = self.get_branch_config(branch_name)
        return config.get("style", "conventional")

    def validate_commit_message(self, message: str, branch_name: str = None) -> bool:
        """Validate commit message against branch rules"""
        config = self.get_branch_config(branch_name)
        
        # Check length
        max_length = config.get("max_length", 72)
        if len(message.split('\n')[0]) > max_length:
            return False
        
        # Check prefix if required
        required_prefix = config.get("prefix")
        if required_prefix:
            if not message.startswith(f"{required_prefix}"):
                return False
        
        # Check scope if required
        if config.get("require_scope", False):
            # Simple check for scope pattern
            if required_prefix and f"{required_prefix}(" not in message:
                return False
        
        return True

    def suggest_commit_improvements(self, message: str, branch_name: str = None) -> List[str]:
        """Suggest improvements for commit message"""
        suggestions = []
        config = self.get_branch_config(branch_name)
        
        # Length check
        first_line = message.split('\n')[0]
        max_length = config.get("max_length", 72)
        if len(first_line) > max_length:
            suggestions.append(f"Shorten first line to under {max_length} characters")
        
        # Prefix check
        required_prefix = config.get("prefix")
        if required_prefix and not message.startswith(f"{required_prefix}"):
            suggestions.append(f"Add '{required_prefix}' prefix")
        
        # Scope check
        if config.get("require_scope", False) and required_prefix:
            if f"{required_prefix}(" not in message:
                suggestions.append(f"Add scope: {required_prefix}(scope): description")
        
        return suggestions

    def get_merge_commit_message(self, source_branch: str, target_branch: str = None) -> str:
        """Generate merge commit message"""
        if not target_branch:
            target_branch = self.get_current_branch() or "main"
        
        # Extract feature name from branch
        if "/" in source_branch:
            feature_name = source_branch.split("/", 1)[1]
        else:
            feature_name = source_branch
        
        return f"Merge branch '{source_branch}' into {target_branch}\n\nIntegrate {feature_name} changes"

    def is_protected_branch(self, branch_name: str = None) -> bool:
        """Check if branch is protected (requires extra confirmation)"""
        current_branch = branch_name or self.get_current_branch()
        protected_branches = ["main", "master", "production", "release"]
        
        if not current_branch:
            return True  # Err on the side of caution
        
        return current_branch in protected_branches or current_branch.startswith("release/")

    def get_branch_type(self, branch_name: str = None) -> str:
        """Get branch type classification"""
        current_branch = branch_name or self.get_current_branch()
        
        if not current_branch:
            return "unknown"
        
        if current_branch in ["main", "master"]:
            return "main"
        elif current_branch == "develop":
            return "develop"
        elif current_branch.startswith("feature/"):
            return "feature"
        elif current_branch.startswith("fix/"):
            return "bugfix"
        elif current_branch.startswith("hotfix/"):
            return "hotfix"
        elif current_branch.startswith("release/"):
            return "release"
        elif current_branch.startswith("docs/"):
            return "documentation"
        else:
            return "other"