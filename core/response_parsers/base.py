from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedResponse:
    thought: str
    summary: str
    action: dict
    subtask: str = ""


class BaseResponseParser(ABC):
    
    @abstractmethod
    def parse(self, response: Any) -> ParsedResponse:
        pass
