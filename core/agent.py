import time
from typing import List, Dict, Any, Optional
from utils.adb import ADBWrapper
from config import AgentConfig
from .message_builders.base import BaseMessageBuilder
from .model_clients.base import BaseModelClient
from .response_parsers.base import BaseResponseParser
from .executor.action_executor import ActionExecutor


class MobileAgent:
    
    def __init__(
        self,
        config: AgentConfig,
        message_builder: BaseMessageBuilder,
        model_client: BaseModelClient,
        response_parser: BaseResponseParser,
        adb: Optional[ADBWrapper] = None
    ):
        self.config = config
        self.message_builder = message_builder
        self.model_client = model_client
        self.response_parser = response_parser
        
        self.adb = adb or ADBWrapper(device_id=config.device_id)
        self.executor = ActionExecutor(
            self.adb, 
            model_type=config.model_type,
            use_adbkeyboard=config.use_adbkeyboard
        )
        
        self.history: List[Dict[str, Any]] = []
    
    def run(self, instruction: str, max_steps: Optional[int] = None) -> List[Dict[str, Any]]:
        max_steps = max_steps or self.config.max_steps
        self.history = []
        
        print(f"\n{'='*70}")
        print(f"🚀 Task: {instruction}")
        print(f"{'='*70}\n")
        
        for step in range(max_steps):
            print(f"\n{'─'*70}")
            print(f"📍 Step {step + 1}")
            print(f"{'─'*70}")
            
            if self._check_duplicate_actions():
                print("⚠️  Detected duplicate actions, stopping...")
                break
            
            screenshot_path = self.adb.capture_screenshot(self.config.screenshot_dir)
            print(f"📸 Screenshot: {screenshot_path}")
            
            messages = self.message_builder.build_messages(
                instruction=instruction,
                current_screenshot=screenshot_path,
                history=self.history
            )
            
            print("🤖 Requesting model inference...")
            extra_body = {
                "mm_processor_kwargs": {
                    "min_pixels": self.config.min_pixels,
                    "max_pixels": self.config.max_pixels
                }
            }
            response = self.model_client.chat(
                messages=messages,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
                extra_body=extra_body,
                **self.config.model_kwargs
            )
            
            parsed = self.response_parser.parse(response)
            
            print(f"\n💭 Thought: {parsed.thought}")
            print(f"📝 Action: {parsed.subtask}")
            print(f"⚙️  Tool Call: {parsed.action}")
            
            if parsed.action.get("arguments", {}).get("action") == "terminate":
                print("\n✅ Task completed!")
                self._add_to_history(screenshot_path, parsed)
                break
            
            try:
                result = self.executor.execute(parsed.action)
                print(f"✓ Executed: {result}")
            except Exception as e:
                print(f"❌ Execution failed: {e}")
                break
            
            self._add_to_history(screenshot_path, parsed)
            
            delay = self.config.first_step_delay if step == 0 else self.config.step_delay
            if delay > 0:
                print(f"⏱️  Waiting {delay}s...")
            time.sleep(delay)
        
        print(f"\n{'='*70}")
        print(f"🏁 Task finished after {len(self.history)} steps")
        print(f"{'='*70}\n")
        
        return self.history
    
    def _add_to_history(self, screenshot: str, parsed):
        self.history.append({
            "screenshot": screenshot,
            "thought": parsed.thought,
            "subtask": parsed.subtask,
            "action": parsed.action,
            "summary": parsed.summary
        })
    
    def _check_duplicate_actions(self, window: int = 5) -> bool:
        if len(self.history) < window:
            return False
        
        recent_actions = [h.get("action") for h in self.history[-window:]]
        
        if all(str(action) == str(recent_actions[0]) for action in recent_actions):
            return True
        
        return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
    
    def clear_history(self):
        self.history = []
