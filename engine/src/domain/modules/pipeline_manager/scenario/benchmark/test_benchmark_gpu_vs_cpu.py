"""
Benchmark: GPU vs CPU Rendering Performance Test
Wrapped as a unittest for discovery.
"""

import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Adjust imports to be absolute from src
from adapters.driven.encoder.moviepy_encoder_adapter import MoviePyAdapter  # noqa: E402
from adapters.driven.psd_modeler.psdtools_parser_adapter import PsdToolsAdapter  # noqa: E402
from adapters.driven.renderers.cupy_renderer_adapter import CupyRendererAdapter  # noqa: E402
from adapters.driven.renderers.pillow_renderer_adapter import PillowRenderer  # noqa: E402
from adapters.driven.ui_modeler import UIRendererCore  # noqa: E402
from domain.core import EngineProgress, RenderConfig  # noqa: E402
from domain.core.engine import ProducerEngine as DirectorEngine  # noqa: E402
from domain.value_objects.animation.sequencing_strategy_value import (  # noqa: E402
    SequencingStrategy,
)

# --- Constants ---
# PROJECT_ROOT is 'engine/src'
PSD_PATH = str(PROJECT_ROOT / "assets/Psd/test.psd")
OUTPUT_DIR = str(PROJECT_ROOT / "tests/outputs/benchmark")
CPU_OUTPUT = os.path.join(OUTPUT_DIR, "benchmark_cpu.mp4")
GPU_OUTPUT = os.path.join(OUTPUT_DIR, "benchmark_gpu.mp4")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "benchmark_results.json")


def create_engine_for_cpu() -> DirectorEngine:
    """Factory to create a DirectorEngine configured for CPU rendering."""
    return DirectorEngine(
        psd_port=PsdToolsAdapter(),
        renderer_port=PillowRenderer(),
        video_port=MoviePyAdapter(prefer_nvenc=False),  # Force CPU encoder
        ui_renderer_factory=lambda: UIRendererCore(),
    )


def create_engine_for_gpu() -> DirectorEngine:
    """Factory to create a DirectorEngine configured for GPU rendering."""
    # Import locally to avoid crashing if CuPy is missing (allows skipping test)

    return DirectorEngine(
        psd_port=PsdToolsAdapter(),
        renderer_port=PillowRenderer(),
        video_port=MoviePyAdapter(prefer_nvenc=True),  # Use NVENC if available
        gpu_renderer_port=CupyRendererAdapter(),
        ui_renderer_factory=lambda: UIRendererCore(),
    )


def progress_callback(progress: EngineProgress) -> None:
    """Print progress updates."""
    # Reduced verbosity for test runner
    pass
    # print(f"  [{progress.state.value}] {progress.message} ({progress.progress_percent:.1f}%)")


def run_cpu_benchmark(engine: DirectorEngine, config: RenderConfig) -> float:
    """Run CPU benchmark and return elapsed time in seconds."""
    print("\\n=== CPU Benchmark (run_optimized) ===")
    engine.set_progress_callback(progress_callback)

    start_time = time.perf_counter()
    output_path = engine.run_optimized(config)
    end_time = time.perf_counter()

    elapsed = end_time - start_time
    print(f"  Output: {output_path}")
    print(f"  Elapsed Time: {elapsed:.3f} seconds")
    return elapsed


def run_gpu_benchmark(engine: DirectorEngine, config: RenderConfig) -> float:
    """Run GPU benchmark and return elapsed time in seconds."""
    print("\\n=== GPU Benchmark (run_gpu) ===")
    engine.set_progress_callback(progress_callback)

    start_time = time.perf_counter()
    output_path = engine.run_gpu(config)
    end_time = time.perf_counter()

    elapsed = end_time - start_time
    print(f"  Output: {output_path}")
    print(f"  Elapsed Time: {elapsed:.3f} seconds")
    return elapsed


