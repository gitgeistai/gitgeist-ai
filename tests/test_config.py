# tests/test_config.py
import json
import tempfile
from pathlib import Path

import pytest

from gitgeist.core.config import GitgeistConfig
from gitgeist.core.schema import validate_config, validate_config_file


def test_config_defaults():
    """Test default configuration values"""
    config = GitgeistConfig()

    assert config.auto_commit == True
    assert config.commit_style == "conventional"
    assert config.llm_model == "llama3.2"
    assert config.autonomous_mode == False
    assert config.temperature == 0.3


def test_config_validation_valid():
    """Test valid configuration passes validation"""
    config_data = {
        "llm_model": "llama3.2",
        "commit_style": "conventional",
        "auto_commit": True,
        "temperature": 0.5,
    }

    errors = validate_config(config_data)
    assert len(errors) == 0


def test_config_validation_missing_required():
    """Test validation catches missing required fields"""
    config_data = {
        "auto_commit": True
        # Missing llm_model and commit_style
    }

    errors = validate_config(config_data)
    assert len(errors) == 2
    assert any("llm_model" in error for error in errors)
    assert any("commit_style" in error for error in errors)


def test_config_validation_invalid_enum():
    """Test validation catches invalid enum values"""
    config_data = {"llm_model": "llama3.2", "commit_style": "invalid_style"}

    errors = validate_config(config_data)
    assert len(errors) == 1
    assert "commit_style" in errors[0]


def test_config_validation_invalid_type():
    """Test validation catches type errors"""
    config_data = {
        "llm_model": "llama3.2",
        "commit_style": "conventional",
        "temperature": "not_a_number",
    }

    errors = validate_config(config_data)
    assert len(errors) == 1
    assert "temperature" in errors[0]


def test_config_file_validation():
    """Test configuration file validation"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_data = {"llm_model": "llama3.2", "commit_style": "conventional"}
        json.dump(config_data, f)
        config_path = Path(f.name)

    try:
        errors = validate_config_file(config_path)
        assert len(errors) == 0
    finally:
        config_path.unlink()


def test_config_save_load():
    """Test configuration save and load cycle"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"

        # Create and save config
        config = GitgeistConfig(llm_model="test_model", temperature=0.7)
        config.save(config_path)

        # Load and verify
        loaded_config = GitgeistConfig.load(config_path)
        assert loaded_config.llm_model == "test_model"
        assert loaded_config.temperature == 0.7
