from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseMessageBuilder(ABC):
    
    @abstractmethod
    def build_system_prompt(self, **kwargs) -> str:
        pass
    
    @abstractmethod
    def build_messages(
        self,
        instruction: str,
        current_screenshot: str,
        history: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        pass