class TestBenchmarkGpuVsCpu(unittest.TestCase):
    """Benchmark: GPU vs CPU Performance."""

    @unittest.skipUnless(
        os.environ.get("RUN_BENCHMARKS") == "1",
        "Benchmarks skipped by default. Set RUN_BENCHMARKS=1 to run.",
    )
    def test_run_benchmark(self) -> None:  # noqa: PLR0915
        """Main benchmark execution."""
        print("=" * 60)
        print(" GPU vs CPU Rendering Benchmark")
        print("=" * 60)

        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        results: dict[str, Any] = {
            "psd_file": PSD_PATH,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu": {},
            "gpu": {},
        }

        # --- CPU Benchmark ---
        try:
            cpu_engine = create_engine_for_cpu()
            cpu_engine.load_project(PSD_PATH)
            cpu_engine.generate_timeline(SequencingStrategy.STAGGERED)

            cpu_config = RenderConfig(
                output_path=CPU_OUTPUT,
                fps=30,
                width=1080,
                height=1920,
                strategy=SequencingStrategy.STAGGERED,
                use_gpu=False,
            )

            print("\\n=== CPU Benchmark (run) ===")
            cpu_engine.set_progress_callback(progress_callback)

            start_time = time.perf_counter()
            output_path = cpu_engine.run(cpu_config)
            end_time = time.perf_counter()

            elapsed = end_time - start_time
            print(f"  Output: {output_path}")
            print(f"  Elapsed Time: {elapsed:.3f} seconds")
            cpu_time = elapsed
            results["cpu"] = {
                "elapsed_seconds": round(cpu_time, 3),
                "output_file": CPU_OUTPUT,
                "status": "success",
            }
        except Exception as e:
            print(f"  CPU Benchmark FAILED: {e}")
            results["cpu"] = {"status": "failed", "error": str(e)}
            cpu_time = None

        # --- GPU Benchmark ---
        gpu_time = None
        try:
            # Check if cupy available first?
            # Assuming it might need drivers
            gpu_engine = create_engine_for_gpu()
            gpu_engine.load_project(PSD_PATH)
            gpu_engine.generate_timeline(SequencingStrategy.STAGGERED)

            gpu_config = RenderConfig(
                output_path=GPU_OUTPUT,
                fps=30,
                width=1080,
                height=1920,
                strategy=SequencingStrategy.STAGGERED,
                use_gpu=True,
            )

            print("\\n=== GPU Benchmark (run) ===")
            gpu_engine.set_progress_callback(progress_callback)

            start_time = time.perf_counter()
            output_path = gpu_engine.run(gpu_config)
            end_time = time.perf_counter()

            elapsed = end_time - start_time
            print(f"  Output: {output_path}")
            print(f"  Elapsed Time: {elapsed:.3f} seconds")
            gpu_time = elapsed
            results["gpu"] = {
                "elapsed_seconds": round(gpu_time, 3),
                "output_file": GPU_OUTPUT,
                "status": "success",
            }
        except ImportError:
            print("  GPU Benchmark SKIPPED (CuPy/drivers missing)")
            results["gpu"] = {"status": "skipped", "error": "ImportError"}
        except Exception as e:
            print(f"  GPU Benchmark FAILED: {e}")
            results["gpu"] = {"status": "failed", "error": str(e)}

        # --- Calculate Speedup ---
        if cpu_time and gpu_time:
            speedup = cpu_time / gpu_time
            results["speedup_factor"] = round(speedup, 2)
            print("\\n" + "=" * 60)
            print(" RESULTS:")
            print(f"   CPU Time: {cpu_time:.3f}s")
            print(f"   GPU Time: {gpu_time:.3f}s")
            print(f"   Speedup:  {speedup:.2f}x")
            print("=" * 60)
        else:
            results["speedup_factor"] = None
            print("\\n  Could not calculate speedup (one or both benchmarks failed).")

        # --- Save Results ---
        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\\nResults saved to: {RESULTS_FILE}")
        self.assertTrue(os.path.exists(RESULTS_FILE))


if __name__ == "__main__":
    unittest.main()
