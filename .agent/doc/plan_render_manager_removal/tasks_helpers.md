# Tasks: Helpers Agent

## 1. 🦅 Eagle View

**Project:** client-app (timelapse video generation engine)
**Task:** Remove `render_manager`, migrate to `pipeline_manager`
**5 Parallel Agents:** Config, Engine, Pipeline, Strategies, Helpers

**Your focus:** Helper modules (`cursor_overlay`, `ui_helper`, `parallel_renderer`)
**NOT your concern:** config, DirectorEngine, RenderPipeline, strategies

## 2. Role & Scope

| Migrate | Update Imports For |
|---------|-------------------|
| `cursor_overlay.py`, `ui_helper.py`, `parallel_renderer.py` | `CursorOverlay`, `build_ui_layer_list` |

## 3. Tasks

### Task 1: Create cursor_overlay.py
**Target:** `pipeline_manager/cursor_overlay.py`

Copy from `render_manager/cursor_overlay_module.py`

No import changes needed (standalone).

---

### Task 2: Create ui_helper.py
**Target:** `pipeline_manager/ui_helper.py`

Copy from `render_manager/ui_helper.py`

No import changes needed (standalone).

---

### Task 3: Create parallel_renderer.py
**Target:** `pipeline_manager/parallel_renderer.py`

Copy from `render_manager/parallel_renderer.py`

Update internal imports if needed.

---

### Task 4: Add helper exports to __init__.py
**Target:** `pipeline_manager/__init__.py`

Add lines:
```python
from .cursor_overlay import CursorOverlay
from .ui_helper import build_ui_layer_list
```

Add to `__all__`:
```python
"CursorOverlay", "build_ui_layer_list",
```

---

## 4. Verification

```bash
python -c "from src.domain.modules.pipeline_manager import CursorOverlay; print('✅ Helpers OK')"
python -c "from src.domain.modules.pipeline_manager.ui_helper import build_ui_layer_list; print('✅ UI Helper OK')"
```

## 5. Completion Signal

```
✅ HELPERS_AGENT_DONE
```
