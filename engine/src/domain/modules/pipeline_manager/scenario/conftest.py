import pytest
import sys
from pathlib import Path

# Ensure src path
SCENARIO_DIR = Path(__file__).parent
from domain.modules.script_director import plan_smart_timeline

layers = list(psd_world.scene.iterate_all())
return plan_smart_timeline(
    layers=layers,
    canvas_width=psd_world.width,
    canvas_height=psd_world.height,
    exclude_bottom_layer=True
)
    service = MediaOutputService(config)

    return service