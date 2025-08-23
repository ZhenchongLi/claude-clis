from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from claude_clis.shared.config import Config, ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".claude-clis"
        config_dir.mkdir()
        yield config_dir


@pytest.fixture
def config_manager(temp_config_dir):
    """Create a ConfigManager with a temporary directory"""
    manager = ConfigManager()
    manager._config_dir = temp_config_dir
    manager._config_file = temp_config_dir / "config.yaml"
    manager._config = None  # Reset cached config
    return manager


def test_config_defaults():
    """Test that default configuration values are correct"""
    config = Config()
    
    assert config.ai.provider == "gemini"
    assert config.ai.gemini.model == "gemini-1.5-pro"
    assert config.ai.gemini.temperature == 0.3
    assert config.ai.ollama.base_url == "http://localhost:11434"
    assert config.tools.doc2md.default_style == "technical"


def test_config_manager_load_empty(config_manager):
    """Test loading config when no file exists"""
    config = config_manager.load_config()
    
    assert config.ai.provider == "gemini"
    assert config.ai.gemini.model == "gemini-1.5-pro"


def test_config_manager_save_and_load(config_manager):
    """Test saving and loading configuration"""
    # Create and save config
    config = config_manager.load_config()
    config.ai.provider = "ollama"
    config.ai.gemini.api_key = "test-key"
    config_manager.save_config(config)
    
    # Load fresh instance
    config_manager._config = None
    loaded_config = config_manager.load_config()
    
    assert loaded_config.ai.provider == "ollama"
    assert loaded_config.ai.gemini.api_key == "test-key"


def test_config_manager_set_get_value(config_manager):
    """Test setting and getting configuration values"""
    config_manager.set_config_value("ai.provider", "anthropic")
    config_manager.set_config_value("ai.gemini.api_key", "secret-key")
    
    assert config_manager.get_config_value("ai.provider") == "anthropic"
    assert config_manager.get_config_value("ai.gemini.api_key") == "secret-key"


def test_get_ai_provider_priority(config_manager, monkeypatch):
    """Test AI provider selection priority"""
    # Set config file default
    config_manager.set_config_value("ai.provider", "gemini")
    
    # Test config file default
    assert config_manager.get_ai_provider() == "gemini"
    
    # Test environment variable override
    monkeypatch.setenv("CLAUDE_CLIS_AI_PROVIDER", "ollama")
    assert config_manager.get_ai_provider() == "ollama"
    
    # Test explicit override
    assert config_manager.get_ai_provider("anthropic") == "anthropic"


def test_get_ai_config(config_manager):
    """Test getting AI provider specific configuration"""
    config_manager.set_config_value("ai.gemini.api_key", "gemini-key")
    config_manager.set_config_value("ai.ollama.model", "llama3")
    
    gemini_config = config_manager.get_ai_config("gemini")
    assert gemini_config["api_key"] == "gemini-key"
    assert gemini_config["model"] == "gemini-1.5-pro"
    
    ollama_config = config_manager.get_ai_config("ollama")
    assert ollama_config["model"] == "llama3"
    assert ollama_config["base_url"] == "http://localhost:11434"


def test_get_ai_config_invalid_provider(config_manager):
    """Test error handling for invalid provider"""
    with pytest.raises(ValueError, match="Unknown AI provider"):
        config_manager.get_ai_config("invalid")


def test_config_file_format(config_manager):
    """Test that config file is saved in correct YAML format"""
    config_manager.set_config_value("ai.provider", "ollama")
    config_manager.set_config_value("ai.gemini.api_key", "test-key")
    
    # Read the file directly
    with open(config_manager.config_file, encoding="utf-8") as f:
        file_content = yaml.safe_load(f)
    
    assert file_content["ai"]["provider"] == "ollama"
    assert file_content["ai"]["gemini"]["api_key"] == "test-key"