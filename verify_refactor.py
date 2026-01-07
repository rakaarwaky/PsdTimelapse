import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'engine/src'))

try:
    from PIL import Image
except ImportError:
    print("PIL not installed")
    sys.exit(1)

from dataclasses import dataclass
from unittest.mock import MagicMock

# Import refactored modules
from domain.modules.pipeline_manager.rendering.layer_animation_service_module import create_layer_animation_service
from domain.modules.animator.rendering.layer_render_config_module import LayerRenderConfig
from domain.entities.layer_entity import LayerEntity
from domain.value_objects.common.bounds_value import Bounds
from domain.value_objects.common.opacity_value import Opacity
from domain.value_objects.geometry.vector_value import Vector2

def test_layer_animation_service():
    print("Testing LayerAnimationService...")
    
    # Mock config
    config = LayerRenderConfig(
        canvas_width=100,
        canvas_height=100,
        fps=30
    )
    
    # Create service
    service = create_layer_animation_service(config)
    
    # Mock Layer
    layer = MagicMock(spec=LayerEntity)
    layer.id = "test_layer"
    layer.position = Vector2(50, 50)
    layer.opacity = Opacity(1.0)
    layer.bounds = Bounds(0, 0, 50, 50)
    
    # Mock Image Callback
    def get_layer_image(l):
        return Image.new('RGBA', (50, 50), (255, 0, 0, 255))
        
    # Timeline info
    timeline_mock = {
        'start_frame': 0,
        'end_frame': 5,
        'total_frames': 10,
        'action': None
    }
    
    # Run generator
    frames = list(service.generate_frames(layer, get_layer_image, timeline_mock))
    
    print(f"Generated {len(frames)} frames")
    
    has_image = False
    for f in frames:
        if f.frame_type == "active":
            if f.image is not None and isinstance(f.image, Image.Image):
                has_image = True
            else:
                print(f"Frame {f.frame_number} active but no image!")
                
    if has_image:
        print("SUCCESS: Service produced RenderFrames with Images.")
    else:
        print("FAILURE: No images found in active frames.")

if __name__ == "__main__":
    test_layer_animation_service()
