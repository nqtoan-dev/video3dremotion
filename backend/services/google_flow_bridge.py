import os
import pathlib
import shutil
import subprocess
from backend.models import ShotItem

ASSETS_DIR = pathlib.Path("./renderer/public/assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


class GoogleFlowBridge:
    """
    Cầu nối tự động hóa Google Labs Flow (1.000 credits/tháng) qua gflow-cli.
    Bảo vệ túi tiền credit của bạn theo nguyên tắc:
      1. Ảnh Storyboard (First Frame) -> Dùng Nano Banana / Imagen 4 (0 CREDIT).
      2. Chỉ khi bạn bấm Duyệt Ảnh -> Mới gọi Veo 3 Fast (20 credits) ở chế độ Image-to-Video (i2v).
    """

    @staticmethod
    def is_simulation_mode() -> bool:
        return os.getenv("FLOW_SIMULATION_MODE", "false").lower() == "true" or shutil.which("gflow") is None

    @staticmethod
    def check_credits() -> dict:
        if GoogleFlowBridge.is_simulation_mode():
            return {
                "mode": "simulation",
                "monthly_credits_remaining": 1000,
                "daily_free_credits": 50,
                "message": "Chế độ mô phỏng (Chưa tìm thấy gflow-cli hoặc đang bật FLOW_SIMULATION_MODE)",
            }
        res = subprocess.run(["gflow", "credits", "user"], capture_output=True, text=True, check=False)
        return {"mode": "live_google_flow", "raw_output": res.stdout.strip()}

    @staticmethod
    def generate_free_storyboard_frame(project_id: str, shot: ShotItem) -> str:
        out_dir = ASSETS_DIR / project_id / "frames"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{shot.shot_id}_first_frame.png"

        full_prompt = (
            f"{shot.veo_image_prompt}, shot on ARRI Alexa 65, {shot.camera.focal_length} lens, "
            f"{shot.camera.aperture}, {shot.camera.lighting_mood}, 2.39:1 CinemaScope anamorphic framing, "
            f"cinematic color grading, photorealistic, clean composition, text-free, no watermarks"
        )
        if shot.user_feedback:
            full_prompt += f", director revision: {shot.user_feedback}"

        if GoogleFlowBridge.is_simulation_mode():
            out_file.write_text(f"SIMULATED_FRAME: {full_prompt}", encoding="utf-8")
            return f"/assets/{project_id}/frames/{shot.shot_id}_first_frame.png"

        cmd = [
            "gflow", "image", "t2i",
            full_prompt,
            "--aspect", "16:9",
            "--output", str(out_file),
        ]
        subprocess.run(cmd, check=True)
        return f"/assets/{project_id}/frames/{shot.shot_id}_first_frame.png"

    @staticmethod
    def generate_veo3_shot_video(
        project_id: str,
        shot: ShotItem,
        model_tier: str = "veo-3-fast",
    ) -> str:
        out_dir = ASSETS_DIR / project_id / "clips"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_video = out_dir / f"{shot.shot_id}_veo3.mp4"

        local_frame = ASSETS_DIR / project_id / "frames" / f"{shot.shot_id}_first_frame.png"

        motion_prompt = (
            f"{shot.veo_motion_prompt}. Camera movement: {shot.camera.camera_motion}. "
            f"Keep consistent lighting ({shot.camera.lighting_mood}) and natural 24fps motion."
        )
        if shot.user_feedback:
            motion_prompt += f" Director note: {shot.user_feedback}."

        if GoogleFlowBridge.is_simulation_mode():
            out_video.write_text(f"SIMULATED_VEO3_CLIP ({model_tier}): {motion_prompt}", encoding="utf-8")
            return f"/assets/{project_id}/clips/{shot.shot_id}_veo3.mp4"

        cmd = [
            "gflow", "video", "i2v",
            "--image", str(local_frame.resolve()),
            "--prompt", motion_prompt,
            "--model", model_tier,
            "--aspect", "16:9",
            "--output", str(out_video),
        ]
        subprocess.run(cmd, check=True)
        return f"/assets/{project_id}/clips/{shot.shot_id}_veo3.mp4"
