from abc import ABC, abstractmethod
from typing import Any, List, Dict


class BaseModelClient(ABC):
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        pass
