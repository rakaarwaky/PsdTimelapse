# Agent: GPU Strategy Refactoring

## 1. 🦅 Eagle View

This project is **Psd Timelapse Engine**, a domain-driven rendering pipeline. Current feature: **Compliance Refactoring** to enforce "Blind Logic" pattern. System has 3 agents:
- **Agent Composition**: Remove PIL imports from `layer_composition_module.py`
- **Agent GPU Strategy**: Inject GpuBackend instead of internal import
- **Agent Strategy Factories**: Add factory injection for AnimationController/FrameCompositor

**Your focus:** Agent GPU Strategy. You run **IN PARALLEL** with others. DO NOT wait for them.

---

## 2. Role

**GPU Strategy Refactor Agent** - Inject GpuBackend via constructor instead of internal import.

**Responsibilities:**
- Remove internal `from .gpu_backend_module import GpuBackend`
- Add `backend` parameter to `initialize()` method
- Update `DirectorEngine` to inject backend

**Constraints:**
- Must not break GPU rendering flow
- Must not wait for other agents
- Changes in `gpu_strategy_module.py` and `director_engine_module.py`

---

## 3. Interface Contracts

**Input (From DirectorEngine):**
```json
{
  "gpu_port": "GpuRendererPort",
  "ui_renderer_factory": "Callable",
  "compositor": "CompositorPort",
  "backend": "GpuBackend (injected)"
}
```

**Output (Unchanged):**
```json
{
  "output_path": "str"
}
```

---

## 4. Task Map

```mermaid
graph TD
    T4[Remove Backend Import]
    T5[Add backend to initialize]
    T6[Update DirectorEngine]
    style T4 stroke-dasharray: 5 5
    style T5 stroke-dasharray: 5 5
    style T6 stroke-dasharray: 5 5
```

---

## 5. Tasks (Simultaneous)

### Task 4: Remove Internal Backend Import
**Complexity:** 2 | **Dependencies:** NONE

**Description:** 
Remove line 78 inside `execute()` method:
```python
# DELETE THIS (inside execute method):
from .gpu_backend_module import GpuBackend
backend = GpuBackend(self.compositor_port)
```

Replace with:
```python
backend = self.backend
```

**Acceptance:**
- [ ] No internal `from .gpu_backend_module` inside method
- [ ] Uses `self.backend` instead

---

### Task 5: Add backend to initialize()
**Complexity:** 3 | **Dependencies:** NONE

**Description:**
Update `GPURenderStrategy.initialize()` signature:

```diff
def initialize(
    self, 
    gpu_port: GpuRendererPort, 
    ui_renderer_factory: Callable[[], Any], 
-   compositor: Optional[CompositorPort] = None
+   compositor: Optional[CompositorPort] = None,
+   backend: Any = None
):
    self.gpu_port = gpu_port
    self.ui_renderer_factory = ui_renderer_factory
    self.compositor_port = compositor
+   self.backend = backend
```

**Acceptance:**
- [ ] `backend` parameter added
- [ ] `self.backend` assigned

---

### Task 6: Update DirectorEngine Injection
**Complexity:** 4 | **Dependencies:** NONE

**Description:**
In `director_engine_module.py`, update `run_gpu()` to inject backend:

```diff
def run_gpu(self, config: RenderConfig) -> str:
    ...
+   # Create backend via factory or injection
+   from ..rendering.gpu_backend_module import GpuBackend
+   backend = GpuBackend(self.compositor_port) if self.compositor_port else None
    
    strategy = GPURenderStrategy(self.world)
    if hasattr(strategy, 'initialize'):
-       strategy.initialize(self.gpu_renderer_port, self.ui_renderer_factory, self.compositor_port)
+       strategy.initialize(self.gpu_renderer_port, self.ui_renderer_factory, self.compositor_port, backend)
```

**Acceptance:**
- [ ] Backend created in DirectorEngine (Level 2 Manager)
- [ ] Passed to strategy via initialize()

---

## 6. Verification

```bash
# Run integration tests
cd engine/src/domain/modules/pipeline_manager/scenario
python -m pytest integration/test_05_director_integration.py -v
python -m pytest benchmark/test_benchmark_gpu_vs_cpu.py -v
```
