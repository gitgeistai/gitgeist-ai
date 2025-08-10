# gitgeist/core/schema.py
import json
from pathlib import Path
from typing import Any, Dict, List

GITGEIST_SCHEMA = {
    "type": "object",
    "properties": {
        "auto_commit": {"type": "boolean"},
        "commit_style": {
            "type": "string",
            "enum": ["conventional", "semantic", "default"],
        },
        "llm_model": {"type": "string"},
        "llm_host": {"type": "string", "format": "uri"},
        "temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
        "watch_paths": {"type": "array", "items": {"type": "string"}},
        "ignore_patterns": {"type": "array", "items": {"type": "string"}},
        "supported_languages": {"type": "array", "items": {"type": "string"}},
        "autonomous_mode": {"type": "boolean"},
        "require_confirmation": {"type": "boolean"},
        "max_commit_frequency": {"type": "integer", "minimum": 1},
        "data_dir": {"type": "string"},
        "log_file": {"type": "string"},
        "log_level": {
            "type": "string",
            "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
        },
    },
    "required": ["llm_model", "commit_style"],
    "additionalProperties": False,
}


def validate_config(config_data: Dict[str, Any]) -> List[str]:
    """Validate configuration against schema. Returns list of errors."""
    errors = []

    # Check required fields
    for field in GITGEIST_SCHEMA["required"]:
        if field not in config_data:
            errors.append(f"Missing required field: {field}")

    # Check field types and values
    for field, value in config_data.items():
        if field not in GITGEIST_SCHEMA["properties"]:
            errors.append(f"Unknown field: {field}")
            continue

        field_schema = GITGEIST_SCHEMA["properties"][field]

        # Type validation
        if field_schema["type"] == "boolean" and not isinstance(value, bool):
            errors.append(
                f"Field '{field}' must be boolean, got {type(value).__name__}"
            )
        elif field_schema["type"] == "string" and not isinstance(value, str):
            errors.append(f"Field '{field}' must be string, got {type(value).__name__}")
        elif field_schema["type"] == "number" and not isinstance(value, (int, float)):
            errors.append(f"Field '{field}' must be number, got {type(value).__name__}")
        elif field_schema["type"] == "integer" and not isinstance(value, int):
            errors.append(
                f"Field '{field}' must be integer, got {type(value).__name__}"
            )
        elif field_schema["type"] == "array" and not isinstance(value, list):
            errors.append(f"Field '{field}' must be array, got {type(value).__name__}")

        # Enum validation
        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append(
                f"Field '{field}' must be one of {field_schema['enum']}, got '{value}'"
            )

        # Range validation
        if (
            "minimum" in field_schema
            and isinstance(value, (int, float))
            and value < field_schema["minimum"]
        ):
            errors.append(
                f"Field '{field}' must be >= {field_schema['minimum']}, got {value}"
            )
        if (
            "maximum" in field_schema
            and isinstance(value, (int, float))
            and value > field_schema["maximum"]
        ):
            errors.append(
                f"Field '{field}' must be <= {field_schema['maximum']}, got {value}"
            )

    return errors


def validate_config_file(config_path: Path) -> List[str]:
    """Validate configuration file. Returns list of errors."""
    if not config_path.exists():
        return [f"Configuration file not found: {config_path}"]

    try:
        with open(config_path) as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in configuration file: {e}"]
    except Exception as e:
        return [f"Error reading configuration file: {e}"]

    return validate_config(config_data)
