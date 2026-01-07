"""
Main entry point for the Timelapse Engine.
Dependencies: uvicorn, fastapi, src.adapters.driving

Run with: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Import from Single Source of Truth
from adapters.driving.http_api_adapter import create_api

from domain.core import ProducerEngine

# Try to import adapters (may fail if dependencies not installed)
try:
    from adapters.driven.encoder import MoviePyEncoderAdapter
    from adapters.driven.psd_modeler import PsdModeler
    from adapters.driven.ui_modeler import UIRendererCore

    HAS_ALL_DEPS = True
except ImportError as e:
    HAS_ALL_DEPS = False
    print(f"Warning: Some dependencies not installed: {e}")

# Import Driven Adapters (Implementations)
try:
    from fastapi.middleware.cors import CORSMiddleware

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def create_engine() -> ProducerEngine:
    """Create a fully configured ProducerEngine with all adapters."""

    # 1. Initialize Ports (Adapters)
    psd_port = None
    video_port = None
    ui_renderer_factory = None
    gpu_renderer_port = None

    # Try importing optional dependencies
    try:
        from adapters.driven.psd_modeler import PsdModeler

        psd_port = PsdModeler()
        print("✅ PsdModeler loaded")
    except ImportError as e:
        print(f"⚠️ PsdModeler not loaded: {e}")

    try:
        from adapters.driven.encoder import MoviePyEncoderAdapter

        video_port = MoviePyEncoderAdapter()
        print("✅ MoviePyEncoderAdapter loaded")
    except ImportError as e:
        print(f"⚠️ MoviePyEncoderAdapter not loaded: {e}")

    try:
        from adapters.driven.ui_modeler import UIRendererCore

        ui_renderer_factory = lambda: UIRendererCore()
        print("✅ UIRendererCore factory loaded")
    except ImportError as e:
        print(f"⚠️ UIRendererCore not loaded: {e}")

    # Optional GPU support
    try:
        # Check for CuPy availability first to avoid messy tracebacks
        import cupy
        from adapters.driven.renderers.gpu.cupy_renderer_adapter import CupyRendererAdapter

        gpu_renderer_port = CupyRendererAdapter()
        print("✅ CupyRendererAdapter loaded (GPU Support Enabled)")
    except ImportError:
        print("ℹ️ GPU Rendering not available (requires cupy & CUDA)")
    except Exception as e:
        print(f"⚠️ GPU Adapter failed to load: {e}")

    # 2. Inject into ProducerEngine
    engine = ProducerEngine(
        psd_port=psd_port,
        renderer_port=None,  # Deprecated/Internal in new architecture
        video_port=video_port,
        ui_renderer_factory=ui_renderer_factory,
        gpu_renderer_port=gpu_renderer_port,
        # compositor_port=gpu_renderer_port # GPU adapter acts as Compositor usually, or separate
    )

    return engine


# Create engine and API
engine = create_engine()
app = create_api(engine)

# Add CORS middleware
if HAS_FASTAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Timelapse Engine API",
        "version": "2.0.0",
        "role": "IntegrationLead",
        "status": "ready",
        "mode": "ProducerEngine (SSOT)",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
