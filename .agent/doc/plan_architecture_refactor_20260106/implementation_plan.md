# RefactoringSpecialist Tasks: Hexagonal Architecture Compliance

**Goal:** Execute 5 tasks to align `engine/src/domain` with Hexagonal Architecture rules.

## Proposed Changes

### 1. Core Gateway (`core/__init__.py`)

#### [MODIFY] [\_\_init\_\_.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/core/__init__.py)

Add exports for all Entities, Value Objects, and Ports to create the "Gateway" layer. Modules will import shared types from `domain.core` instead of direct paths.

**Added exports:**
- Entities: `LayerEntity`, `SceneEntity`, `WorldEntity`, `CameraEntity`, `ViewportEntity`, `AssetEntity`, `DocumentEntity`, `TimelineEntity`, `DirectorProfile`
- Value Objects: `Vector2`, `Rect`, `Color`, `Dimensions`, `Duration`, `FrameRate`, `Resolution`, `Opacity`, `Progress`, `BrushTool`, etc.
- Ports: All from `domain.ports`

---

### 2. Define Ports

#### [NEW] [compositor\_port.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/ports/compositor_port.py)

Define `CompositorPort` interface for GPU blend operations. Methods:
- `blend(target, source, x, y) -> None`

#### [MODIFY] [\_\_init\_\_.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/ports/__init__.py)

Add `CompositorPort` to exports.

> [!NOTE]
> `ImageAdapterPort` in the task spec appears to map to the existing `ImageProcessingPort`. No new port needed for that.

---

### 3. Refactor GPU Module

#### [MODIFY] [gpu\_backend\_module.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/pipeline_manager/gpu_backend_module.py)

**Current violation (line 11):**
```python
from src.adapters.driven.renderers.gpu.cupy_compositor import CupyCompositor
```

**Fix:** Accept `CompositorPort` via constructor injection:
```diff
-from src.adapters.driven.renderers.gpu.cupy_compositor import CupyCompositor
+from ...ports.compositor_port import CompositorPort

 class GpuBackend(CompositingBackend):
-    def __init__(self):
+    def __init__(self, compositor: CompositorPort):
         if not HAS_GPU_BACKEND:
             raise ImportError("CuPy not installed or GPU not available")
-        self.compositor = CupyCompositor()
+        self.compositor = compositor
```

---

### 4. Refactor Mask Module

#### [MODIFY] [mask\_generator\_module.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/animator/mask_generator_module.py)

**Current violation (line 32):**
```python
from src.adapters.driven.pillow_image_adapter import PillowImageAdapter
```

**Fix:** Remove default adapter initialization. Functions already accept `image_processor` parameter. Remove the global default:
```diff
-_default_image_processor: Optional[ImageProcessingPort] = None

-def get_default_processor() -> ImageProcessingPort:
-    global _default_image_processor
-    if _default_image_processor is None:
-        from src.adapters.driven.pillow_image_adapter import PillowImageAdapter
-        _default_image_processor = PillowImageAdapter()
-    return _default_image_processor

 def generate_reveal_mask(..., image_processor: ImageProcessingPort) -> Any:
     # Make image_processor required, no default fallback
```

> [!IMPORTANT]
> This is a **breaking change** for callers that rely on default processor. Callers must now pass `image_processor` explicitly.

---

### 5. Update Module Imports

Scan domain modules and update any direct entity/VO imports to use `domain.core`. Most already use relative imports which is acceptable. Focus on standardizing.

---

## Verification Plan

### Automated Tests

**Command to run existing tests:**
```bash
cd /home/rakaarwaky/Work/App\ Project/client-app/engine && python -m pytest tests/ -v
```

**Expected:** All tests pass. The test `test_domain_entities_new.py` validates entity/VO behavior.

### Import Verification

```bash
cd /home/rakaarwaky/Work/App\ Project/client-app/engine && python -c "from src.domain.core import *; print('Gateway OK')"
```

### Manual Verification

If the full render test needs to run:
```bash
cd /home/rakaarwaky/Work/App\ Project/client-app/engine && python tests/full_render_test.py
```

> [!WARNING]
> `full_render_test.py` requires GPU dependencies (CuPy). May skip if not available.
