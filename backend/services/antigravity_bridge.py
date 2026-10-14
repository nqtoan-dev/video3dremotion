import json
import os
import pathlib
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional


class AntigravityBridge:
    """
    Tích hợp trực tiếp Google Antigravity CLI (`agy`) làm Nhân AI trung tâm (AI Core).
    Không cần cấu hình GEMINI_API_KEY: sử dụng trực tiếp phiên đăng nhập Google OAuth
    của Antigravity trên máy (`agy auth login` hoặc `~/.gemini/antigravity-cli`).
    """

    @staticmethod
    def find_agy_binary() -> Optional[str]:
        for cmd in ("agy", "agy.exe", "antigravity", "antigravity.exe"):
            found = shutil.which(cmd)
            if found:
                return found
        # Kiểm tra đường dẫn cài đặt mặc định trên Windows 11
        local_app = os.environ.get("LOCALAPPDATA", "")
        user_profile = os.environ.get("USERPROFILE", "")
        candidates = [
            pathlib.Path(local_app) / "Programs" / "Antigravity" / "agy.exe",
            pathlib.Path(user_profile) / ".gemini" / "antigravity-cli" / "bin" / "agy.exe",
            pathlib.Path(user_profile) / "AppData" / "Roaming" / "npm" / "agy.cmd",
        ]
        for c in candidates:
            if c.exists():
                return str(c.resolve())
        return None

    @staticmethod
    def check_status() -> Dict[str, Any]:
        agy_bin = AntigravityBridge.find_agy_binary()
        config_dir = pathlib.Path.home() / ".gemini" / "antigravity-cli"
        has_config = config_dir.exists()

        if not agy_bin:
            return {
                "installed": False,
                "authenticated": False,
                "binary_path": None,
                "message": "Chưa tìm thấy lệnh 'agy' trong PATH. Hãy cài Antigravity CLI hoặc chạy 'agy auth login'.",
            }

        try:
            ver_res = subprocess.run(
                [agy_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            version_str = ver_res.stdout.strip() or ver_res.stderr.strip()
        except Exception as exc:
            version_str = str(exc)

        return {
            "installed": True,
            "authenticated": True,
            "binary_path": agy_bin,
            "config_dir": str(config_dir),
            "has_config": has_config,
            "version": version_str,
            "message": f"Đã kết nối Antigravity CLI ({version_str})",
        }

    @staticmethod
    def launch_interactive_login() -> Dict[str, Any]:
        """
        Mở cửa sổ Terminal trên Windows 11 để chạy `agy auth login` (xác thực OAuth qua trình duyệt Google).
        """
        agy_bin = AntigravityBridge.find_agy_binary() or "agy"
        if os.name == "nt":
            subprocess.Popen(
                f'start "Antigravity OAuth Login" cmd /k "{agy_bin} auth login"',
                shell=True,
            )
            return {
                "status": "launched",
                "command": f"{agy_bin} auth login",
                "message": "Đã bật cửa sổ đăng nhập Antigravity CLI trên máy. Hãy hoàn tất đăng nhập tài khoản Google trên trình duyệt!",
            }
        else:
            subprocess.Popen([agy_bin, "auth", "login"])
            return {
                "status": "launched",
                "command": f"{agy_bin} auth login",
                "message": "Đã kích hoạt lệnh agy auth login.",
            }

    @staticmethod
    def run_director_prompt(user_script: str) -> Optional[List[Dict[str, Any]]]:
        """
        Gọi Antigravity CLI ở chế độ Headless (`agy -p "<prompt>" --mode=plan`)
        để phân tích kịch bản tiếng Việt thành danh sách các cảnh quay (Shots) JSON chuẩn DCI 2K.
        """
        agy_bin = AntigravityBridge.find_agy_binary()
        if not agy_bin:
            return None

        director_prompt = (
            "Bạn là Đạo diễn Điện ảnh chuyên nghiệp. Hãy phân tích kịch bản sau và chia thành các cảnh quay (shots) "
            "chuẩn rạp DCI 2K (2048x1080, CinemaScope 2.39:1, 24fps). "
            "CHỈ TRẢ VỀ MỘT MẢNG JSON HỢP LỆ (không kèm giải thích ngoài JSON) theo mẫu: "
            '[{"title":"TIÊU ĐỀ 3D NGẮN","narration":"Lời bình tiếng Việt","synopsis":"Mô tả cảnh quay tiếng Việt",'
            '"lens":"24mm Anamorphic f/2.8","motion":"Slow Aerial Push-In",'
            '"veo_image_prompt":"Detailed English prompt for Veo 3 First Frame, ARRI Alexa 65, anamorphic lens, Kodak 2383",'
            '"veo_motion_prompt":"English camera and subject motion prompt for Veo 3 i2v",'
            '"colors":["#0f172a","#1e3a5f","#f59e0b"]}]. '
            f"Kịch bản cần phân tích: {user_script}"
        )

        try:
            res = subprocess.run(
                [agy_bin, "-p", director_prompt, "--mode=plan"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=45,
                check=False,
            )
            raw_out = (res.stdout or "") + "\n" + (res.stderr or "")
            # Trích xuất mảng JSON [...] từ kết quả trả về của Antigravity CLI
            match = re.search(r"\[\s*\{.*\}\s*\]", raw_out, flags=re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed
        except Exception as exc:
            print(f"[AntigravityBridge] Lỗi khi gọi agy -p: {exc}")

        return None
