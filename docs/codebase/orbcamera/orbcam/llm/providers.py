
import os
import abc
import json
import base64
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelInfo:
    def __init__(self, id: str, name: str, provider: str):
        self.id = id
        self.name = name
        self.provider = provider
        
    def __repr__(self):
        return f"[{self.provider}] {self.name} ({self.id})"

class LLMProvider(abc.ABC):
    """Abstract Base Class for all LLM Providers"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        
    @abc.abstractmethod
    def verify_connection(self) -> bool:
        """Verify that the API key works."""
        pass
        
    @abc.abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """Fetch list of available models from the API."""
        pass
        
    @abc.abstractmethod
    def chat(self, model_id: str, system_prompt: str, user_content: List[Dict[str, Any]]) -> str:
        """
        Send a chat request.
        user_content format: [{'type': 'text', 'text': '...'}, {'type': 'image_url', ...}]
        """
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("openai package missing. Run: pip install openai")

    def verify_connection(self) -> bool:
        try:
            # Simple list models check
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI Connection Failed: {e}")
            return False
            
    def list_models(self) -> List[ModelInfo]:
        try:
            resp = self.client.models.list()
            # Filter for likely chat models
            models = []
            for m in resp.data:
                if "gpt" in m.id:
                    models.append(ModelInfo(m.id, m.id, "openai"))
            return sorted(models, key=lambda x: x.id, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def chat(self, model_id: str, system_prompt: str, user_content: List[Dict[str, Any]]) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        response = self.client.chat.completions.create(
            model=model_id,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=500
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key, base_url=base_url)
        except ImportError:
            raise ImportError("anthropic package missing. Run: pip install anthropic")

    def verify_connection(self) -> bool:
        try:
            # Anthropic doesn't have a lightweight 'list models' endpoint that is free/fast check usually,
            # but we can try a tiny message.
            self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic Connection Failed: {e}")
            return False

    def list_models(self) -> List[ModelInfo]:
        # Anthropic does not expose a list_models API yet. We return the known static list.
        known = [
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        return [ModelInfo(m, m, "anthropic") for m in known]

    def chat(self, model_id: str, system_prompt: str, user_content: List[Dict[str, Any]]) -> str:
        # Anthropic 'system' is a separate parameter
        # content must be converted: 'image_url' -> 'image' block
        fixed_content = []
        for item in user_content:
            if item['type'] == 'text':
                fixed_content.append(item)
            elif item['type'] == 'image_url':
                # Extract base64
                url = item['image_url']['url']
                if "base64," in url:
                    media_type = url.split(";")[0].split(":")[1]
                    data = url.split("base64,")[1]
                    fixed_content.append({
                        "type": "image", 
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data
                        }
                    })
        
        response = self.client.messages.create(
            model=model_id,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": fixed_content}]
        )
        return response.content[0].text

class GeminiProvider(LLMProvider):
    # Placeholders for future expansion (user requested multi-model capability)
    def verify_connection(self): return False
    def list_models(self): return []
    def chat(self, *args): return "{}"

class OllamaProvider(LLMProvider):
    # Placeholders for future expansion
    def verify_connection(self): return False
    def list_models(self): return []
    def chat(self, *args): return "{}"
