import hashlib
import json
import pathlib
from backend.models import ShotItem

CACHE_DIR = pathlib.Path("./out/shot_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class ShotCacheManager:
    """
    Bộ nhớ đệm theo từng Cảnh quay (Shot-Level Content-Addressable Cache).
    Nếu 1 cảnh không thay đổi video gốc, lời dẫn, chữ 3D hay chuyển động máy,
    hệ thống lấy ngay kết quả đã render từ ổ SSD trong 0.01 giây mà không cần render lại!
    """

    @staticmethod
    def compute_shot_hash(shot: ShotItem, lut_file: str, aspect_crop: str) -> str:
        payload = {
            "shot_id": shot.shot_id,
            "duration": shot.duration_seconds,
            "raw_video": shot.raw_video_path or "",
            "voiceover": shot.voiceover_path or "",
            "title": shot.title_overlay or "",
            "narration": shot.narration_text or "",
            "lens": shot.camera.focal_length,
            "motion": shot.camera.camera_motion,
            "particle": shot.particle_preset,
            "lut": lut_file,
            "aspect": aspect_crop,
        }
        raw_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()[:16]

    @staticmethod
    def get_cached_segment(shot: ShotItem, lut_file: str, aspect_crop: str) -> pathlib.Path:
        digest = ShotCacheManager.compute_shot_hash(shot, lut_file, aspect_crop)
        return CACHE_DIR / f"{shot.shot_id}_{digest}.mp4"

    @staticmethod
    def is_cached(shot: ShotItem, lut_file: str, aspect_crop: str) -> bool:
        target = ShotCacheManager.get_cached_segment(shot, lut_file, aspect_crop)
        return target.exists() and target.stat().st_size > 0
