from typing import Dict, Any
from utils.adb import ADBWrapper


class ActionExecutor:
    
    def __init__(self, adb: ADBWrapper, model_type: str = "qwen3vl", use_adbkeyboard: bool = True):
        self.adb = adb
        self.model_type = model_type
        self.use_adbkeyboard = use_adbkeyboard
        self.screen_width, self.screen_height = adb.get_screen_size()
    
    def execute(self, action: Dict[str, Any]) -> str:
        if "arguments" not in action:
            raise ValueError("Action must have 'arguments' field")
        
        args = action["arguments"]
        action_type = args.get("action", "")
        
        if action_type == "click":
            return self._execute_click(args)
        elif action_type == "long_press":
            return self._execute_long_press(args)
        elif action_type == "swipe":
            return self._execute_swipe(args)
        elif action_type == "type":
            return self._execute_type(args)
        elif action_type == "system_button":
            return self._execute_system_button(args)
        elif action_type == "wait":
            return self._execute_wait(args)
        elif action_type == "terminate":
            return "Task terminated"
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    def _transform_coordinates(self, x: int, y: int) -> tuple[int, int]:
        if self.model_type == "qwen3vl":
            real_x = int(x * self.screen_width / 999)
            real_y = int(y * self.screen_height / 999)
            return real_x, real_y
        elif self.model_type == "qwen25vl":
            raise NotImplementedError("qwen25vl coordinate transformation not implemented")
        else:
            return x, y
    
    def _execute_click(self, args: Dict[str, Any]) -> str:
        coordinate = args.get("coordinate", [])
        if len(coordinate) != 2:
            raise ValueError(f"Invalid coordinate: {coordinate}")
        
        x, y = self._transform_coordinates(int(coordinate[0]), int(coordinate[1]))
        self.adb.tap(x, y)
        return f"Clicked at ({x}, {y})"
    
    def _execute_long_press(self, args: Dict[str, Any]) -> str:
        coordinate = args.get("coordinate", [])
        duration = args.get("time", 1) * 1000
        if len(coordinate) != 2:
            raise ValueError(f"Invalid coordinate: {coordinate}")
        
        x, y = self._transform_coordinates(int(coordinate[0]), int(coordinate[1]))
        self.adb.swipe(x, y, x, y, int(duration))
        return f"Long pressed at ({x}, {y}) for {duration}ms"
    
    def _execute_swipe(self, args: Dict[str, Any]) -> str:
        coordinate = args.get("coordinate", [])
        coordinate2 = args.get("coordinate2", [])
        
        if len(coordinate) != 2 or len(coordinate2) != 2:
            raise ValueError(f"Invalid coordinates: {coordinate}, {coordinate2}")
        
        x1, y1 = self._transform_coordinates(int(coordinate[0]), int(coordinate[1]))
        x2, y2 = self._transform_coordinates(int(coordinate2[0]), int(coordinate2[1]))
        
        self.adb.swipe(x1, y1, x2, y2)
        return f"Swiped from ({x1}, {y1}) to ({x2}, {y2})"
    
    def _execute_type(self, args: Dict[str, Any]) -> str:
        text = args.get("text", "")
        if not text:
            raise ValueError("Text cannot be empty for type action")
        
        self.adb.text(text, use_adbkeyboard=self.use_adbkeyboard)
        method = "ADBKeyboard" if self.use_adbkeyboard else "input text"
        return f"Typed: {text} (via {method})"
    
    def _execute_system_button(self, args: Dict[str, Any]) -> str:
        button = args.get("button", "")
        
        if button == "Back":
            self.adb.back()
            return "Pressed Back button"
        elif button == "Home":
            self.adb.home()
            return "Pressed Home button"
        elif button == "Enter":
            self.adb.enter()
            return "Pressed Enter button"
        elif button == "Menu":
            self.adb.keyevent(82)
            return "Pressed Menu button"
        else:
            raise ValueError(f"Unknown system button: {button}")
    
    def _execute_wait(self, args: Dict[str, Any]) -> str:
        import time
        duration = args.get("time", 1)
        time.sleep(duration)
        return f"Waited for {duration} seconds"
