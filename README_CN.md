# <p align="center"><b>MobiZen-GUI</b></p>

<p align="center">
🌐 <a href="https://huggingface.co/alibabagroup/MobiZen-GUI-4B">模型（Hugging Face）</a>  |
🌐 <a href="https://modelscope.cn/models/GUIAgent/MobiZen-GUI-4B">模型（ModelScope）</a>  |
💻 <a href="./demo/">演示</a>  |
📄 <a href="https://github.com/alibaba">中文轨迹数据</a>
</p>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README_CN.md">简体中文</a>
</p>

**MobiZen-GUI** 是一套可扩展的移动端自动化框架，借助视觉-语言模型 (VLM) 通过自然语言指令操控 Android 设备。名称 “MobiZen” 结合了 **Mobile** 与 **禅 (Zen)**，寓意“智能、无感”的移动自动化体验。

MobiZen-GUI 采用大规模、精挑细选的 **中文移动 GUI 交互数据集** 进行训练，覆盖电商、出行、社交、金融等场景的数十万真实 App 会话。每条数据均包含截图、触控轨迹及中文指令，使得智能体对中文 UI 规范与业务流程有深刻理解。

MobiZen-GUI 的目标是让 **移动 GUI 智能体** 的开发与部署更加快捷、易用。它带来了：

- **40 亿参数的智能体模型**：可完全在本地台式机或笔记本电脑上运行。  
- **仅依赖单图像加历史动作，执行速度快**：仅依赖单张当前图像加历史动作，无需额外信息，执行速度快。
- **即插即用的推理套件**：自动处理 ADB 连接并安装所有依赖库。

## 应用演示

- **指令**：打开12306，帮我订一张本周六早上八点零八分从济南出发到上海的高铁票，只看高铁和动车, 预定二等座
  **[点击查看演示视频](./demo/video_1_compressed.mp4)**

- **指令**：打开哔哩哔哩，开启睡眠提醒  
  **[点击查看演示视频](./demo/video_2_compressed.mp4)**

- **指令**：  
  打开小红书，在"我"的页面里 查看关注列表，并把关注列表的第三个人取消关注；然后回到"首页"的发现页面，搜索"派大星"然后进入"用户"tab，关注第二个账号；最后回到手机主页面，在拼多多里面搜 索"儿童成长牛奶"并查看第一个商品的用户评价，然后回到手机主页面 
  **[点击查看演示视频](./demo/video_3_compressed.mp4)**

- **指令**：打开计算器，计算5.5535*3.33
  **[点击查看演示视频](./demo/video_4_compressed.mp4)**

- **指令**：去飞猪查询2月27日去，3月4日回，广州到莫斯科的往返机票, 无需购买
  **[点击查看演示视频](./demo/video_5_compressed.mp4)**

---

## 运行必备

### 1. 安装 ADB（Android Debug Bridge）

**macOS**
```bash
brew install android-platform-tools
```

**Linux**
```bash
sudo apt-get install android-tools-adb
```

