---
name: mobizen-gui
description: Helps users set up and run MobiZen-GUI to perform mobile-use tasks — automating Android phone operations via natural language. Use when the user wants to control a phone, execute mobile-use tasks, install/configure MobiZen-GUI, deploy MobiZen-GUI-4B model, or customize the agent's input/output. Triggers on keywords like phone task, mobile-use, mobile automation, Android control, MobiZen, ADB, deploy model, run agent, configure model.
---

# MobiZen-GUI

VLM-based mobile automation framework — control Android devices via natural language.

Repo: https://github.com/alibaba/MobiZen-GUI

---

## 1. Environment Setup

### 1.1 Install ADB

```bash
# macOS
brew install android-platform-tools
# Linux
sudo apt-get install android-tools-adb
# Windows: download from https://developer.android.com/studio/releases/platform-tools
adb version  # verify
```

### 1.2 Connect Device & Install ADBKeyboard

```bash
adb devices                    # USB; or: adb tcpip 5555 && adb connect <ip>:5555
adb install ADBKeyboard.apk    # download from https://github.com/senzhk/ADBKeyBoard
```
Then on device: Settings → System → Languages & Input → Virtual Keyboard → Enable ADBKeyboard.

### 1.3 Install Project

```bash
git clone https://github.com/alibaba/MobiZen-GUI.git && cd MobiZen-GUI
pip install -r requirements.txt   # openai, pillow, pyyaml
```

---

## 2. Quick Start (Config Only, No Code Changes)

Copy example config:

```bash
cp config_example.yaml my_config.yaml
```

Only **3 fields** need to be configured — `api_key`, `base_url`, `model_name`:

```yaml
api_key: "your-api-key-here"
base_url: "https://api.openai.com/v1"   # your model endpoint
model_name: "gpt-4o"                    # model identifier
```

**How to set these 3 fields**: When the user asks to run a phone task but hasn't configured yet, the AI should **ask the user to provide** `api_key`, `base_url`, and `model_name`, then write them into `my_config.yaml`. The user can also manually edit the file. Any **OpenAI-compatible** API works.

Provider examples:

```yaml
# OpenAI
base_url: "https://api.openai.com/v1"
api_key: "sk-..."
model_name: "gpt-4o"

# DeepSeek / Moonshot / Zhipu AI etc.
base_url: "https://api.deepseek.com/v1"
api_key: "your-key"
model_name: "deepseek-chat"

# Ollama (local)
base_url: "http://localhost:11434/v1"
api_key: "dummy"
model_name: "llava"
```

Run:

```bash
python main.py --config my_config.yaml --instruction "打开微信并发送消息"
```

---

## 3. Configuration Reference

| Field | Default | Description |
|-------|---------|-------------|
| `device_id` | `null` (auto) | ADB device; null = first available |
| `api_key` | `""` | Model API key |
| `base_url` | `null` | Model API endpoint |
| `model_name` | `"gpt-4o"` | Model identifier |
| `model_type` | `"qwen3vl"` | Coordinate system (999x999 virtual space) |
| `max_steps` | `25` | Max execution steps |
| `step_delay` | `2.0` | Delay between steps (seconds) |
| `first_step_delay` | `4.0` | Delay after first step |
| `temperature` | `0.1` | Sampling temperature |
| `top_p` | `0.001` | Top-p sampling |
| `max_tokens` | `1024` | Max output tokens |
| `timeout` | `60` | Request timeout (seconds) |
| `use_adbkeyboard` | `true` | Chinese text input via ADBKeyboard |
| `screenshot_dir` | `"./screenshots"` | Screenshot save directory |

---

## 4. Advanced: Deploy MobiZen-GUI-4B Locally

For best results on Chinese mobile tasks, deploy the dedicated 4B model.

### 4.1 Download Model

```bash
pip install -U huggingface_hub
# China mirror (optional)
export HF_ENDPOINT=https://hf-mirror.com
hf download alibabagroup/MobiZen-GUI-4B --local-dir ./MobiZen-GUI-4B
```

