from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GeminiConfig(BaseModel):
    api_key: str = ""
    model: str = "gemini-1.5-pro"
    temperature: float = 0.3
    max_tokens: int = 4096


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2:latest"
    temperature: float = 0.3
    timeout: int = 120


class AnthropicConfig(BaseModel):
    api_key: str = ""
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.3
    max_tokens: int = 4096


class AIConfig(BaseModel):
    provider: Literal["gemini", "ollama", "anthropic"] = "gemini"
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)


class Doc2mdConfig(BaseModel):
    default_style: str = "technical"
    chunk_size: int = 4000
    preserve_formatting: bool = True
    output_format: str = "markdown"


class ToolsConfig(BaseModel):
    doc2md: Doc2mdConfig = Field(default_factory=Doc2mdConfig)


class Config(BaseSettings):
    ai: AIConfig = Field(default_factory=AIConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)

    class Config:
        env_prefix = "CLAUDE_CLIS_"
        env_nested_delimiter = "_"


class ConfigManager:
    def __init__(self) -> None:
        self._config_dir = Path.home() / ".claude-clis"
        self._config_file = self._config_dir / "config.yaml"
        self._config: Config | None = None

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def config_file(self) -> Path:
        return self._config_file

    def ensure_config_dir(self) -> None:
        self._config_dir.mkdir(exist_ok=True)

    def load_config(self) -> Config:
        if self._config is not None:
            return self._config

        # Load from file if exists
        config_data: dict[str, Any] = {}
        if self._config_file.exists():
            with open(self._config_file, encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

        # Create config with environment variables and file data
        self._config = Config(**config_data)
        return self._config

    def save_config(self, config: Config | None = None) -> None:
        if config is not None:
            self._config = config

        if self._config is None:
            raise ValueError("No config to save")

        self.ensure_config_dir()
        
        # Convert to dict and save
        config_dict = self._config.model_dump(exclude_unset=False)
        with open(self._config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

    def get_ai_provider(self, override: str | None = None) -> str:
        if override:
            return override
        
        # Check environment variable
        env_provider = os.getenv("CLAUDE_CLIS_AI_PROVIDER")
        if env_provider:
            return env_provider
            
        # Use config file default
        config = self.load_config()
        return config.ai.provider

    def get_ai_config(self, provider: str | None = None) -> dict[str, Any]:
        config = self.load_config()
        provider = provider or self.get_ai_provider()
        
        if provider == "gemini":
            return config.ai.gemini.model_dump()
        elif provider == "ollama":
            return config.ai.ollama.model_dump()
        elif provider == "anthropic":
            return config.ai.anthropic.model_dump()
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

    def set_config_value(self, key: str, value: Any) -> None:
        config = self.load_config()
        
        # Handle nested keys like "ai.provider" or "ai.gemini.api_key"
        keys = key.split(".")
        target = config
        
        for k in keys[:-1]:
            target = getattr(target, k)
        
        setattr(target, keys[-1], value)
        self.save_config(config)

    def get_config_value(self, key: str) -> Any:
        config = self.load_config()
        
        keys = key.split(".")
        target = config
        
        for k in keys:
            target = getattr(target, k)
        
        return target

    def show_config(self) -> dict[str, Any]:
        config = self.load_config()
        return config.model_dump()


# Global config manager instance
config_manager = ConfigManager()