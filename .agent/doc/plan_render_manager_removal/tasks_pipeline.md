# Tasks: Pipeline Agent

## 1. 🦅 Eagle View

**Project:** client-app (timelapse video generation engine)
**Task:** Remove `render_manager`, migrate to `pipeline_manager`
**5 Parallel Agents:** Config, Engine, Pipeline, Strategies, Helpers

**Your focus:** `RenderPipeline` component
**NOT your concern:** config, DirectorEngine, strategies, helpers

## 2. Role & Scope

| Migrate | Update Imports For |
|---------|-------------------|
| `render_pipeline.py` | `RenderPipeline`, `PipelineState`, `PipelineProgress`, `PipelineConfig` |

## 3. Tasks

### Task 1: Create render_pipeline.py
**Target:** `pipeline_manager/render_pipeline.py`

Copy from `render_manager/progress_tracker_module.py`:
- `PipelineState` (Enum)
- `PipelineProgress` (dataclass)
- `PipelineConfig` (dataclass)
- `RenderPipeline` class
- `ProgressCallback` type alias

Update internal imports to use `pipeline_manager` paths.

---

### Task 2: Add Pipeline exports to __init__.py
**Target:** `pipeline_manager/__init__.py`

Add lines:
```python
from .render_pipeline import RenderPipeline, PipelineState, PipelineProgress, PipelineConfig
```

Add to `__all__`:
```python
"RenderPipeline", "PipelineState", "PipelineProgress", "PipelineConfig",
```

---

### Task 3: Update modules/__init__.py
**Target:** `engine/src/domain/modules/__init__.py`

Change ONLY Pipeline-related imports:
```diff
-from .render_manager import (
-    ...
-    RenderPipeline, PipelineConfig, PipelineState, PipelineProgress,
-)
+from .pipeline_manager import RenderPipeline, PipelineConfig, PipelineState, PipelineProgress
```

---

## 4. Verification

```bash
python -c "from src.domain.modules.pipeline_manager import RenderPipeline, PipelineState, PipelineConfig; print('✅ Pipeline OK')"
```

## 5. Completion Signal

```
✅ PIPELINE_AGENT_DONE
```
