from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ShotStatus(str, Enum):
    DRAFT = "draft"
    STORYBOARD_READY = "storyboard_ready"       # Đã có ảnh tĩnh (0 credit), chờ duyệt ở Trạm 1
    STORYBOARD_APPROVED = "storyboard_approved" # Đã duyệt ảnh, sẵn sàng gọi Veo 3 i2v
    VIDEO_READY = "video_ready"                 # Đã có clip Veo 3, chờ duyệt ở Trạm 2
    VIDEO_APPROVED = "video_approved"           # Đã duyệt cảnh quay, sẵn sàng ghép phim DCI 2K
    REGENERATE_REQUESTED = "regenerate_requested"


class CameraSpec(BaseModel):
    shot_size: str = Field(
        default="Medium Anamorphic Shot",
        description="Cỡ cảnh: Extreme Close-Up (ECU), Close-Up, Medium Shot, Wide Establishing Shot",
    )
    focal_length: str = Field(
        default="50mm Anamorphic",
        description="Tiêu cự ống kính: 24mm, 35mm, 50mm, 85mm Anamorphic",
    )
    aperture: str = Field(default="f/1.8", description="Khẩu độ ống kính tạo hiệu ứng xoá phông Bokeh")
    camera_motion: str = Field(
        default="Slow Dolly Push-In",
        description="Chuyển động máy quay: Slow Dolly Push-In, Low-Angle Tracking, Crane Up, Subtle Handheld",
    )
    lighting_mood: str = Field(
        default="Volumetric Golden Hour & Soft Rim Light",
        description="Thiết kế ánh sáng điện ảnh cho cảnh quay",
    )


class ShotItem(BaseModel):
    shot_id: str
    order: int
    duration_seconds: float = Field(default=4.5, ge=2.0, le=8.0)
    status: ShotStatus = Field(default=ShotStatus.DRAFT)
    narration_text: str = Field(default="", description="Lời bình / Voiceover của cảnh")
    visual_synopsis: str = Field(..., description="Mô tả cảnh quay bằng tiếng Việt để người dùng duyệt")
    veo_image_prompt: str = Field(..., description="Prompt tiếng Anh chuẩn tạo ảnh First Frame trên Google Flow")
    veo_motion_prompt: str = Field(..., description="Prompt tiếng Anh điều khiển chuyển động cho Veo 3 i2v")
    camera: CameraSpec = Field(default_factory=CameraSpec)
    title_overlay: Optional[str] = Field(default=None, description="Chữ 3D điện ảnh xuất hiện trong cảnh")
    particle_preset: str = Field(default="warm_dust", description="Hiệu ứng hạt 3D: warm_dust | mist | embers | none")
    user_feedback: Optional[str] = Field(default=None)
    first_frame_path: Optional[str] = None
    raw_video_path: Optional[str] = None
    voiceover_path: Optional[str] = None


class CinemaProject(BaseModel):
    project_id: str
    user_prompt: str
    title: str = "Dự Án Phim Điện Ảnh DCI 2K"
    logline: str = ""
    resolution_width: int = 2048
    resolution_height: int = 1080
    aspect_ratio_crop: str = "2.39:1"
    fps: int = 24
    lut_file: str = "luts/kodak_2383_cinema.cube"
    character_reference_prompt: str = ""
    current_stage: str = "init"
    shots: List[ShotItem] = Field(default_factory=list)


class CreateProjectRequest(BaseModel):
    user_prompt: str
    simulation_mode: bool = False


class ShotFeedbackRequest(BaseModel):
    feedback: Optional[str] = None
    model_tier: str = "veo-3-fast"
