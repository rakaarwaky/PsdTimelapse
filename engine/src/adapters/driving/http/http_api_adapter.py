"""
HttpApiAdapter: FastAPI adapter for external access.
Dependencies: fastapi, uvicorn, ProducerEngine
"""

from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import (  # type: ignore[import-not-found]  # noqa: PLR0913, PLR0912
        BackgroundTasks,
        FastAPI,
        File,
        HTTPException,
        UploadFile,
    )
    from pydantic import BaseModel  # type: ignore[import-not-found]

    HAS_FASTAPI = True
else:
    try:
        from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
        from pydantic import BaseModel

        HAS_FASTAPI = True
    except ImportError:
        HAS_FASTAPI = False
        FastAPI = Any
        BaseModel = object
        # Mocks for runtime safety
        BackgroundTasks = Any
        File = Any
        HTTPException = Any
        UploadFile = Any

from domain.core import (  # type: ignore[import-not-found]
    EngineProgress,
    EngineState,
    ProducerConfig,  # Use ProducerConfig for high level options like 'use_gpu'
    ProducerEngine,
    SequencingStrategy,
)


# Request/Response Models
class RenderRequest(BaseModel):  # type: ignore[misc]
    """Request body for render endpoint."""

    psd_path: str
    output_path: str = "./output.mp4"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    strategy: str = "staggered"
    use_gpu: bool = False


class RenderResponse(BaseModel):  # type: ignore[misc]
    """Response for render endpoint."""

    status: str
    message: str
    job_id: str | None = None
    output_path: str | None = None


class ProgressResponse(BaseModel):  # type: ignore[misc]
    """Response for progress endpoint."""

    state: str
    current_frame: int
    total_frames: int
    progress_percent: float
    message: str


# Global state for background jobs
_active_jobs: dict[str, EngineProgress] = {}


def create_api(engine: ProducerEngine) -> FastAPI:
    if not HAS_FASTAPI:
        raise ImportError("FastAPI not installed")

    app = FastAPI(title="Timelapse Engine API", version="2.0.0")

    uploads_dir = "./uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...)):  # type: ignore[no-untyped-def]  # noqa: B008
        if not file.filename:
            raise HTTPException(400, "No filename")
        ext = file.filename.split(".")[-1].lower()
        if ext not in ("psd", "psb"):
            raise HTTPException(400, "Only PSD/PSB")

        safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        file_path = os.path.join(uploads_dir, safe_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        return {"status": "uploaded", "path": os.path.abspath(file_path)}

    @app.get("/health")
    async def health_check():  # type: ignore[no-untyped-def]
        return {"status": "healthy", "engine_state": engine.state.value}

    @app.post("/render", response_model=RenderResponse)
    async def start_render(request: RenderRequest, background_tasks: BackgroundTasks):  # type: ignore[no-untyped-def]
        if not os.path.exists(request.psd_path):
            raise HTTPException(404, f"PSD not found: {request.psd_path}")

        strategy_map = {
            "sequential": SequencingStrategy.SEQUENTIAL,
            "parallel": SequencingStrategy.PARALLEL,
            "staggered": SequencingStrategy.STAGGERED,
        }
        strategy = strategy_map.get(request.strategy, SequencingStrategy.STAGGERED)

        # Use ProducerConfig which supports high-level options like use_gpu
        config = ProducerConfig(
            output_path=request.output_path,
            fps=request.fps,
            width=request.width,
            height=request.height,
            strategy=strategy,
            use_gpu=request.use_gpu,
        )

        job_id = str(uuid.uuid4())[:8]

        def track_progress(progress: EngineProgress) -> None:
            _active_jobs[job_id] = progress

        engine.set_progress_callback(track_progress)
        background_tasks.add_task(_run_render, engine, request.psd_path, config, job_id)

        return RenderResponse(
            status="started", message=f"Render job {job_id} started", job_id=job_id
        )

    @app.get("/progress/{job_id}", response_model=ProgressResponse)
    async def get_progress(job_id: str):  # type: ignore[no-untyped-def]
        if job_id not in _active_jobs:
            raise HTTPException(404, "Job not found")
        progress = _active_jobs[job_id]
        return ProgressResponse(
            state=progress.state.value,
            current_frame=progress.current_frame,
            total_frames=progress.total_frames,
            progress_percent=progress.progress_percent,
            message=progress.message,
        )

    @app.get("/download/{job_id}")
    async def download_video(job_id: str) -> None:
        if job_id not in _active_jobs:
            raise HTTPException(404, "Job not found")
        progress = _active_jobs[job_id]
        if progress.state != EngineState.COMPLETE:
            raise HTTPException(400, "Not complete")
        raise HTTPException(501, "Download not implemented")

    return app


async def _run_render(
    engine: ProducerEngine, psd_path: str, config: ProducerConfig, job_id: str
) -> None:
    try:
        engine.load_psd(psd_path)
        engine.generate_timeline(config.strategy)
        engine.render(config)
    except Exception as e:
        _active_jobs[job_id] = EngineProgress(
            state=EngineState.ERROR, current_frame=0, total_frames=0, message=str(e)
        )
