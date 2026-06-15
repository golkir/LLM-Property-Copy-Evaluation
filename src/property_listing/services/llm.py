import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from pydantic import BaseModel
import anthropic
from google import genai
from google.genai import types

class LLMProviderService(ABC):
    @abstractmethod
    def generate_structured(self, prompt: str, system_instruction: str, response_schema: Type[BaseModel]) -> Dict[str, Any]:
        pass

class AnthropicService(LLMProviderService):
    def __init__(self, model_name: str = "claude-sonnet-4-6"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing 'ANTHROPIC_API_KEY' environment variable.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name

    def generate_structured(self, prompt: str, system_instruction: str, response_schema: Type[BaseModel]) -> Dict[str, Any]:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1500,
            temperature=0.0,
            system=system_instruction,
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": f"submit_{response_schema.__name__.lower()}",
                "description": f"Outputs structured schema for {response_schema.__name__}",
                "input_schema": response_schema.model_json_schema()
            }],
            tool_choice={"type": "tool", "name": f"submit_{response_schema.__name__.lower()}"}
        )
        tool_block = [b for b in response.content if b.type == "tool_use"][0]
        return tool_block.input

class GeminiService(LLMProviderService):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing 'GEMINI_API_KEY' environment variable.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_structured(self, prompt: str, system_instruction: str, response_schema: Type[BaseModel]) -> Dict[str, Any]:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        import json
        return json.loads(response.text)