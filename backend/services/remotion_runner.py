import json
import os
import pathlib
from backend.models import CinemaProject, ShotStatus

RENDERER_DIR = pathlib.Path("./renderer")
MANIFEST_PATH = RENDERER_DIR / "public" / "project_manifest.json"
OUT_DIR = pathlib.Path("./out")


class RemotionRunner:
    """
    Điều phối việc xuất danh sách các cảnh đã duyệt sang Remotion (2048x1080 @ 24fps)
    và gọi FFmpeg NVENC trên card NVIDIA Quadro P2000 để đóng gói file phim cuối cùng.
    """

    @staticmethod
    def export_manifest(project: CinemaProject) -> str:
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        approved_shots = [
            {
                "shotId": s.shot_id,
                "order": s.order,
                "durationSeconds": s.duration_seconds,
                "rawVideoUrl": s.raw_video_path or "",
                "voiceoverUrl": s.voiceover_path or "",
                "titleOverlay": s.title_overlay,
                "focalLength": s.camera.focal_length,
                "cameraMotion": s.camera.camera_motion,
                "particlePreset": s.particle_preset,
                "narrationText": s.narration_text,
            }
            for s in sorted(project.shots, key=lambda x: x.order)
            if s.status == ShotStatus.VIDEO_APPROVED
        ]

        payload = {
            "projectId": project.project_id,
            "projectTitle": project.title,
            "width": project.resolution_width,
            "height": project.resolution_height,
            "fps": project.fps,
            "enableAnamorphicBars": True,
            "shots": approved_shots,
        }
        MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(MANIFEST_PATH.resolve())

    @staticmethod
    def render_dci2k_master(project: CinemaProject) -> dict:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        manifest_file = RemotionRunner.export_manifest(project)

        raw_remotion_mp4 = OUT_DIR / f"{project.project_id}_remotion_2048x1080.mp4"
        final_cinema_mp4 = OUT_DIR / f"{project.project_id}_FINAL_DCI2K_24FPS.mp4"
        concurrency = os.getenv("REMOTION_CONCURRENCY", "3")

        remotion_cmd = [
            "npx", "remotion", "render",
            "src/index.ts",
            "Video3DRemotionCinema",
            str(raw_remotion_mp4.resolve()),
            f"--props={manifest_file}",
            f"--concurrency={concurrency}",
            "--gl=angle",
        ]

        ffmpeg_filter = (
            f"scale=2048:1080:flags=lanczos,cas=0.4,"
            f"lut3d=file='{project.lut_file}',noise=c0s=4:c0f=t+u"
        )
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-hwaccel", "cuda",
            "-i", str(raw_remotion_mp4.resolve()),
            "-vf", ffmpeg_filter,
            "-r", "24",
            "-c:v", "h264_nvenc",
            "-preset", "p6",
            "-tune", "hq",
            "-rc", "vbr",
            "-cq", "17",
            "-b:v", "25M",
            "-maxrate", "35M",
            "-bufsize", "50M",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "320k",
            str(final_cinema_mp4.resolve()),
        ]

        return {
            "status": "manifest_exported",
            "manifest_path": manifest_file,
            "remotion_command": " ".join(remotion_cmd),
            "ffmpeg_nvenc_command": " ".join(ffmpeg_cmd),
            "output_path": str(final_cinema_mp4.resolve()),
        }
