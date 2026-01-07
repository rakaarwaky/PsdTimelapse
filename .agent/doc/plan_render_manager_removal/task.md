# Task: Remove `render_manager` → Migrate to `pipeline_manager`

## True Parallel Structure (5 Agents)

| Agent | Component | Dependencies |
|-------|-----------|--------------|
| 🟢 **Config** | config.py | NONE |
| 🔵 **Engine** | director_engine.py | NONE |
| 🟣 **Pipeline** | render_pipeline.py | NONE |
| 🟠 **Strategies** | strategies/*.py | NONE |
| 🔴 **Helpers** | cursor, ui_helper, parallel | NONE |

**ALL agents dapat berjalan PARALLEL tanpa menunggu satu sama lain.**

---

## Agent: Config
- [x] Create `pipeline_manager/config.py`
- [x] Add exports to `__init__.py`
- [x] Update `core/__init__.py` (EngineState, RenderConfig, EngineProgress only)

## Agent: Engine
- [x] Create `pipeline_manager/director_engine.py`
- [x] Add exports to `__init__.py`
- [x] Update `core/engine.py`, `main.py`, `verify_modules.py`

## Agent: Pipeline
- [x] Create `pipeline_manager/render_pipeline.py`
- [x] Add exports to `__init__.py`
- [x] Update `modules/__init__.py`

## Agent: Strategies
- [x] Create `pipeline_manager/strategies/` folder (4 files)
- [x] Add exports to `__init__.py`
- [x] Update test files

## Agent: Helpers
- [x] Create `pipeline_manager/cursor_overlay.py`
- [x] Create `pipeline_manager/ui_helper.py`
- [x] Create `pipeline_manager/parallel_renderer.py`
- [x] Add exports to `__init__.py`

---

## Final Step (After All Agents Done)
- [x] Delete `render_manager/` folder
- [x] Run verification tests
