# Tasks: Config Agent

## 1. 🦅 Eagle View

**Project:** client-app (timelapse video generation engine)
**Task:** Remove `render_manager`, migrate to `pipeline_manager`
**5 Parallel Agents:** Config, Engine, Pipeline, Strategies, Helpers

**Your focus:** `config.py` component (EngineState, RenderConfig, EngineProgress)
**NOT your concern:** DirectorEngine, RenderPipeline, strategies, helpers

## 2. Role & Scope

| Migrate | Update Imports For |
|---------|-------------------|
| `config.py` | `EngineState`, `RenderConfig`, `EngineProgress` |

## 3. Tasks

### Task 1: Create config.py
**Target:** `pipeline_manager/config.py`

Copy from `render_manager/config.py`:
- `EngineState` (Enum)
- `EngineProgress` (dataclass)
- `RenderConfig` (dataclass)

---

### Task 2: Add config imports to __init__.py
**Target:** `pipeline_manager/__init__.py`

Add line:
```python
from .config import EngineState, EngineProgress, RenderConfig
```

Add to `__all__`:
```python
"EngineState", "EngineProgress", "RenderConfig",
```

---

### Task 3: Update core/__init__.py
**Target:** `engine/src/domain/core/__init__.py`

Change ONLY the config-related imports:
```diff
-from ..modules.render_manager import (
-    ...
-    EngineState,
-    RenderConfig,
-    EngineProgress,
-    ...
-)
+# Config imports handled by pipeline_manager
+from ..modules.pipeline_manager import EngineState, RenderConfig, EngineProgress
```

> Note: Leave other imports (DirectorEngine, RenderPipeline) for other agents

---

## 4. Verification

```bash
python -c "from src.domain.modules.pipeline_manager import EngineState, RenderConfig, EngineProgress; print('✅ Config OK')"
```

## 5. Completion Signal

```
✅ CONFIG_AGENT_DONE
```
