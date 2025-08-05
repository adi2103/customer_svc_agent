"""
LLM-agnostic adapter interface with pluggable providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.constants import DEFAULT_TEMPERATURE


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def initialize(self, api_key: str, model: str) -> bool:
        """Initialize the provider with API key and model."""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """Send chat request with optional tools."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""

    def __init__(self):
        self.client = None
        self.model = None
        self.available = False

    def initialize(self, api_key: str, model: str = "gemini-2.5-flash-lite") -> bool:
        """Initialize Gemini provider."""
        try:
            import google.genai as genai

            self.client = genai.Client(api_key=api_key)
            self.model = model
            self.available = True
            print(f"✅ Gemini provider initialized with {model}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.available = False
            return False

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """Send chat request to Gemini."""
        if not self.available:
            return {
                "content": "🏔️ Gemini provider not available. Please check your GEMINI_API_KEY!",
                "error": "Provider not available",
            }

        try:
            from google.genai import types

            # Build conversation context
            conversation_context = self._build_conversation_context(messages)

            # Create config with proper format
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=3000,
            )

            # Add tools to config if provided
            if tools:
                # Convert tools to Python functions for Gemini
                # For now, we'll skip function calling and just use text generation
                # This allows the system to work without complex function calling setup
                pass

            # Make the request
            response = self.client.models.generate_content(
                model=self.model,
                contents=conversation_context,
                config=config,
            )

            return self._parse_response(response)

        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return {
                "content": f"🏔️ I encountered a challenge on this trail! Error: {str(e)} Let's try again! ⛰️",
                "error": str(e),
            }

    def is_available(self) -> bool:
        """Check if Gemini provider is available."""
        return self.available

    def _build_conversation_context(self, messages: List[Dict[str, str]]) -> str:
        """Build conversation context from messages for Gemini."""
        context_parts = []

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")

            if role == "system":
                context_parts.append(f"SYSTEM INSTRUCTIONS: {content}")
            elif role == "user":
                context_parts.append(f"USER: {content}")
            elif role == "assistant":
                context_parts.append(f"ASSISTANT: {content}")

        return "\n\n".join(context_parts)

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse Gemini response into standardized format."""
        try:
            # Try the text attribute first (most common)
            if hasattr(response, "text") and response.text:
                return {"content": response.text.strip(), "success": True}

            # Check if response has candidates
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]

                if hasattr(candidate, "content") and candidate.content:
                    if hasattr(candidate.content, "parts") and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Regular text response
                            if hasattr(part, "text") and part.text and part.text.strip():
                                return {"content": part.text.strip(), "success": True}

            # If we can't parse the response but it's a valid response object,
            # it might be a truncated response due to max tokens
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason") and str(candidate.finish_reason) == "FinishReason.MAX_TOKENS":
                    max_tokens_msg = (
                        "🏔️ I was getting really excited about your request and had a lot "
                        "to share! Let me give you a more concise response. Could you please "
                        "ask again? Onward into the unknown! 🌟"
                    )
                    return {
                        "content": max_tokens_msg,
                        "success": True,
                    }

            # Try to convert response to string as fallback
            response_str = str(response)
            if response_str and response_str != str(type(response)) and len(response_str) < 1000:
                return {"content": response_str, "success": True}

            # If we can't parse the response
            return {
                "content": "🏔️ I received a response but had trouble understanding it. Let's try again! ⛰️",
                "error": "Unable to parse response",
                "success": False,
            }

        except Exception as e:
            return {
                "content": f"🏔️ I had trouble processing the response. Error: {str(e)} Let's try again! ⛰️",
                "error": str(e),
                "success": False,
            }


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""

    def __init__(self):
        self.client = None
        self.model = None
        self.available = False

    def initialize(self, api_key: str, model: str = "gpt-4o-mini") -> bool:
        """Initialize OpenAI provider."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key)
            self.model = model
            self.available = True
            print(f"✅ OpenAI provider initialized with {model}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI: {e}")
            self.available = False
            return False

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """Send chat request to OpenAI."""
        if not self.available:
            return {
                "content": "🏔️ OpenAI provider not available. Please check your OPENAI_API_KEY!",
                "error": "Provider not available",
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                temperature=temperature,
            )

            return self._parse_response(response)

        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return {
                "content": f"🏔️ I encountered a challenge on this trail! Error: {str(e)} Let's try again! ⛰️",
                "error": str(e),
            }

    def is_available(self) -> bool:
        """Check if OpenAI provider is available."""
        return self.available

    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse OpenAI response into standardized format."""
        try:
            message = response.choices[0].message

            result = {
                "content": message.content or "",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

            # Handle tool calls
            if message.tool_calls:
                result["tool_calls"] = []
                for tool_call in message.tool_calls:
                    import json

                    result["tool_calls"].append(
                        {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": json.loads(tool_call.function.arguments),
                            },
                        }
                    )

            return result

        except Exception as e:
            return {
                "content": f"🏔️ I had trouble processing the response. Error: {str(e)} Let's try again! ⛰️",
                "error": str(e),
            }


class LLMAdapter:
    """LLM-agnostic adapter with pluggable providers."""

    def __init__(self, provider: str = "gemini", model: str = None, api_key: str = None):
        """Initialize adapter with specified provider."""
        self.provider_name = provider
        self.provider = None

        # Create provider instance
        if provider.lower() == "gemini":
            self.provider = GeminiProvider()
            default_model = os.getenv("GEMINI_API_MODEL")
            if not default_model:
                default_model = "gemini-2.5-flash-lite"
            default_api_key = os.getenv("GEMINI_API_KEY")
        elif provider.lower() == "openai":
            self.provider = OpenAIProvider()
            default_model = "gpt-4o-mini"
            default_api_key = os.getenv("OPENAI_API_KEY")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Use provided values or defaults
        final_model = model or default_model
        final_api_key = api_key or default_api_key

        if not final_api_key:
            print(f"⚠️  No API key provided for {provider}")
            return

        # Initialize the provider
        self.provider.initialize(final_api_key, final_model)

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> Dict[str, Any]:
        """Send chat request using the configured provider."""
        if not self.provider:
            return {"content": "🏔️ No LLM provider configured!", "error": "No provider"}

        return self.provider.chat(messages, tools, temperature)

    def is_available(self) -> bool:
        """Check if the adapter is available."""
        return self.provider and self.provider.is_available()

    def get_provider_name(self) -> str:
        """Get the name of the current provider."""
        return self.provider_name

    def switch_provider(self, provider: str, model: str = None, api_key: str = None) -> bool:
        """Switch to a different provider at runtime."""
        try:
            old_provider = self.provider_name
            self.__init__(provider, model, api_key)

            if self.is_available():
                print(f"✅ Switched from {old_provider} to {provider}")
                return True
            else:
                print(f"❌ Failed to switch to {provider}")
                return False

        except Exception as e:
            print(f"❌ Error switching provider: {e}")
            return False
