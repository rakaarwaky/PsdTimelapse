# Architecture Audit Report

**Date:** 2026-01-06  
**Auditor:** Architect Agent  
**Goal:** Identify Hexagonal Architecture violations in `engine/src/domain`

---

## Executive Summary

Found **2 critical violations** where domain modules directly import infrastructure adapters, breaking the Hexagonal Architecture boundary.

---

## Violations Detected

### 1. `gpu_backend_module.py` — Direct Adapter Import

| Property | Value |
|----------|-------|
| **File** | [gpu_backend_module.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/pipeline_manager/gpu_backend_module.py) |
| **Line** | 11 |
| **Violation** | `from src.adapters.driven.renderers.gpu.cupy_compositor import CupyCompositor` |
| **Severity** | 🔴 Critical |

**Analysis:** The module directly imports `CupyCompositor` from the adapters layer. This couples the domain to infrastructure.

**Required Fix:** 
- Create/use `GpuCompositorPort` interface in `domain/ports/`
- Module should depend on the port, not the concrete adapter

---

### 2. `mask_generator_module.py` — Direct Adapter Import

| Property | Value |
|----------|-------|
| **File** | [mask_generator_module.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/animator/mask_generator_module.py) |
| **Line** | 32 |
| **Violation** | `from src.adapters.driven.pillow_image_adapter import PillowImageAdapter` |
| **Severity** | 🔴 Critical |

**Analysis:** The `get_default_processor()` function instantiates `PillowImageAdapter` directly. This breaks inversion of control.

**Required Fix:**
- Remove the lazy initialization of adapter in domain
- Inject `ImageProcessingPort` from application layer (Core/Engine)

---

## Architecture Rules Reference

### Module Rules
> Modules MUST be agnostic. They depend on `core` for `entities` and `value_objects`, and use `ports` for external dependencies.

### Core Gateway Rules
> Core SHOULD act as a gateway: only accessing `modules`, `entities`, `value_objects`, and `ports`.

---

## Current Correct Patterns (Examples)

✅ **render_manager_module.py** — Uses port injection correctly:
```python
from ...ports.psd_port import PsdPort
from ...ports.renderer_port import RendererPort
# Ports are injected via constructor, not created internally
```

---

## Task Handoff

| Remediation Task | Assignee | Dependencies |
|-----------------|----------|--------------|
| `define_ports` | RefactoringSpecialist | `audit_analysis` ✅ |
| `refactor_gpu_module` | RefactoringSpecialist | `define_ports` |
| `refactor_mask_module` | RefactoringSpecialist | `define_ports` |
| `wire_dependencies` | Architect | 3 refactor tasks |

---

## Verification Command

To verify no adapters are imported in domain:
```bash
grep -r "from src.adapters" engine/src/domain/
# Expected output after fixes: (no results)
```
