# gitgeist/core/workspace.py
import json
from pathlib import Path
from typing import Dict, List, Optional

from gitgeist.core.config import GitgeistConfig
from gitgeist.utils.exceptions import ConfigurationError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class WorkspaceManager:
    """Manages multiple repositories in a workspace"""

    def __init__(self, workspace_path: Path = None):
        self.workspace_path = workspace_path or Path.home() / ".gitgeist"
        self.workspace_config_path = self.workspace_path / "workspace.json"
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    def add_repository(self, repo_path: str, alias: str = None) -> bool:
        """Add repository to workspace"""
        repo_path = Path(repo_path).resolve()
        
        if not (repo_path / ".git").exists():
            raise ConfigurationError(f"Not a git repository: {repo_path}")
        
        workspace_config = self._load_workspace_config()
        
        # Use directory name as alias if not provided
        if not alias:
            alias = repo_path.name
        
        # Check for conflicts
        if alias in workspace_config["repositories"]:
            existing_path = workspace_config["repositories"][alias]["path"]
            if existing_path != str(repo_path):
                raise ConfigurationError(f"Alias '{alias}' already exists for {existing_path}")
        
        workspace_config["repositories"][alias] = {
            "path": str(repo_path),
            "active": True,
            "last_used": None
        }
        
        self._save_workspace_config(workspace_config)
        logger.info(f"Added repository: {alias} -> {repo_path}")
        return True

    def remove_repository(self, alias: str) -> bool:
        """Remove repository from workspace"""
        workspace_config = self._load_workspace_config()
        
        if alias not in workspace_config["repositories"]:
            return False
        
        del workspace_config["repositories"][alias]
        self._save_workspace_config(workspace_config)
        logger.info(f"Removed repository: {alias}")
        return True

    def list_repositories(self) -> Dict[str, Dict]:
        """List all repositories in workspace"""
        workspace_config = self._load_workspace_config()
        return workspace_config["repositories"]

    def get_repository_path(self, alias: str) -> Optional[Path]:
        """Get path for repository alias"""
        workspace_config = self._load_workspace_config()
        repo_info = workspace_config["repositories"].get(alias)
        
        if repo_info:
            return Path(repo_info["path"])
        return None

    def set_active_repository(self, alias: str) -> bool:
        """Set active repository"""
        workspace_config = self._load_workspace_config()
        
        if alias not in workspace_config["repositories"]:
            return False
        
        # Deactivate all others
        for repo_alias in workspace_config["repositories"]:
            workspace_config["repositories"][repo_alias]["active"] = False
        
        # Activate selected
        workspace_config["repositories"][alias]["active"] = True
        workspace_config["repositories"][alias]["last_used"] = __import__('time').time()
        
        self._save_workspace_config(workspace_config)
        logger.info(f"Set active repository: {alias}")
        return True

    def get_active_repository(self) -> Optional[str]:
        """Get currently active repository alias"""
        workspace_config = self._load_workspace_config()
        
        for alias, info in workspace_config["repositories"].items():
            if info.get("active", False):
                return alias
        
        return None

    def _load_workspace_config(self) -> Dict:
        """Load workspace configuration"""
        if not self.workspace_config_path.exists():
            return {
                "version": "1.0",
                "repositories": {},
                "global_settings": {}
            }
        
        try:
            with open(self.workspace_config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workspace config: {e}")
            return {"version": "1.0", "repositories": {}, "global_settings": {}}

    def _save_workspace_config(self, config: Dict) -> None:
        """Save workspace configuration"""
        try:
            with open(self.workspace_config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workspace config: {e}")
            raise ConfigurationError(f"Cannot save workspace config: {e}")


class MultiRepoCommitGenerator:
    """Commit generator that works across multiple repositories"""

    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace = workspace_manager

    def commit_all_repositories(self, message: str = None) -> Dict[str, bool]:
        """Commit changes in all active repositories"""
        results = {}
        repositories = self.workspace.list_repositories()
        
        for alias, repo_info in repositories.items():
            if not repo_info.get("active", True):
                continue
            
            repo_path = Path(repo_info["path"])
            
            try:
                # Change to repository directory
                import os
                original_cwd = os.getcwd()
                os.chdir(repo_path)
                
                # Load repository-specific config
                config = GitgeistConfig.load()
                
                # Generate commit
                from gitgeist.ai.commit_generator import CommitGenerator
                generator = CommitGenerator(config)
                
                import asyncio
                result = asyncio.run(generator.generate_and_commit(message, auto_commit=True))
                results[alias] = result.get("committed", False)
                
            except Exception as e:
                logger.error(f"Failed to commit in {alias}: {e}")
                results[alias] = False
            finally:
                os.chdir(original_cwd)
        
        return results

    def get_status_all_repositories(self) -> Dict[str, Dict]:
        """Get status for all repositories"""
        status = {}
        repositories = self.workspace.list_repositories()
        
        for alias, repo_info in repositories.items():
            repo_path = Path(repo_info["path"])
            
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                changes = len([line for line in result.stdout.strip().split('\n') if line])
                status[alias] = {
                    "path": str(repo_path),
                    "changes": changes,
                    "clean": changes == 0,
                    "active": repo_info.get("active", True)
                }
                
            except Exception as e:
                status[alias] = {
                    "path": str(repo_path),
                    "error": str(e),
                    "active": repo_info.get("active", True)
                }
        
        return status