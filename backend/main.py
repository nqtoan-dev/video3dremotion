import pathlib
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from backend.models import (
    CinemaProject,
    CreateProjectRequest,
    ShotFeedbackRequest,
    ShotStatus,
)
from backend.agents.director_graph import CinematicDirectorAgent
from backend.services.google_flow_bridge import GoogleFlowBridge
from backend.services.remotion_runner import RemotionRunner
from backend.services.shot_cache import ShotCacheManager

app = FastAPI(
    title="video3dremotion — High-Speed DCI 2K Cinema Studio",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECTS_DB: Dict[str, CinemaProject] = {}
STUDIO_HTML_PATH = pathlib.Path("./studio_ui/video3dremotion_studio.html")


@app.get("/", response_class=HTMLResponse)
def serve_studio_ui():
    if STUDIO_HTML_PATH.exists():
        return STUDIO_HTML_PATH.read_text(encoding="utf-8")
    return "<h1>video3dremotion API is running</h1>"


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": "3.0.0",
        "hardware_profile": "Dell Precision 7530 (Xeon E-2176M + 32GB RAM + Quadro P2000 4GB)",
        "cinema_standard": "DCI 2K (2048x1080 @ 24fps, CinemaScope 2.39:1)",
        "flow_credits": GoogleFlowBridge.check_credits(),
    }


@app.post("/api/projects", response_model=CinemaProject)
def create_project_and_breakdown(req: CreateProjectRequest):
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    proj = CinemaProject(project_id=project_id, user_prompt=req.user_prompt)
    proj = CinematicDirectorAgent.analyze_and_breakdown_script(proj)
    proj = CinematicDirectorAgent.run_gate1_free_storyboards(proj)
    PROJECTS_DB[project_id] = proj
    return proj


@app.get("/api/projects/{project_id}", response_model=CinemaProject)
def get_project(project_id: str):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    return PROJECTS_DB[project_id]


@app.post("/api/projects/{project_id}/shots/{shot_id}/regenerate-storyboard", response_model=CinemaProject)
def regenerate_single_storyboard(project_id: str, shot_id: str, req: ShotFeedbackRequest):
    proj = get_project(project_id)
    for shot in proj.shots:
        if shot.shot_id == shot_id:
            shot.user_feedback = req.feedback
            shot.status = ShotStatus.REGENERATE_REQUESTED
            shot.first_frame_path = GoogleFlowBridge.generate_free_storyboard_frame(project_id, shot)
            shot.status = ShotStatus.STORYBOARD_READY
            break
    return proj


@app.post("/api/projects/{project_id}/approve-storyboards", response_model=CinemaProject)
def approve_storyboards_and_generate_veo3(project_id: str, req: ShotFeedbackRequest):
    proj = get_project(project_id)
    for shot in proj.shots:
        if shot.status == ShotStatus.STORYBOARD_READY:
            shot.status = ShotStatus.STORYBOARD_APPROVED
    proj = CinematicDirectorAgent.run_gate2_veo3_generation(proj, model_tier=req.model_tier)
    return proj


@app.post("/api/projects/{project_id}/shots/{shot_id}/regenerate-video", response_model=CinemaProject)
def regenerate_single_veo3_video(project_id: str, shot_id: str, req: ShotFeedbackRequest):
    proj = get_project(project_id)
    for shot in proj.shots:
        if shot.shot_id == shot_id:
            shot.user_feedback = req.feedback
            shot.raw_video_path = GoogleFlowBridge.generate_veo3_shot_video(
                project_id, shot, model_tier=req.model_tier
            )
            shot.status = ShotStatus.VIDEO_READY
            break
    return proj


@app.post("/api/projects/{project_id}/approve-all-and-render")
def approve_all_shots_and_master_cinema(project_id: str):
    proj = get_project(project_id)
    cache_report = []
    for shot in proj.shots:
        shot.status = ShotStatus.VIDEO_APPROVED
        cache_report.append({
            "shot_id": shot.shot_id,
            "hash": ShotCacheManager.compute_shot_hash(shot, proj.lut_file, proj.aspect_ratio_crop),
            "cached": ShotCacheManager.is_cached(shot, proj.lut_file, proj.aspect_ratio_crop),
        })
    proj.current_stage = "completed_mastering"
    render_info = RemotionRunner.render_dci2k_master(proj)
    return {
        "project": proj,
        "shot_cache": cache_report,
        "mastering": render_info,
    }
