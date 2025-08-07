# gitgeist/ai/llm_client.py
import aiohttp
import asyncio
import json
from typing import Dict, Optional, AsyncGenerator
from gitgeist.core.config import GitgeistConfig
from gitgeist.utils.logger import get_logger
from gitgeist.utils.exceptions import LLMError

logger = get_logger(__name__)

class OllamaClient:
    """Async client for Ollama LLM interactions"""
    
    def __init__(self, config: GitgeistConfig):
        self.config = config
        self.base_url = config.llm_host.rstrip('/')
        self.model = config.llm_model
        self.temperature = config.temperature
        
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": 0.9,
                "num_predict": 200  # Keep commit messages concise
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "").strip()
                    else:
                        error_text = await response.text()
                        raise LLMError(f"Ollama API error {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out")
            raise LLMError("LLM request timed out")
        except aiohttp.ClientError as e:
            logger.error(f"Ollama connection failed: {e}")
            raise LLMError(f"Failed to connect to Ollama: {e}")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise LLMError(f"LLM generation failed: {e}")
    
    async def check_model_availability(self) -> bool:
        """Check if the specified model is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model['name'] for model in data.get('models', [])]
                        # Check for exact match or with :latest suffix
                        return (self.model in models or 
                                f"{self.model}:latest" in models or
                                any(model.startswith(f"{self.model}:") for model in models))
                    return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and responsive"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False