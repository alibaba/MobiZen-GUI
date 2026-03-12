import json
import importlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class AgentConfig:
    device_id: Optional[str] = None
    
    api_key: str = ""
    base_url: Optional[str] = None
    model_name: str = "gpt-4o"
    
    model_type: str = "qwen3vl"
    min_pixels: int = 1 * 32 * 32
    max_pixels: int = 1280 * 32 * 32
    
    max_steps: int = 25
    screenshot_dir: str = "./screenshots"
    
    step_delay: float = 2.0
    first_step_delay: float = 4.0
    
    use_adbkeyboard: bool = True
    
    temperature: float = 0.1
    top_p: float = 0.001
    max_tokens: int = 1024
    timeout: int = 60
    
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    message_builder_class: str = "core.message_builders.qwen.QwenMessageBuilder"
    message_builder_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    model_client_class: str = "core.model_clients.openai.OpenAIClient"
    model_client_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    response_parser_class: str = "core.response_parsers.qwen.QwenResponseParser"
    response_parser_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AgentConfig":
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})
    
    @classmethod
    def from_json_file(cls, file_path: str) -> "AgentConfig":
        with open(file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_yaml_file(cls, file_path: str) -> "AgentConfig":
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            return cls.from_dict(config_dict)
        except ImportError:
            raise ImportError("PyYAML is required to load YAML config files. Install it with: pip install pyyaml")
    
    @classmethod
    def from_file(cls, file_path: str) -> "AgentConfig":
        path = Path(file_path)
        if path.suffix in ['.yaml', '.yml']:
            return cls.from_yaml_file(file_path)
        elif path.suffix == '.json':
            return cls.from_json_file(file_path)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}. Use .json, .yaml, or .yml")
    
    def instantiate_class(self, class_path: str, kwargs: Dict[str, Any] = None):
        kwargs = kwargs or {}
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(**kwargs)
    
    def create_message_builder(self):
        kwargs = self.message_builder_kwargs.copy()
        if 'model_type' not in kwargs:
            kwargs['model_type'] = self.model_type
        if 'max_pixels' not in kwargs:
            kwargs['max_pixels'] = self.max_pixels
        return self.instantiate_class(self.message_builder_class, kwargs)
    
    def create_model_client(self):
        kwargs = self.model_client_kwargs.copy()
        if 'api_key' not in kwargs:
            kwargs['api_key'] = self.api_key
        if 'base_url' not in kwargs:
            kwargs['base_url'] = self.base_url
        if 'model' not in kwargs:
            kwargs['model'] = self.model_name
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self.instantiate_class(self.model_client_class, kwargs)
    
    def create_response_parser(self):
        kwargs = self.response_parser_kwargs.copy()
        if 'model_type' not in kwargs:
            kwargs['model_type'] = self.model_type
        return self.instantiate_class(self.response_parser_class, kwargs)
