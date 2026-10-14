import os
from typing import List
from backend.models import CameraSpec, CinemaProject, ShotItem, ShotStatus
from backend.services.google_flow_bridge import GoogleFlowBridge


class CinematicDirectorAgent:
    """
    Hệ thống Multi-Agent kết hợp:
      - Screenwriter Agent (Lên kịch bản tổng & lời dẫn)
      - Cinematographer Agent (Chia nhỏ thành các cảnh quay chuẩn rạp DCI 2K 2.39:1)
      - Storyboard & Veo 3 Orchestrator (Có 2 trạm dừng chờ người dùng duyệt)
    """

    @staticmethod
    def analyze_and_breakdown_script(project: CinemaProject) -> CinemaProject:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key and api_key != "your_gemini_api_key_here":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-pro",
                    temperature=0.35,
                    google_api_key=api_key,
                )
                structured_llm = llm.with_structured_output(CinemaProject)
                prompt = f"""
                Bạn là Đạo diễn Điện ảnh & DOP (Quay phim trưởng) đạt giải Oscar.
                Hãy phân tích yêu cầu làm video sau của người dùng:
                "{project.user_prompt}"

                Nhiệm vụ:
                1. Đặt tiêu đề phim (title), tóm tắt (logline) và mô tả nhân vật/bối cảnh cố định (character_reference_prompt).
                2. Chia kịch bản thành 4 đến 6 cảnh quay (shots) chuẩn điện ảnh (mỗi cảnh từ 4.0s đến 5.5s).
                3. Thiết kế thông số ống kính Anamorphic (24mm, 35mm, 50mm, 85mm), khẩu độ (f/1.4 - f/2.8) và chuyển động máy quay đa dạng.
                4. Viết 'veo_image_prompt' (mô tả khung hình đầu chi tiết bằng tiếng Anh) và 'veo_motion_prompt' (mô tả chuyển động máy và chủ thể bằng tiếng Anh).
                """
                result: CinemaProject = structured_llm.invoke(prompt)
                result.project_id = project.project_id
                result.user_prompt = project.user_prompt
                result.current_stage = "storyboard_review"
                return result
            except Exception as exc:
                print(f"[Fallback] Sử dụng bộ phân cảnh mẫu do lỗi gọi LLM: {exc}")

        topic = project.user_prompt.strip()
        project.title = f"PHIM ĐIỆN ẢNH DCI 2K: {topic[:42].upper()}"
        project.logline = f"Hành trình điện ảnh màn ảnh rộng 2.39:1 tái hiện: {topic}"
        project.character_reference_prompt = (
            "Consistent cinematic protagonist, natural skin texture, wearing weathered dark expedition jacket, "
            "shot on ARRI Alexa 65 with Panavision C-Series Anamorphic lenses, Kodak 2383 color science"
        )

        sample_shots: List[ShotItem] = [
            ShotItem(
                shot_id="shot_01",
                order=1,
                duration_seconds=4.5,
                status=ShotStatus.DRAFT,
                narration_text="Giữa không gian mênh mông của bình minh, mọi câu chuyện vĩ đại đều bắt đầu từ một khoảnh khắc tĩnh lặng.",
                visual_synopsis=f"[Cảnh Mở Đầu — Đại Cảnh Anamorphic] Toàn cảnh không gian hùng vĩ giới thiệu bối cảnh chính của '{topic}' dưới ánh nắng vàng xuyên qua lớp sương mù dày.",
                veo_image_prompt=f"Extreme wide establishing shot of {topic}, volumetric golden hour sunbeams piercing through morning mist, dramatic depth, epic scale",
                veo_motion_prompt="Slow cinematic drone push-in forward through floating mist, subtle wind moving the environment",
                camera=CameraSpec(
                    shot_size="Extreme Wide Shot (EWS)",
                    focal_length="24mm Anamorphic",
                    aperture="f/2.8",
                    camera_motion="Slow Aerial Push-In",
                    lighting_mood="Volumetric Golden Hour God Rays",
                ),
                title_overlay="KHỞI NGUỒN ĐẠI NGÀN",
                particle_preset="mist",
            ),
            ShotItem(
                shot_id="shot_02",
                order=2,
                duration_seconds=4.0,
                status=ShotStatus.DRAFT,
                narration_text="Từng chi tiết nhỏ nhất đều mang trong mình hơi thở của thời gian và sự chế tác tỉ mỉ.",
                visual_synopsis=f"[Cảnh Cận Macro — Chiều Sâu Trường Ảnh] Cận cảnh chi tiết chủ thể trung tâm của '{topic}', hậu cảnh xoá phông Bokeh mượt mà với các hạt bụi sáng lơ lửng.",
                veo_image_prompt=f"Extreme close-up macro shot of key detail in {topic}, shallow depth of field, creamy anamorphic oval bokeh, warm rim lighting",
                veo_motion_prompt="Ultra-slow macro dolly track left to right, focus rack from foreground texture to main subject",
                camera=CameraSpec(
                    shot_size="Extreme Close-Up (ECU)",
                    focal_length="85mm Anamorphic Macro",
                    aperture="f/1.4",
                    camera_motion="Macro Parallax Slider & Rack Focus",
                    lighting_mood="Warm Chiaroscuro Rim Light",
                ),
                title_overlay=None,
                particle_preset="warm_dust",
            ),
            ShotItem(
                shot_id="shot_03",
                order=3,
                duration_seconds=5.0,
                status=ShotStatus.DRAFT,
                narration_text="Khi chuyển động đạt đến đỉnh cao, ánh sáng và cảm xúc hòa quyện thành một bản giao hưởng thị giác.",
                visual_synopsis=f"[Cảnh Cao Trào — Góc Máy Thấp Hất Lên] Máy quay bám đuổi (Tracking shot) góc thấp tạo cảm giác choáng ngợp và uy lực cho '{topic}'.",
                veo_image_prompt=f"Low-angle heroic medium shot of {topic} in dynamic action, dramatic contrast, teal shadows and warm amber highlights, anamorphic lens flare",
                veo_motion_prompt="Dynamic low-angle gimbal tracking shot orbiting 30 degrees around the subject in slow motion",
                camera=CameraSpec(
                    shot_size="Heroic Low-Angle Medium Shot",
                    focal_length="35mm Anamorphic",
                    aperture="f/1.8",
                    camera_motion="Dynamic Low-Angle Orbit & Track",
                    lighting_mood="High-Contrast Teal & Orange Dramatic Lighting",
                ),
                title_overlay="ĐỈNH CAO CHUYỂN ĐỘNG",
                particle_preset="embers",
            ),
            ShotItem(
                shot_id="shot_04",
                order=4,
                duration_seconds=4.5,
                status=ShotStatus.DRAFT,
                narration_text="Một dấu ấn điện ảnh không thể trộn lẫn, trường tồn trong từng khung hình.",
                visual_synopsis=f"[Cảnh Kết (Outro) — Bố Cục Đối Xứng] Khung hình đối xứng hoàn hảo khép lại câu chuyện '{topic}', ánh sáng dịu dần để nổi bật thông điệp thương hiệu 3D.",
                veo_image_prompt=f"Symmetrical cinematic master shot of {topic} at twilight blue hour, warm glowing focal point in center, moody atmospheric haze",
                veo_motion_prompt="Slow crane pull-back and tilt up into the atmospheric horizon",
                camera=CameraSpec(
                    shot_size="Symmetrical Wide Master Shot",
                    focal_length="50mm Anamorphic",
                    aperture="f/2.0",
                    camera_motion="Slow Crane Pull-Back",
                    lighting_mood="Twilight Blue Hour & Warm Center Glow",
                ),
                title_overlay="DẤU ẤN VƯỢT THỜI GIAN",
                particle_preset="warm_dust",
            ),
        ]
        project.shots = sample_shots
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
