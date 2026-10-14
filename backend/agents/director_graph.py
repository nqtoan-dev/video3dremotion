from typing import List
from backend.models import CameraSpec, CinemaProject, ShotItem, ShotStatus
from backend.services.antigravity_bridge import AntigravityBridge
from backend.services.google_flow_bridge import GoogleFlowBridge


class CinematicDirectorAgent:
    """
    Hệ thống Multi-Agent sử dụng trực tiếp **Antigravity CLI (`agy`)** đã đăng nhập trên máy
    làm Nhân AI trung tâm (Không cần cấu hình API Key):
      1. Gọi `AntigravityBridge.run_director_prompt()` (`agy -p ... --mode=plan`) để bóc tách kịch bản.
      2. Nếu máy chưa mở terminal đăng nhập `agy`, tự động dùng bộ Smart Script Parser nội bộ.
    """

    @staticmethod
    def analyze_and_breakdown_script(project: CinemaProject) -> CinemaProject:
        agy_shots = AntigravityBridge.run_director_prompt(project.user_prompt)
        if agy_shots:
            built_shots: List[ShotItem] = []
            for idx, item in enumerate(agy_shots):
                built_shots.append(
                    ShotItem(
                        shot_id=f"shot_0{idx + 1}",
                        order=idx + 1,
                        duration_seconds=float(item.get("duration", 4.5)),
                        status=ShotStatus.DRAFT,
                        narration_text=item.get("narration", ""),
                        visual_synopsis=item.get("synopsis", item.get("narration", "")),
                        veo_image_prompt=item.get("veo_image_prompt", item.get("veoPrompt", "")),
                        veo_motion_prompt=item.get("veo_motion_prompt", item.get("motionPrompt", "")),
                        camera=CameraSpec(
                            shot_size=item.get("shot_size", "Anamorphic Cinema Shot"),
                            focal_length=item.get("lens", "50mm Anamorphic f/1.8"),
                            aperture="f/1.8",
                            camera_motion=item.get("motion", "Slow Dolly Push-In"),
                            lighting_mood="Kodak 2383 Cinematic Lighting",
                        ),
                        title_overlay=item.get("title", f"CẢNH 0{idx + 1}").upper(),
                        particle_preset=item.get("particle", "warm_dust"),
                    )
                )
            project.shots = built_shots
            project.current_stage = "storyboard_review"
            return project

        # Bộ bóc tách kịch bản thông minh theo từng dòng/câu khi chạy offline
        raw_lines = [
            line.strip()
            for line in project.user_prompt.replace(". ", ".\n").splitlines()
            if len(line.strip()) > 4
        ]
        if not raw_lines:
            raw_lines = [project.user_prompt.strip() or "Cảnh điện ảnh mở đầu"]

        lenses = [
            ("24mm Anamorphic", "f/2.8", "Slow Aerial Push-In", "mist"),
            ("85mm Anamorphic Macro", "f/1.4", "Macro Parallax Slider", "warm_dust"),
            ("35mm Anamorphic", "f/1.8", "Dynamic Low-Angle Orbit", "embers"),
            ("50mm Anamorphic", "f/2.0", "Slow Crane Pull-Back", "warm_dust"),
        ]

        built_shots = []
        for idx, line in enumerate(raw_lines):
            lens, aperture, motion, particle = lenses[idx % len(lenses)]
            words = " ".join(line.split()[:4]).upper()
            built_shots.append(
                ShotItem(
                    shot_id=f"shot_0{idx + 1}",
                    order=idx + 1,
                    duration_seconds=4.5,
                    status=ShotStatus.DRAFT,
                    narration_text=line,
                    visual_synopsis=line,
                    veo_image_prompt=(
                        f"Cinematic 2.39:1 anamorphic shot of {line}, shot on ARRI Alexa 65, "
                        f"{lens} {aperture}, Kodak 2383 film color grading, photorealistic, no text"
                    ),
                    veo_motion_prompt=f"{motion}, natural 24fps 180-degree shutter motion blur",
                    camera=CameraSpec(
                        shot_size="Cinematic Anamorphic Shot",
                        focal_length=lens,
                        aperture=aperture,
                        camera_motion=motion,
                        lighting_mood="Volumetric Cinematic Lighting",
                    ),
                    title_overlay=words,
                    particle_preset=particle,
                )
            )
        project.shots = built_shots
        project.current_stage = "storyboard_review"
        return project

    @staticmethod
    def run_gate1_free_storyboards(project: CinemaProject) -> CinemaProject:
        for shot in project.shots:
            if shot.status in (ShotStatus.DRAFT, ShotStatus.REGENERATE_REQUESTED):
                shot.first_frame_path = GoogleFlowBridge.generate_free_storyboard_frame(
                    project.project_id, shot
                )
                shot.status = ShotStatus.STORYBOARD_READY
        project.current_stage = "gate1_waiting_storyboard_approval"
        return project

    @staticmethod
    def run_gate2_veo3_generation(
        project: CinemaProject, model_tier: str = "veo-3-fast"
    ) -> CinemaProject:
        for shot in project.shots:
            if shot.status == ShotStatus.STORYBOARD_APPROVED:
                shot.raw_video_path = GoogleFlowBridge.generate_veo3_shot_video(
                    project.project_id, shot, model_tier=model_tier
                )
                shot.status = ShotStatus.VIDEO_READY
        project.current_stage = "gate2_waiting_video_approval"
        return project