Alternatively from ModelScope: https://modelscope.cn/models/GUIAgent/MobiZen-GUI-4B

### 4.2 Serve with vLLM

```bash
pip install vllm==0.11.0
vllm serve ./MobiZen-GUI-4B --host 0.0.0.0 --port 8000 --trust-remote-code
```

### 4.3 Point Config to Local Model

```yaml
api_key: "dummy"
base_url: "http://localhost:8000/v1"
model_name: "MobiZen-GUI-4B"
model_type: "qwen3vl"
```

Then run as usual: `python main.py --config my_config.yaml --instruction "..."`

---

## 5. Customization (Requires Code Changes)

The framework uses a plugin architecture — three components can be swapped via config class paths:

| Component | Role | Base Class | Default Implementation |
|-----------|------|-----------|------------------------|
| **MessageBuilder** | Builds prompt + screenshot for model | `core.message_builders.base.BaseMessageBuilder` | `core.message_builders.qwen.QwenMessageBuilder` |
| **ModelClient** | Calls the model API | `core.model_clients.base.BaseModelClient` | `core.model_clients.openai.OpenAIClient` |
| **ResponseParser** | Parses model output → action | `core.response_parsers.base.BaseResponseParser` | `core.response_parsers.qwen.QwenResponseParser` |

### 5.1 Custom Model Client

For non-OpenAI-compatible APIs:

```python
# core/model_clients/my_client.py
from .base import BaseModelClient

class MyClient(BaseModelClient):
    def __init__(self, api_key: str, base_url: str = None, model: str = "", timeout: int = 60):
        pass  # init your client

    def chat(self, messages, **kwargs):
        pass  # must return obj with .choices[0].message.content
```

Config:
```yaml
model_client_class: "core.model_clients.my_client.MyClient"
model_client_kwargs: {}  # extra kwargs passed to __init__
```

### 5.2 Custom Message Builder

To change the system prompt or how screenshots/history are formatted:

```python
# core/message_builders/my_builder.py
from .base import BaseMessageBuilder
from utils.image import image_to_data_url

class MyBuilder(BaseMessageBuilder):
    def build_system_prompt(self, **kwargs) -> str:
        return "your system prompt"

    def build_messages(self, instruction, current_screenshot, history, **kwargs):
        return [{"role": "system", "content": [...]}, {"role": "user", "content": [...]}]
```

Config:
```yaml
message_builder_class: "core.message_builders.my_builder.MyBuilder"
```

### 5.3 Custom Response Parser

To parse a different model output format:

```python
# core/response_parsers/my_parser.py
from .base import BaseResponseParser, ParsedResponse

class MyParser(BaseResponseParser):
    def parse(self, response) -> ParsedResponse:
        content = response.choices[0].message.content
        # parse content into structured fields
        return ParsedResponse(
            thought="...",
            summary="...",
            action={"arguments": {"action": "click", "coordinate": [x, y]}},
            subtask="..."
        )
```

**Action dict format**: `{"arguments": {"action": "<type>", ...}}` — supported types: `click`, `long_press`, `swipe`, `type`, `system_button`, `wait`, `terminate`.

Config:
```yaml
response_parser_class: "core.response_parsers.my_parser.MyParser"
```

### 5.4 Add New Action Type

1. Add `_execute_<action>(self, args)` method in `core/executor/action_executor.py`
2. Add dispatch branch in `ActionExecutor.execute()`
3. Update system prompt in `QwenMessageBuilder.build_system_prompt()`

---

## 6. Troubleshooting

- **Device not found**: Run `adb devices` — check USB/wireless connection
- **ADBKeyboard not working**: Ensure enabled in device settings; test: `adb shell am broadcast -a ADB_INPUT_TEXT --es msg "test"`
- **Model connection error**: Verify `base_url` + `api_key`; check network
- **Coordinate mismatch**: Ensure `model_type` matches your model; check screen size: `adb shell wm size`
- **Duplicate action loop**: Agent auto-stops after 5 identical actions; may indicate model confusion
