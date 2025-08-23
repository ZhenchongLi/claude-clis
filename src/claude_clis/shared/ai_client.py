from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName, Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
# from pydantic_ai.models.ollama import OllamaModel

from .config import ConfigManager


class AIClientError(Exception):
    pass


class AIClient:
    def __init__(self, config_manager: ConfigManager) -> None:
        self._config_manager = config_manager
        self._models: dict[str, Model] = {}

    def _get_model(self, provider: str) -> Model:
        if provider in self._models:
            return self._models[provider]

        config = self._config_manager.get_ai_config(provider)
        
        if provider == "gemini":
            # Check for API key
            api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise AIClientError(
                    "Gemini API key not found. Set GOOGLE_API_KEY or configure it with: "
                    "claude-clis config set ai.gemini.api_key YOUR_KEY"
                )
            
            model = GeminiModel(
                model_name=config["model"],
                api_key=api_key,
            )
            
        elif provider == "ollama":
            # Use OpenAI-compatible endpoint for Ollama
            from pydantic_ai.models.openai import OpenAIModel
            model = OpenAIModel(
                model_name=config["model"],
                base_url=config["base_url"] + "/v1",
                api_key="ollama",  # Ollama doesn't need real API key
                http_client=httpx.Client(timeout=config["timeout"]),
            )
            
        elif provider == "anthropic":
            # Check for API key
            api_key = config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise AIClientError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY or configure it with: "
                    "claude-clis config set ai.anthropic.api_key YOUR_KEY"
                )
            
            model = AnthropicModel(
                model_name=config["model"],
                api_key=api_key,
            )
            
        else:
            raise AIClientError(f"Unknown AI provider: {provider}")

        self._models[provider] = model
        return model

    def create_agent(
        self, 
        provider: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> Agent[None, str]:
        provider = provider or self._config_manager.get_ai_provider()
        model = self._get_model(provider)
        
        return Agent(
            model=model,
            system_prompt=system_prompt,
            **kwargs
        )

    async def run_prompt(
        self,
        prompt: str,
        provider: str | None = None,
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> str:
        agent = self.create_agent(provider, system_prompt, **kwargs)
        
        try:
            result = await agent.run(prompt)
            return result.data
        except Exception as e:
            raise AIClientError(f"AI request failed: {str(e)}") from e

    def get_available_providers(self) -> list[str]:
        return ["gemini", "ollama", "anthropic"]

    def test_provider(self, provider: str) -> bool:
        try:
            self._get_model(provider)
            return True
        except AIClientError:
            return False


class DocumentProcessor:
    def __init__(self, ai_client: AIClient) -> None:
        self.ai_client = ai_client
    
    def _create_conversion_prompt(
        self, 
        content: str, 
        style: str = "technical",
        preserve_formatting: bool = True
    ) -> str:
        base_prompt = f"""Convert the following document content to clean, well-structured Markdown format.

Requirements:
- Maintain document structure and hierarchy
- Use appropriate Markdown syntax for headers, lists, tables, etc.
- {"Preserve original formatting and styling as much as possible" if preserve_formatting else "Focus on clean, readable structure"}
- Style: {style}
- Remove any unnecessary whitespace or formatting artifacts
- Ensure proper code block formatting if code is present

Document content:
{content}

Please provide only the converted Markdown content without any additional explanation."""

        return base_prompt

    async def convert_to_markdown(
        self,
        content: str,
        provider: str | None = None,
        style: str = "technical",
        preserve_formatting: bool = True,
        **kwargs: Any
    ) -> str:
        prompt = self._create_conversion_prompt(content, style, preserve_formatting)
        
        system_prompt = """You are an expert document converter specialized in converting various document formats to clean, well-structured Markdown. 
        
        Focus on:
        - Accurate content preservation
        - Proper Markdown syntax
        - Clean, readable output
        - Maintaining document structure and hierarchy
        """
        
        return await self.ai_client.run_prompt(
            prompt=prompt,
            provider=provider,
            system_prompt=system_prompt,
            **kwargs
        )

    def chunk_content(self, content: str, chunk_size: int = 4000) -> list[str]:
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(content):
            # Find a good break point (prefer paragraph breaks)
            end_pos = min(current_pos + chunk_size, len(content))
            
            if end_pos < len(content):
                # Look for paragraph break
                for i in range(end_pos, max(current_pos + chunk_size // 2, end_pos - 200), -1):
                    if content[i:i+2] == "\n\n":
                        end_pos = i + 2
                        break
                else:
                    # Look for sentence break
                    for i in range(end_pos, max(current_pos + chunk_size // 2, end_pos - 100), -1):
                        if content[i] in ".!?":
                            end_pos = i + 1
                            break
            
            chunk = content[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            current_pos = end_pos
        
        return chunks

    async def process_large_content(
        self,
        content: str,
        provider: str | None = None,
        chunk_size: int = 4000,
        style: str = "technical",
        preserve_formatting: bool = True,
        **kwargs: Any
    ) -> str:
        chunks = self.chunk_content(content, chunk_size)
        
        if len(chunks) == 1:
            return await self.convert_to_markdown(
                content, provider, style, preserve_formatting, **kwargs
            )
        
        # Process chunks and combine results
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_prompt = self._create_conversion_prompt(
                chunk, style, preserve_formatting
            ) + f"\n\nNote: This is part {i+1} of {len(chunks)} of a larger document."
            
            processed_chunk = await self.ai_client.run_prompt(
                prompt=chunk_prompt,
                provider=provider,
                system_prompt="You are converting part of a larger document to Markdown. Maintain consistency with document structure.",
                **kwargs
            )
            processed_chunks.append(processed_chunk)
        
        return "\n\n---\n\n".join(processed_chunks)