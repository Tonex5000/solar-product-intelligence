"""LLM Service for AI Explanation Layer using Groq."""
import json
import logging
from typing import Optional, Any
from functools import lru_cache

import requests
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMServiceError(Exception):
    """Exception for LLM service errors."""
    pass


class LLMResponse:
    """LLM response wrapper."""
    
    def __init__(self, content: str, model: str, usage: dict = None):
        self.content = content
        self.model = model
        self.usage = usage or {}


class LLMService:
    """
    LLM Service using Groq API.
    
    Supports multiple models including Qwen/Qwen3.6-27B.
    """
    
    # Available models on Groq
    AVAILABLE_MODELS = {
        "qwen": "qwen/qwen3.6-27b",
        "llama": "llama-3.3-70b-versatile",
        "mixtral": "mixtral-8x7b-32768",
        "default": "qwen/qwen3.6-27b",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen",
        temperature: float = 0.3,
        max_tokens: int = 2048
    ):
        """
        Initialize LLM service.
        
        Args:
            api_key: Groq API key (defaults to environment variable)
            model: Model to use (qwen, llama, mixtral, or default)
            temperature: Response temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            raise LLMServiceError("GROQ_API_KEY not configured")
        
        self.model = self.AVAILABLE_MODELS.get(model, model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = "https://api.groq.com/openai/v1"
        
    def _build_headers(self) -> dict:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _build_payload(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict:
        """Build request payload."""
        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
    
    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        Send a chat request to the LLM.
        
        Args:
            system_prompt: System prompt defining the assistant's role
            user_message: User's message/question
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            LLMResponse with content and metadata
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        payload = self._build_payload(messages, temperature, max_tokens)
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                raise LLMServiceError(f"Groq API error: {response.status_code}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage
            )
            
        except requests.exceptions.Timeout:
            raise LLMServiceError("Groq API request timed out")
        except requests.exceptions.RequestException as e:
            raise LLMServiceError(f"Groq API request failed: {str(e)}")
    
    def structured_chat(
        self,
        system_prompt: str,
        user_message: str,
        response_schema: dict,
        temperature: float = 0.1
    ) -> dict:
        """
        Send a chat request expecting structured JSON response.
        
        Args:
            system_prompt: System prompt defining the assistant's role
            user_message: User's message/question
            response_schema: JSON schema for expected response
            temperature: Temperature for more deterministic output
            
        Returns:
            Parsed JSON response
        """
        # Add JSON output instruction to system prompt
        enhanced_system = f"{system_prompt}\n\nIMPORTANT: Respond ONLY with valid JSON matching this schema:\n{json.dumps(response_schema, indent=2)}\nDo not include any text outside the JSON."
        
        response = self.chat(
            system_prompt=enhanced_system,
            user_message=user_message,
            temperature=temperature,
            max_tokens=4096
        )
        
        try:
            # Try to parse as JSON
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            content = response.content
            # Find JSON object in response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            raise LLMServiceError("Failed to parse structured response as JSON")
    
    def generate_explanation(
        self,
        system_prompt: str,
        context: str,
        question: str
    ) -> str:
        """
        Generate an explanation using the provided context.
        
        Args:
            system_prompt: System prompt for the explanation
            context: Context data to use
            question: User's question
            
        Returns:
            Generated explanation text
        """
        user_message = f"""Context Data:
---
{context}
---

Question: {question}

Based ONLY on the context data provided above, answer the question. If the information is not available in the context, clearly state "This information is not available in the provided data" rather than guessing."""

        response = self.chat(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return response.content


@lru_cache(maxsize=1)
def get_llm_service(
    api_key: Optional[str] = None,
    model: str = "qwen"
) -> LLMService:
    """
    Get cached LLM service instance.
    
    Args:
        api_key: Optional API key override
        model: Model to use
        
    Returns:
        LLMService instance
    """
    return LLMService(api_key=api_key, model=model)