**Windows**  
从 [Android Developer Site](https://developer.android.com/studio/releases/platform-tools) 下载并解压。

验证安装：
```bash
adb version
```

### 2. 在测试设备上安装 ADBKeyboard

文本输入（尤其是中文）需使用 ADBKeyboard。

1. 下载 [ADBKeyboard.apk](https://github.com/senzhk/ADBKeyBoard)  
2. 安装到设备：
   ```bash
   adb install ADBKeyboard.apk
   ```
3. 在手机设置中启用：设置 → 系统 → 语言和输入法 → 虚拟键盘 → 开启 ADBKeyboard

### 3. 连接设备

**USB 连接**
```bash
adb devices
```

**无线连接**
```bash
adb tcpip 5555
adb connect <device-ip>:5555
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/MobiZen-GUI.git
cd MobiZen-GUI
```

### 2. 安装依赖

**推荐：使用 uv**
```bash
uv venv
source .venv/bin/activate        # Windows 用 .venv\Scripts\activate
uv pip install -r requirements.txt
```

**或使用 pip**
```bash
pip install -r requirements.txt
```

### 3. 配置智能体

复制示例配置并修改：

```bash
cp config_example.yaml my_config.yaml
```

编辑 `my_config.yaml`：

```yaml
device_id: null                  # 为空表示自动选择首个设备
api_key: "your-api-key-here"
base_url: "https://api.openai.com/v1"
model_name: "gpt-4o"
model_type: "qwen3vl"
use_adbkeyboard: true
```

### 4. 运行智能体

```bash
python main.py --config my_config.yaml --instruction "打开小红书，找到 John 的聊天，发送 'Hello'"
```

---

## 模型选择

### 方案一：使用 **MobiZen-GUI-4B**（推荐）

我们提供专为移动自动化微调的 **MobiZen-GUI-4B** 预训练模型。**注意：部署MobiZen-GUI-4B时vLLM版本要求：vllm==0.11.0**

**下载模型**
```bash
pip install -U huggingface_hub
export HF_ENDPOINT=https://hf-mirror.com
hf download alibabagroup/MobiZen-GUI-4B --local-dir .
```

**使用 vLLM 部署**

```bash
pip install vllm==0.11.0

vllm serve /path/to/MobiZen-GUI-4B \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code
```

**配置文件修改**
```yaml
base_url: "http://localhost:8000/v1"
model_name: "MobiZen-GUI-4B"
model_type: "qwen3vl"
```

### 方案二：使用 OpenAI 兼容模型

MobiZen-GUI 支持 **任何遵循 OpenAI API 协议** 的模型，例如：

- **OpenAI 官方**：GPT-4o、GPT-4o-mini 等  
- **云服务商**：Azure OpenAI、AWS Bedrock（兼容 OpenAI）  
- **本地部署**：vLLM、Ollama、LM Studio、Text Generation WebUI（OpenAI 模式）  
- **其他厂商**：DeepSeek、Moonshot、智谱等  

示例配置：

```yaml
# OpenAI
base_url: "https://api.openai.com/v1"
api_key: "sk-..."
model_name: "gpt-4o"

# Azure OpenAI
base_url: "https://your-resource.openai.azure.com/openai/deployments/your-deployment"
api_key: "your-azure-key"
model_name: "gpt-4o"

# vLLM (本地/远程)
base_url: "http://localhost:8000/v1"
api_key: "dummy"
model_name: "your-model-name"

# Ollama
base_url: "http://localhost:11434/v1"
api_key: "dummy"
model_name: "llava"
```

### 方案三：自定义模型客户端

若模型不支持 OpenAI 协议，可自行实现客户端：

```python
from core.model_clients.base import BaseModelClient

class MyModelClient(BaseModelClient):
    def chat(self, messages, **kwargs):
        # 自定义调用逻辑
        pass
```

在配置中指定：
```yaml
model_client_class: "my_module.MyModelClient"
model_client_kwargs:
  model_path: "/path/to/model"
```

---

## 配置说明

### 基本参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `device_id` | ADB 设备 ID（留空自动检测首个设备） | `null` |
| `api_key` | 模型服务的 API Key | 必填 |
| `base_url` | 模型服务接口地址 | 必填 |
| `model_name` | 模型名称 | 必填 |
| `model_type` | 坐标转换类型（`qwen3vl` 或 `qwen25vl`） | `qwen3vl` |
| `use_adbkeyboard` | 是否使用 ADBKeyboard 输入文本 | `true` |

### 运行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_steps` | 单任务最大步数 | `25` |
| `step_delay` | 每步操作后等待时间（秒） | `2.0` |
| `first_step_delay` | 第一步操作后的等待时间（秒） | `4.0` |
| `screenshot_dir` | 截图保存目录 | `./screenshots` |

### 模型推理参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `temperature` | 采样温度 | `0.1` |
| `top_p` | top-p 采样阈值 | `0.001` |
| `max_tokens` | 生成的最长 token 数 | `1024` |
| `timeout` | 请求超时（秒） | `60` |

完整示例见 `config_example.yaml` / `config_example.json`。

---

## 使用示例

### 命令行

```bash
# 打开应用
python main.py --config my_config.yaml --instruction "打开知乎"

# 执行复杂任务
python main.py --config my_config.yaml --instruction "在高德地图搜索附近的餐馆"

# 多步骤任务
python main.py --config my_config.yaml --instruction "打开小红书，找到 John 的聊天，发送 'Hello'"
```

### Python API

```python
from config import AgentConfig
from core.agent import MobileAgent

# 从文件加载配置
config = AgentConfig.from_file("my_config.yaml")

# 创建智能体
agent = MobileAgent(
    config=config,
    message_builder=config.create_message_builder(),
    model_client=config.create_model_client(),
    response_parser=config.create_response_parser()
)

# 执行任务
history = agent.run("打开设置，开启 WiFi")

# 查看执行历史
for step in history:
    print(f"步骤: {step['subtask']}")
    print(f"动作: {step['action']}")
```

---

## 支持的操作

- **click**：点击指定坐标  
- **long_press**：长按  
- **swipe**：滑动  
- **type**：输入文本（配合 ADBKeyboard 支持中文）  
- **system_button**：按返回 / 首页 / Enter / 菜单等系统按键  
- **wait**：等待指定时长  
- **terminate**：结束任务执行  

---

## 常见问题

**设备无法识别**

```bash
adb devices
# 如列表为空，检查 USB 连接或无线连接是否正常
```

**ADBKeyboard 无法输入**

1. 确认已安装并在系统设置中启用 ADBKeyboard  
2. 测试命令：  
   ```bash
   adb shell am broadcast -a ADB_INPUT_TEXT --es msg "test"
   ```

**模型连接失败**

- 检查 `base_url`、`api_key` 是否正确  
- 确认网络连通性  
- 保证模型服务端口可访问  

**坐标映射不准确**

- 确认 `model_type` 与模型一致（`qwen3vl` 或 `qwen25vl`）  
- 查看设备分辨率：`adb shell wm size`

## ToDo

- ✅ 发布 GUI 模型 [MobiZen-GUI-4B](https://huggingface.co/alibabagroup/MobiZen-GUI-4B)
- ☐ 发布高质量的中文轨迹训练/评测语料库及对应的评测代码
- ☐ 为热门的 OpenClaw 项目编写 skill.md
- ☐ 支持更多 GUI 模型，例如 MAI-UI、Qwen 3.5、GeLab-Zero

## 许可证

Apache License 2.0