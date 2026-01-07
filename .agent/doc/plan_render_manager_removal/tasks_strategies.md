# Tasks: Strategies Agent

## 1. 🦅 Eagle View

**Project:** client-app (timelapse video generation engine)
**Task:** Remove `render_manager`, migrate to `pipeline_manager`
**5 Parallel Agents:** Config, Engine, Pipeline, Strategies, Helpers

**Your focus:** Render strategies (`CPURenderStrategy`, `OptimizedRenderStrategy`, `GPURenderStrategy`)
**NOT your concern:** config, DirectorEngine, RenderPipeline, helpers

## 2. Role & Scope

| Migrate | Update Imports For |
|---------|-------------------|
| `strategies/*.py` | `CPURenderStrategy`, `OptimizedRenderStrategy`, `GPURenderStrategy` |

## 3. Tasks

### Task 1: Create strategies/ folder
**Target:** `pipeline_manager/strategies/`

Create folder structure:
```
pipeline_manager/strategies/
├── __init__.py
├── cpu_strategy.py
├── optimized_strategy.py
└── gpu_strategy.py
```

---

### Task 2: Create cpu_strategy.py
Copy from `render_manager/cpu_render_strategy.py`

Update imports:
```python
from ..config import EngineState, RenderConfig
from ..ui_helper import build_ui_layer_list
```

---

### Task 3: Create optimized_strategy.py
Copy from `render_manager/optimized_render_strategy.py`

Update imports:
```python
from ..config import EngineState, RenderConfig
from ..ui_helper import build_ui_layer_list
from ..pipeline_manager_module import PipelineManager, CompositeConfig
from ..cursor_overlay import CursorOverlay
```

---

### Task 4: Create gpu_strategy.py
Copy from `render_manager/gpu_render_strategy.py`

Update imports accordingly.

---

### Task 5: Create strategies/__init__.py
```python
from .cpu_strategy import CPURenderStrategy
from .optimized_strategy import OptimizedRenderStrategy
from .gpu_strategy import GPURenderStrategy

__all__ = ["CPURenderStrategy", "OptimizedRenderStrategy", "GPURenderStrategy"]
```

---

### Task 6: Add strategies to pipeline_manager/__init__.py
Add line:
```python
from .strategies import CPURenderStrategy, OptimizedRenderStrategy, GPURenderStrategy
```

Add to `__all__`:
```python
"CPURenderStrategy", "OptimizedRenderStrategy", "GPURenderStrategy",
```

---

### Task 7: Update test files
**Target:** `engine/tests/custom/verify_modules.py`

```diff
-from src.domain.modules.render_manager.gpu_render_strategy import GPURenderStrategy
+from src.domain.modules.pipeline_manager.strategies import GPURenderStrategy
```

**Target:** `engine/tests/benchmark_gpu_vs_cpu.py`

Update strategy imports.

---

## 4. Verification

```bash
python -c "from src.domain.modules.pipeline_manager.strategies import CPURenderStrategy, GPURenderStrategy, OptimizedRenderStrategy; print('✅ Strategies OK')"
```

## 5. Completion Signal

```
✅ STRATEGIES_AGENT_DONE
```
