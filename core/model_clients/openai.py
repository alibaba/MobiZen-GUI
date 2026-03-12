from openai import OpenAI
from typing import Any, List, Dict, Optional
from .base import BaseModelClient


class OpenAIClient(BaseModelClient):
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.model = model
        self.timeout = timeout
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response
