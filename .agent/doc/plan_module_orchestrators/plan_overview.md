# Module Orchestrator Upgrade Plan

## Executive Summary

Upgrade all 5 module `__init__.py` files from simple index/re-exports to **intelligent orchestrators** with:
- Factory methods for creating pre-configured instances
- Validation logic for internal consistency
- Clear public API with hidden internals
- Dependency injection support

---

## Computational Analysis

```
Total Tasks: 5
Total Edges (Dependencies): 0
Execution Mode: 100% PARALLEL
Total Internal Files: 36
Total Complexity Score: 15/25
```

```mermaid
graph TD
    AN[upgrade_animator_orchestrator]
    CO[upgrade_compositor_orchestrator]
    SD[upgrade_script_director_orchestrator]
    PM[upgrade_pipeline_manager_orchestrator]
    LM[upgrade_layout_manager_orchestrator]
    
    style AN fill:#4CAF50,stroke:#2E7D32,color:white
    style CO fill:#2196F3,stroke:#1565C0,color:white
    style SD fill:#4CAF50,stroke:#2E7D32,color:white
    style PM fill:#2196F3,stroke:#1565C0,color:white
    style LM fill:#4CAF50,stroke:#2E7D32,color:white
```

> [!NOTE]
> **No arrows = No dependencies.** All 5 tasks execute simultaneously.

---

## Agent Allocation

| Agent | Modules | Complexity |
|-------|---------|------------|
| **ModuleArchitect_A** | animator, script_director, layout_manager | 6/15 |
| **ModuleArchitect_B** | compositor, pipeline_manager | 9/15 |

---

## Orchestrator Pattern (Target Architecture)

Each module `__init__.py` will follow this pattern:

```python
"""
{ModuleName} Orchestrator
=========================

Intelligent facade that coordinates all internal components.

Public API:
-----------
- {MainClass}: Primary orchestrator class
- create_{module}(): Factory with default configuration
- {module}_from_config(): Factory with custom configuration

Internal (DO NOT IMPORT DIRECTLY):
----------------------------------
- All *_module.py files
- All *_op.py files  
- All *_strategy.py files
"""

from typing import Optional, Any
from dataclasses import dataclass

# --- Configuration ---
@dataclass
class {Module}Config:
    """Configuration for {Module} orchestrator."""
    # Module-specific settings
    pass

# --- Factory Functions ---
def create_{module}(**kwargs) -> "{MainClass}":
    """
    Factory: Create {Module} with sensible defaults.
    
    Usage:
        orchestrator = create_{module}()
    """
    config = {Module}Config(**kwargs)
    return {MainClass}(config)

# --- Main Orchestrator Class ---
class {MainClass}:
    """
    Central orchestrator for {Module}.
    
    Coordinates:
    - [List internal responsibilities]
    """
    
    def __init__(self, config: Optional[{Module}Config] = None):
        self.config = config or {Module}Config()
        self._initialize_internals()
    
    def _initialize_internals(self):
        \"\"\"Wire up internal components.\"\"\"
        # Lazy imports to avoid circular dependencies
        from .internal_module import InternalClass
        self._internal = InternalClass()

# --- Public Exports ---
__all__ = [
    # Orchestrator
    '{MainClass}',
    '{Module}Config',
    # Factories
    'create_{module}',
    # Key types (minimal)
    # ...
]
```

---

## Orchestrator Capabilities

Each upgraded `__init__.py` will have:

| Capability | Description |
|------------|-------------|
| **Factory Methods** | `create_X()` for default instantiation |
| **Config Dataclass** | Type-safe configuration object |
| **Lazy Imports** | Internal imports inside methods (no circular deps) |
| **Validation** | `validate()` method to check internal consistency |
| **Clear Docstring** | Public vs Internal API clearly documented |
| **Minimal __all__** | Only expose what external code needs |

---

## Verification Plan

### Automated Tests

```bash
# Import test - ensure all modules can be imported
python -c "from src.domain.modules.animator import *; print('animator OK')"
python -c "from src.domain.modules.compositor import *; print('compositor OK')"
python -c "from src.domain.modules.script_director import *; print('script_director OK')"
python -c "from src.domain.modules.pipeline_manager import *; print('pipeline_manager OK')"
python -c "from src.domain.modules.layout_manager import *; print('layout_manager OK')"

# Run existing tests to ensure no regression
python -m pytest tests/ -v --tb=short
```

### Acceptance Criteria

- [ ] All 5 `__init__.py` files upgraded to orchestrator pattern
- [ ] Factory functions work for each module
- [ ] No circular import errors
- [ ] All 7 original tests still pass
- [ ] `engine.py` can use new orchestrator APIs

---

## Files to Modify

| Module | File | Current Lines | Target Lines |
|--------|------|---------------|--------------|
| animator | `__init__.py` | 52 | ~80 |
| compositor | `__init__.py` | 44 | ~90 |
| script_director | `__init__.py` | 40 | ~70 |
| pipeline_manager | `__init__.py` | 37 | ~100 |
| layout_manager | `__init__.py` | 15 | ~50 |
