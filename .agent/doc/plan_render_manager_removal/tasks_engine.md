# Tasks: Engine Agent

## 1. 🦅 Eagle View

**Project:** client-app (timelapse video generation engine)
**Task:** Remove `render_manager`, migrate to `pipeline_manager`
**5 Parallel Agents:** Config, Engine, Pipeline, Strategies, Helpers

**Your focus:** `DirectorEngine` component
**NOT your concern:** config, RenderPipeline, strategies, helpers

## 2. Role & Scope

| Migrate | Update Imports For |
|---------|-------------------|
| `director_engine.py` | `DirectorEngine` |

## 3. Tasks

### Task 1: Create director_engine.py
**Target:** `pipeline_manager/director_engine.py`

Copy from `render_manager/render_manager_module.py`:
- `DirectorEngine` class only
- `ProgressCallback` type alias

Update internal imports:
```python
from .config import EngineState, EngineProgress, RenderConfig
from .strategies.cpu_strategy import CPURenderStrategy
from .strategies.optimized_strategy import OptimizedRenderStrategy
from .strategies.gpu_strategy import GPURenderStrategy
```

---

### Task 2: Add DirectorEngine to __init__.py
**Target:** `pipeline_manager/__init__.py`

Add line:
```python
from .director_engine import DirectorEngine
```

Add to `__all__`:
```python
"DirectorEngine",
```

---

### Task 3: Update core/engine.py
**Target:** `engine/src/domain/core/engine.py`

Change ONLY DirectorEngine import:
```diff
-from ..modules.render_manager import (
-    DirectorEngine,
-    ...
-)
+from ..modules.pipeline_manager import DirectorEngine
```

---

### Task 4: Update main.py
**Target:** `engine/main.py`

```diff
-from src.domain.modules.render_manager import DirectorEngine
+from src.domain.modules.pipeline_manager import DirectorEngine
```

---

### Task 5: Update verify_modules.py
**Target:** `engine/tests/custom/verify_modules.py`

```diff
-from src.domain.modules.render_manager import DirectorEngine
+from src.domain.modules.pipeline_manager import DirectorEngine
```

---

## 4. Verification

```bash
python -c "from src.domain.modules.pipeline_manager import DirectorEngine; print('✅ Engine OK')"
```

## 5. Completion Signal

```
✅ ENGINE_AGENT_DONE
``` 

## Task Progress
- [x] Task 1: Create director_engine.py
- [x] Task 2: Add DirectorEngine to __init__.py
- [x] Task 3: Update core/engine.py
- [x] Task 4: Update main.py
- [x] Task 5: Update verify_modules.py
