# Agent Task List: RefactoringSpecialist

## 1. 🦅 Eagle View
This project is **Client-App Refactor**, focusing on splitting Engine and Client and enforcing Hexagonal Architecture.
- **Architect**: High-level design and final wiring.
- **RefactoringSpecialist**: Code modifications and interface extraction.
- **QA**: Verification.

## 2. Tasks (Topologically Sorted)

### Task: refactor_core_exports
**Complexity:** 2 | **Dependencies:** audit_analysis

**Description:**
Update `engine/src/domain/core/__init__.py` to export all Entities, Value Objects, and Ports. This creates the 'Gateway'.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).

### Task: define_ports
**Complexity:** 2 | **Dependencies:** audit_analysis

**Description:**
Define `CompositorPort` and `ImageAdapterPort` in `engine/src/domain/ports/`. These interfaces decouple modules from adapters.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).

### Task: update_module_imports
**Complexity:** 4 | **Dependencies:** refactor_core_exports

**Description:**
Scan all domain modules and update imports to use `domain.core` instead of direct file paths for entities/VOs.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).

### Task: refactor_gpu_module
**Complexity:** 3 | **Dependencies:** define_ports

**Description:**
Refactor `pipeline_manager/gpu_backend_module.py` to use `CompositorPort` via dependency injection instead of concrete import.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).

### Task: refactor_mask_module
**Complexity:** 3 | **Dependencies:** define_ports

**Description:**
Refactor `animator/mask_generator_module.py` to use `ImageAdapterPort` via dependency injection.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).
