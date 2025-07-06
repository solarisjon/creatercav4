"""
Unified LLM client that handles all LLM provider integrations
"""
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion from prompt"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion using OpenAI"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 4000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion using Anthropic"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.3),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

class OpenRouterProvider(LLMProvider):
    """OpenRouter provider implementation"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet", 
                 base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion using OpenRouter"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 4000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter generation failed: {e}")
            raise

class LLMProxyProvider(LLMProvider):
    """LLM Proxy provider implementation (OpenAI-compatible)"""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion using LLM Proxy"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical analyst specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 4000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM Proxy generation failed: {e}")
            raise

class UnifiedLLMClient:
    """Unified client that manages multiple LLM providers with fallback support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {}
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup available LLM providers based on configuration"""
        # OpenAI
        if self.config.get('openai_api_key'):
            self.providers['openai'] = OpenAIProvider(
                api_key=self.config['openai_api_key'],
                model=self.config.get('openai_model', 'gpt-4o')
            )
        
        # Anthropic
        if self.config.get('anthropic_api_key'):
            self.providers['anthropic'] = AnthropicProvider(
                api_key=self.config['anthropic_api_key'],
                model=self.config.get('anthropic_model', 'claude-3-5-sonnet-20241022')
            )
        
        # OpenRouter
        if self.config.get('openrouter_api_key'):
            self.providers['openrouter'] = OpenRouterProvider(
                api_key=self.config['openrouter_api_key'],
                model=self.config.get('openrouter_model', 'anthropic/claude-3.5-sonnet'),
                base_url=self.config.get('openrouter_base_url', 'https://openrouter.ai/api/v1')
            )
        
        # LLM Proxy
        if self.config.get('llmproxy_api_key') and self.config.get('llmproxy_base_url'):
            self.providers['llmproxy'] = LLMProxyProvider(
                api_key=self.config['llmproxy_api_key'],
                model=self.config.get('llmproxy_model', 'gpt-4o'),
                base_url=self.config['llmproxy_base_url']
            )
        
        logger.info(f"Initialized LLM providers: {list(self.providers.keys())}")
    
    async def generate_analysis(self, prompt: str, preferred_provider: Optional[str] = None, **kwargs) -> str:
        """
        Generate analysis using specified provider with fallback support
        
        Args:
            prompt: The prompt to send to the LLM
            preferred_provider: Preferred LLM provider name
            **kwargs: Additional arguments (temperature, max_tokens, etc.)
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If all providers fail
        """
        # Determine provider order
        provider_order = self._get_provider_order(preferred_provider)
        
        last_error = None
        for provider_name in provider_order:
            if provider_name in self.providers:
                try:
                    logger.info(f"Attempting generation with provider: {provider_name}")
                    response = await self.providers[provider_name].generate_completion(prompt, **kwargs)
                    logger.info(f"Successfully generated response with provider: {provider_name}")
                    return response
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    last_error = e
                    continue
        
        # All providers failed
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _get_provider_order(self, preferred_provider: Optional[str] = None) -> List[str]:
        """Get ordered list of providers to try"""
        available_providers = list(self.providers.keys())
        
        if not available_providers:
            return []
        
        # If preferred provider specified and available, try it first
        if preferred_provider and preferred_provider in available_providers:
            order = [preferred_provider]
            order.extend([p for p in available_providers if p != preferred_provider])
            return order
        
        # Use config default
        default_provider = self.config.get('default_llm')
        if default_provider and default_provider in available_providers:
            order = [default_provider]
            order.extend([p for p in available_providers if p != default_provider])
            return order
        
        # Return all available providers
        return available_providers
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a specific provider is available"""
        return provider_name in self.providers
