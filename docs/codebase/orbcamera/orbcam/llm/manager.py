
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from .providers import LLMProvider, OpenAIProvider, AnthropicProvider, GeminiProvider, OllamaProvider, ModelInfo

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("d:/Projects/orbcamera/config/models.json")

class LLMManager:
    """
    Manages LLM Providers, API Keys, and Active Model selection.
    Persists state to config/models.json.
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.active_provider: Optional[LLMProvider] = None
        self._initialize_active_provider()
        
    def _load_config(self) -> Dict:
        if not CONFIG_PATH.exists():
            return {
                "providers": {}, # { 'openai': {'api_key': '...'}, 'anthropic': ... }
                "active_model": None, # { 'provider': 'openai', 'model_id': 'gpt-4o' }
                "models_cache": {} # { 'openai': ['gpt-4o', ...] }
            }
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _initialize_active_provider(self):
        active = self.config.get("active_model")
        if active:
            provider_name = active.get("provider")
            self.active_provider = self._create_provider_instance(provider_name)

    def _create_provider_instance(self, provider_name: str) -> Optional[LLMProvider]:
        creds = self.config.get("providers", {}).get(provider_name)
        if not creds: return None
        
        api_key = creds.get("api_key")
        base_url = creds.get("base_url")
        
        if provider_name == "openai":
            return OpenAIProvider(api_key, base_url)
        elif provider_name == "anthropic":
            return AnthropicProvider(api_key, base_url)
        # Add Gemini/Ollama later
        return None

    def add_provider(self, name: str, api_key: str, base_url: Optional[str] = None) -> bool:
        """Register a new provider and verify connection."""
        # Temporary config update to test
        previous_config = self.config.get("providers", {}).get(name)
        
        self.config.setdefault("providers", {})[name] = {"api_key": api_key, "base_url": base_url}
        
        # Test connection
        provider = self._create_provider_instance(name)
        if provider and provider.verify_connection():
            # Success: Persist
            self._save_config()
            # Fetch Models
            models = provider.list_models()
            self.config.setdefault("models_cache", {})[name] = [m.id for m in models]
            self._save_config()
            return True
        else:
            # Revert if failed
            if previous_config:
                self.config["providers"][name] = previous_config
            else:
                del self.config["providers"][name]
            return False

    def get_available_models(self) -> Dict[str, List[str]]:
        return self.config.get("models_cache", {})

    def set_active_model(self, provider_name: str, model_id: str):
        if provider_name not in self.config.get("providers", {}):
            raise ValueError(f"Provider {provider_name} not configured.")
            
        self.config["active_model"] = {"provider": provider_name, "model_id": model_id}
        self._save_config()
        self._initialize_active_provider()
        
    def think(self, user_content: List[Dict]) -> str:
        """
        Main entry point for the Agent.
        """
        if not self.active_provider:
            return json.dumps({"thought": "No Brain Connected", "action": "wait"})
            
        active = self.config.get("active_model")
        model_id = active.get("model_id")
        
        system_prompt = """
        You are OrbOS, an autonomous camera agent.
        Output JSON: {"thought": "...", "action": "...", "parameters": {...}}
        Actions: [patrol, track, wait, reset]
        """
        
        return self.active_provider.chat(model_id, system_prompt, user_content)
