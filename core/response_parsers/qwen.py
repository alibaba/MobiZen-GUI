import re
import json
from typing import Any
from .base import BaseResponseParser, ParsedResponse


class QwenResponseParser(BaseResponseParser):
    
    def __init__(self, model_type: str = "qwen3vl"):
        self.model_type = model_type
    
    def parse(self, response: Any) -> ParsedResponse:
        try:
            content = response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"Failed to extract content from response: {e}")
        
        if self.model_type == "qwen3vl":
            return self._parse_qwen3vl(content)
        else:
            raise NotImplementedError(f"Model type {self.model_type} not supported")
    
    def _parse_qwen3vl(self, content: str) -> ParsedResponse:
        summary = ''
        thought = ''
        pred_subtask = ''
        action = {}
        
        try:
            thought = content.split('\nAction')[0].replace('Thought', '').replace(':', '').replace('：', '').strip()
        except:
            pass
        
        try:
            pred_subtask = content.split('\nAction')[-1].replace(':', '').replace('：', '').replace('\"', '').split('\n<tool_call>')[0].strip('"')
        except:
            pass
        
        try:
            action_str = content.split('<tool_call>')[1].split('</tool_call>')[0].strip().replace("'", '"')
            pattern = r'\{.*?\}}'
            result = re.search(pattern, action_str, re.DOTALL)
            if result:
                action_str = result.group()
            action = json.loads(action_str)
        except Exception as e:
            print(f"Failed to parse action: {e}")
            action = {}
        
        return ParsedResponse(
            thought=thought,
            summary=summary,
            action=action,
            subtask=pred_subtask
        )
