# gitgeist/utils/recovery.py
import json
import shutil
from pathlib import Path
from typing import Dict, Optional

from gitgeist.core.config import GitgeistConfig
from gitgeist.utils.exceptions import GitgeistError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class RecoveryManager:
    """Handles error recovery and system repair"""

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path(".gitgeist.json")
        self.backup_path = Path(".gitgeist.backup.json")

    def create_backup(self) -> bool:
        """Create backup of current configuration"""
        try:
            if self.config_path.exists():
                shutil.copy2(self.config_path, self.backup_path)
                logger.info("Configuration backup created")
                return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
        return False

    def restore_backup(self) -> bool:
        """Restore configuration from backup"""
        try:
            if self.backup_path.exists():
                shutil.copy2(self.backup_path, self.config_path)
                logger.info("Configuration restored from backup")
                return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
        return False

    def repair_config(self) -> Optional[GitgeistConfig]:
        """Attempt to repair corrupted configuration"""
        try:
            # Try to load existing config
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Fix common issues
                repaired_data = self._repair_config_data(data)
                
                # Save repaired config
                with open(self.config_path, 'w') as f:
                    json.dump(repaired_data, f, indent=2)
                
                logger.info("Configuration repaired")
                return GitgeistConfig.load()
                
        except Exception as e:
            logger.error(f"Config repair failed: {e}")
            
            # Try backup restore
            if self.restore_backup():
                try:
                    return GitgeistConfig.load()
                except Exception:
                    pass
        
        return None

    def _repair_config_data(self, data: Dict) -> Dict:
        """Repair configuration data"""
        defaults = {
            "autonomous_mode": False,
            "commit_style": "conventional",
            "llm_model": "llama3.2",
            "llm_host": "http://localhost:11434",
            "temperature": 0.3,
            "log_level": "INFO",
            "watch_paths": ["."],
            "ignore_patterns": [
                ".git/*", "node_modules/*", "*.pyc", "__pycache__/*",
                ".env", "venv/*", ".venv/*"
            ],
            "supported_languages": ["python", "javascript", "typescript"],
            "require_confirmation": True,
            "max_commit_frequency": 300
        }
        
        # Fill missing keys with defaults
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
                logger.debug(f"Added missing config key: {key}")
        
        # Fix invalid values
        if not isinstance(data.get("temperature"), (int, float)):
            data["temperature"] = 0.3
        
        if data.get("commit_style") not in ["conventional", "semantic", "default"]:
            data["commit_style"] = "conventional"
        
        if not isinstance(data.get("watch_paths"), list):
            data["watch_paths"] = ["."]
        
        return data

    def clean_data_directory(self) -> bool:
        """Clean corrupted data directory"""
        try:
            data_dir = Path("data")
            if data_dir.exists():
                # Remove corrupted memory database
                memory_db = data_dir / "memory.db"
                if memory_db.exists():
                    memory_db.unlink()
                    logger.info("Removed corrupted memory database")
                
                # Clean log files older than 7 days
                logs_dir = data_dir / "logs"
                if logs_dir.exists():
                    import time
                    week_ago = time.time() - (7 * 24 * 60 * 60)
                    
                    for log_file in logs_dir.glob("*.log"):
                        if log_file.stat().st_mtime < week_ago:
                            log_file.unlink()
                            logger.debug(f"Removed old log: {log_file}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to clean data directory: {e}")
        
        return False

    def reset_to_defaults(self) -> GitgeistConfig:
        """Reset configuration to defaults"""
        try:
            # Create backup first
            self.create_backup()
            
            # Remove existing config
            if self.config_path.exists():
                self.config_path.unlink()
            
            # Create new default config
            config = GitgeistConfig()
            config.save()
            
            logger.info("Configuration reset to defaults")
            return config
            
        except Exception as e:
            logger.error(f"Failed to reset config: {e}")
            raise GitgeistError(f"Could not reset configuration: {e}")

    def diagnose_system(self) -> Dict[str, bool]:
        """Diagnose system health"""
        diagnosis = {
            "config_exists": self.config_path.exists(),
            "config_valid": False,
            "git_repo": False,
            "data_dir": False,
            "dependencies": False
        }
        
        # Check config validity
        try:
            GitgeistConfig.load()
            diagnosis["config_valid"] = True
        except Exception:
            pass
        
        # Check git repository
        try:
            from gitgeist.core.validator import GitValidator
            GitValidator.validate_repository()
            diagnosis["git_repo"] = True
        except Exception:
            pass
        
        # Check data directory
        data_dir = Path("data")
        diagnosis["data_dir"] = data_dir.exists() and data_dir.is_dir()
        
        # Check dependencies
        try:
            from gitgeist.core.validator import SystemValidator
            missing = SystemValidator.validate_dependencies()
            diagnosis["dependencies"] = len(missing) == 0
        except Exception:
            pass
        
        return diagnosis