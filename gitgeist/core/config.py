# gitgeist/core/config.py
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GitgeistConfig:
    # Git settings
    auto_commit: bool = True
    commit_style: str = "conventional"  # conventional, semantic, custom

    # AI settings
    llm_model: str = "llama3.2"
    llm_host: str = "http://localhost:11434"
    temperature: float = 0.3

    # Watcher settings
    watch_paths: List[str] = field(default_factory=lambda: ["."])
    ignore_patterns: List[str] = field(
        default_factory=lambda: [
            ".git/*",
            "node_modules/*",
            "*.pyc",
            "__pycache__/*",
            "data/logs/*",
            "*.log",
            ".env",
            "venv/*",
            ".venv/*",
        ]
    )

    # AST settings
    supported_languages: List[str] = field(
        default_factory=lambda: ["python", "javascript", "typescript", "rust", "go"]
    )

    # Agent settings
    autonomous_mode: bool = False
    require_confirmation: bool = True
    max_commit_frequency: int = 300  # seconds

    # Paths
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    log_file: Path = field(default_factory=lambda: Path("./data/logs/gitgeist.log"))

    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "GitgeistConfig":
        """Load configuration from file or environment"""
        config_path = config_path or Path(".gitgeist.json")

        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
            # Convert string paths back to Path objects
            if "data_dir" in data:
                data["data_dir"] = Path(data["data_dir"])
            if "log_file" in data:
                data["log_file"] = Path(data["log_file"])
            return cls(**data)

        # Load from environment
        return cls(
            auto_commit=os.getenv("GITGEIST_AUTO_COMMIT", "true").lower() == "true",
            llm_model=os.getenv("GITGEIST_LLM_MODEL", "llama3.2"),
            autonomous_mode=os.getenv("GITGEIST_AUTONOMOUS", "false").lower() == "true",
        )

    def save(self, config_path: Optional[Path] = None):
        """Save configuration to file"""
        config_path = config_path or Path(".gitgeist.json")

        # Convert to JSON-serializable format
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                data[key] = str(value)
            else:
                data[key] = value

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
