from typing import List, Dict, Any
from .base import BaseMessageBuilder
from utils.image import image_to_data_url


class QwenMessageBuilder(BaseMessageBuilder):
    
    def __init__(self, model_type: str = "qwen3vl", max_pixels: int = 1280 * 32 * 32):
        self.model_type = model_type
        self.max_pixels = max_pixels
    
    def build_system_prompt(self, **kwargs) -> str:
        if self.model_type == "qwen3vl":
            return """\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>\n{\"type\": \"function\", \"function\": {\"name\": \"mobile_use\", \"description\": \"Use a touchscreen to interact with a mobile device, and take screenshots.\\n* This is an interface to a mobile device with touchscreen. You can perform actions like clicking, typing, swiping, etc.\\n* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.\\n* The screen's resolution is 999x999.\\n* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked.\", \"parameters\": {\"properties\": {\"action\": {\"description\": \"The action to perform. The available actions are:\\n* `click`: Click the point on the screen with coordinate (x, y).\\n* `long_press`: Press the point on the screen with coordinate (x, y) for specified seconds.\\n* `swipe`: Swipe from the starting point with coordinate (x, y) to the end point with coordinates2 (x2, y2).\\n* `type`: Input the specified text into the activated input box.\\n* `answer`: Output the answer.\\n* `system_button`: Press the system button.\\n* `wait`: Wait specified seconds for the change to happen.\\n* `terminate`: Terminate the current task and report its completion status.\", \"enum\": [\"click\", \"long_press\", \"swipe\", \"type\", \"answer\", \"system_button\", \"wait\", \"terminate\"], \"type\": \"string\"}, \"coordinate\": {\"description\": \"(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=click`, `action=long_press`, and `action=swipe`.\", \"type\": \"array\"}, \"coordinate2\": {\"description\": \"(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=swipe`.\", \"type\": \"array\"}, \"text\": {\"description\": \"Required only by `action=type` and `action=answer`.\", \"type\": \"string\"}, \"time\": {\"description\": \"The seconds to wait. Required only by `action=long_press` and `action=wait`.\", \"type\": \"number\"}, \"button\": {\"description\": \"Back means returning to the previous interface, Home means returning to the desktop, Menu means opening the application background menu, and Enter means pressing the enter. Required only by `action=system_button`\", \"enum\": [\"Back\", \"Home\", \"Menu\", \"Enter\"], \"type\": \"string\"}, \"status\": {\"description\": \"The status of the task. Required only by `action=terminate`.\", \"type\": \"string\", \"enum\": [\"success\", \"failure\"]}}, \"required\": [\"action\"], \"type\": \"object\"}}}\n</tools>\nFor each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call>\n\n# Response format\n\nResponse format for every step:\n1) Thought: one concise sentence explaining the next move (no multi-step reasoning).\n2) Action: a short imperative describing what to do in the UI.\n3) A single <tool_call>...</tool_call> block containing only the JSON: {\"name\": <function-name>, \"arguments\": <args-json-object>}.\n\nRules:\n- Output exactly in the order: Thought, Action, <tool_call>.\n- Be brief: one sentence for Thought, one for Action.\n- Do not output anything else outside those three parts.\n- If finishing, use action=terminate in the tool call."""
        else:
            raise NotImplementedError(f"Model type {self.model_type} not supported")
    
    def build_messages(
        self,
        instruction: str,
        current_screenshot: str,
        history: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        
        stage2_history = ''
        for idx, hist in enumerate(history):
            subtask = hist.get('subtask', '')
            stage2_history += f'Step {idx + 1}: {subtask.replace(chr(10), "").replace(chr(34), "")}\n'
        
        if len(history) == 0:
            user_query = f"The user query: {instruction}.\n"
        else:
            user_query = f"The user query: {instruction}.\nTask progress (You have done the following operation on the current device): {stage2_history}"
        
        image_data_url = image_to_data_url(current_screenshot)
        
        messages = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": self.build_system_prompt()},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_query},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        },
                    },
                ],
            }
        ]
        
        return messages
