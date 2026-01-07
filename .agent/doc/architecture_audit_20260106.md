# Domain Architecture Audit & Knowledge Base
**Date:** 2026-01-06
**Status:** DRAFT (Audit Phase)

## 1. Core Architectural Principles
The `engine/src/domain` layer must strictly adhere to **Hexagonal Architecture** with the following specific rules:

### Rule 1: Modules Are Agnostic
- **Constraint:** Domain Modules (`domain/modules/*`) MUST NOT depend on Infrastructure (`adapters/*`).
- **Implementation:** 
  - No `import src.adapters...` statements allowed in modules.
  - If a module needs external capability (e.g., GPU compositing), it must define a **Port** (Interface).
  - The concrete Adapter is injected by `Core` at runtime.

### Rule 2: Core is the Gateway
- **Constraint:** Modules should not treat `entities`, `value_objects`, or `ports` as public APIs directly.
- **Implementation:**
  - **Core** (`domain/core`) is the owner of the domain.
  - Core imports and re-exports authorized Entities, Value Objects, and Ports.
  - **Modules** must import these dependencies FROM `domain.core`, not from the file structure directly.
  - *Current Status:* Core needs update to support this (currently does not export entities).

---

## 2. Compliance Audit (Findings)
As of investigation on Jan 6, 2026, the following violations exist:

### A. Infrastructure Leakage (Violation of Rule 1)
Modules found importing concrete adapters directly:
1. **`pipeline_manager/gpu_backend_module.py`**
   - *Import:* `from src.adapters.driven.renderers.gpu.cupy_compositor import CupyCompositor`
   - *Impact:* Hard dependency on a specific driver. Tightly couples domain to implementation.
2. **`animator/mask_generator_module.py`**
   - *Import:* `from src.adapters.driven.pillow_image_adapter import PillowImageAdapter`
   - *Impact:* Hard dependency on Pillow adapter.

### B. Bypass of Core Gateway (Violation of Rule 2)
Modules currently import entities directly from the file system because `domain/core` does not expose them.
- *Example:* `from ...entities.world_entity import WorldEntity`
- *Target:* Should be `from ...core import WorldEntity`

---

## 3. Remediation Plan (Knowledge Transfer)
To align the codebase with the architectural vision, the following refactoring steps are required:

### Step 1: Fortify Core Exports
Update `engine/src/domain/core/__init__.py` to be the single source of truth:
```python
# engine/src/domain/core/__init__.py

# 1. Export Entities & Value Objects
from ..entities.world_entity import WorldEntity
from ..value_objects.vector import Vector2
# ... etc

# 2. Export Ports
from ..ports.renderer_port import RendererPort
# ... etc

__all__ = ["WorldEntity", "Vector2", "RendererPort", ...]
```

### Step 2: Invert Dependencies in Modules
Refactor violating modules to use Injection instead of Import.

**Before (Violation):**
```python
# gpu_backend_module.py
from src.adapters... import CupyCompositor # BAD

class GpuBackend:
    def __init__(self):
        self.impl = CupyCompositor() # BAD
```

**After (Compliant):**
```python
# gpu_backend_module.py
# No adapter imports!

class GpuBackend:
    def __init__(self, compositor_impl: CompositorPort): # INJECTED
        self.impl = compositor_impl
```

**Wiring (in Core):**
```python
# engine.py (Core)
from src.adapters... import CupyCompositor # OK (Core wires dependencies)

def initialize_system(self):
    backend = GpuBackend(compositor_impl=CupyCompositor())
```
