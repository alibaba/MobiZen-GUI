import subprocess
import time
import os
from typing import Optional


class ADBWrapper:
    def __init__(self, device_id: Optional[str] = None):
        if device_id is None:
            device_id = self._get_first_device()
        self.device_id = device_id
        self.device_arg = ["-s", device_id] if device_id else []
    
    @staticmethod
    def _get_first_device() -> Optional[str]:
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                if '\tdevice' in line:
                    return line.split('\t')[0]
            return None
        except Exception:
            return None
    
    def _run_command(self, cmd: list, timeout: int = 30) -> str:
        try:
            result = subprocess.run(
                ["adb"] + self.device_arg + cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                raise RuntimeError(f"ADB command failed: {result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"ADB command timed out after {timeout}s")
    
    def connect(self, host_port: str) -> str:
        return self._run_command(["connect", host_port])
    
    def disconnect(self) -> str:
        return self._run_command(["disconnect"])
    
    def capture_screenshot(self, save_path: str) -> str:
        screenshot_path = os.path.join(save_path, f"screenshot_{int(time.time() * 1000)}.png")
        os.makedirs(save_path, exist_ok=True)
        
        temp_path = "/sdcard/screenshot.png"
        self._run_command(["shell", "screencap", "-p", temp_path])
        self._run_command(["pull", temp_path, screenshot_path])
        self._run_command(["shell", "rm", temp_path])
        
        return screenshot_path
    
    def tap(self, x: int, y: int) -> str:
        return self._run_command(["shell", "input", "tap", str(x), str(y)])
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
        return self._run_command([
            "shell", "input", "swipe", 
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
    
    def text(self, text: str, use_adbkeyboard: bool = True) -> str:
        if use_adbkeyboard:
            return self._text_adbkeyboard(text)
        else:
            escaped_text = text.replace(" ", "%s").replace("&", "\\&")
            return self._run_command(["shell", "input", "text", escaped_text])
    
    def _text_adbkeyboard(self, text: str) -> str:
        def preprocess_text_for_adb(text):
            # Escape special characters for adb shell input
            text = text.replace("\n", " ").replace("\t", " ")
            text = text.replace(" ", "\\ ")
            return text
        return self._run_command(["shell", "am", "broadcast", "-a", "ADB_INPUT_TEXT", "--es", "msg", preprocess_text_for_adb(text)])
    
    def keyevent(self, keycode: int) -> str:
        return self._run_command(["shell", "input", "keyevent", str(keycode)])
    
    def back(self) -> str:
        return self.keyevent(4)
    
    def home(self) -> str:
        return self.keyevent(3)
    
    def enter(self) -> str:
        return self.keyevent(66)
    
    def get_screen_size(self) -> tuple[int, int]:
        output = self._run_command(["shell", "wm", "size"])
        size_str = output.split(":")[-1].strip()
        width, height = map(int, size_str.split("x"))
        return width, height
    
    def get_xml(self) -> str:
        temp_path = "/sdcard/window_dump.xml"
        self._run_command(["shell", "uiautomator", "dump", temp_path])
        xml_content = self._run_command(["shell", "cat", temp_path])
        self._run_command(["shell", "rm", temp_path])
        return xml_content
    
    def is_keyboard_shown(self) -> bool:
        output = self._run_command(["shell", "dumpsys", "input_method"])
        return "mInputShown=true" in output
    
    def start_app(self, package: str, activity: str = None) -> str:
        if activity:
            return self._run_command(["shell", "am", "start", "-n", f"{package}/{activity}"])
        return self._run_command(["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])
    
    def stop_app(self, package: str) -> str:
        return self._run_command(["shell", "am", "force-stop", package])
    
    def get_current_activity(self) -> str:
        output = self._run_command(["shell", "dumpsys", "window", "windows"])
        for line in output.split("\n"):
            if "mCurrentFocus" in line or "mFocusedApp" in line:
                return line.strip()
        return ""
