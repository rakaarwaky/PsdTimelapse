# Fix Failing Engine Tests

## Problem Summary

7 test files were run, **4 failed** with critical errors:

| Test File | Status | Root Cause |
|-----------|--------|------------|
| `final_render_test.py` | ✅ PASS | - |
| `brush_reveal_path_variations_test.py` | ✅ PASS | - |
| `brush_reveal_multi_object_test.py` | ❌ FAIL | `animator_module.py:30` - AttributeError |
| `brush_reveal_easing_showcase_test.py` | ❌ FAIL | `animator_module.py:30` - AttributeError |
| `benchmark_gpu_vs_cpu.py` | ❌ FAIL | Import from deleted `render_manager` |
| `render_frames_debug.py` | ❌ FAIL | `animator_module.py:30` - AttributeError |
| `debug_frames_test.py` | ✅ PASS | - |

---

## Computational Analysis

```
Total Tasks: 2
Total Edges (Dependencies): 0
Execution Mode: 100% PARALLEL
Total Complexity Score: 5/10
```

```mermaid
graph TD
    T1[fix_animator_initialize_layers]
    T2[fix_benchmark_import_path]
    
    style T1 fill:#4CAF50,stroke:#2E7D32,color:white
    style T2 fill:#2196F3,stroke:#1565C0,color:white
```

> [!NOTE]
> **No Edges = No Dependencies.** Both tasks can execute simultaneously.

---

## Task Overview

### Task 1: `fix_animator_initialize_layers`

| Property | Value |
|----------|-------|
| **File** | `src/domain/modules/animator/animator_module.py` |
| **Complexity** | 2/5 (Simple logic fix) |
| **Impact** | Fixes 3 tests |

**Issue:** Method `initialize_layers()` at line 30 expects `LayerEntity` objects but tests pass string IDs directly:

```python
# Current (Broken)
def initialize_layers(self, layers: List[Any]):
    for layer in layers:
        lid = layer.id  # ❌ Fails when layer is already a string!
```

**Solution:** Add type check to handle both cases:

```python
# Fixed
def initialize_layers(self, layers: List[Any]):
    for layer in layers:
        lid = layer if isinstance(layer, str) else layer.id  # ✅
```

---

### Task 2: `fix_benchmark_import_path`

| Property | Value |
|----------|-------|
| **File** | `tests/benchmark_gpu_vs_cpu.py` |
| **Complexity** | 3/5 (Requires API mapping) |
| **Impact** | Fixes 1 test |

**Issue:** Imports from deleted module:

```python
# Current (Broken)
from src.domain.modules.render_manager.render_manager_module import (
    DirectorEngine,
    RenderConfig,
    EngineProgress,
)
```

**Solution:** Update to use `pipeline_manager`:

```python
# Fixed
from src.domain.modules.pipeline_manager.director_engine import DirectorEngine
from src.domain.modules.pipeline_manager.config import RenderConfig
from src.domain.core.engine import EngineProgress
```

> [!IMPORTANT]
> Need to verify exact class locations in `pipeline_manager` before implementing.

---

## Verification Plan

### Automated Tests

```bash
# Run all previously failing tests
python -m pytest tests/brush_reveal_multi_object_test.py \
                 tests/brush_reveal_easing_showcase_test.py \
                 tests/render_frames_debug.py \
                 tests/benchmark_gpu_vs_cpu.py -v

# Run as standalone scripts (original test method)
source venv/bin/activate && python tests/brush_reveal_multi_object_test.py
source venv/bin/activate && python tests/benchmark_gpu_vs_cpu.py
```

### Acceptance Criteria

- [ ] `animator_module.py` handles both `str` and `LayerEntity` inputs
- [ ] `benchmark_gpu_vs_cpu.py` imports from correct module paths
- [ ] All 7 test files pass without errors
- [ ] No regressions in `final_render_test.py` (current passing test)
