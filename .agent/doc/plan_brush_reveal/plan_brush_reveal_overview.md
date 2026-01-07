# Feature Plan: Brush Reveal Effect

**Goal:** Implement progressive reveal masking in `FrameCompositor` so layers "wipe in" during Brush actions instead of appearing instantly.

---

## Computational Analysis

```python
# Independence Validation (Required by /plan workflow)
import networkx as nx

G = nx.DiGraph()

# Tasks as Independent Nodes (NO EDGES)
tasks = [
    "create_reveal_op",      # New reveal_op.py module
    "modify_compositor",     # Integrate mask in compositor_module.py
    "verify_test"            # Run existing brush_reveal_test.py
]
G.add_nodes_from(tasks)

# CRITICAL: Validate Zero Dependencies
assert G.number_of_edges() == 0, f"Error: Dependencies detected! {G.edges()}"
print(f"✅ All {len(tasks)} tasks are PARALLEL (0 edges)")
```

**Output:**

| Metric | Value |
|--------|-------|
| Total Tasks | 3 |
| Dependencies | **0** (Pure Parallel) |
| Execution Mode | SIMULTANEOUS |
| Complexity Sum | 6 |

---

## Task Map

```mermaid
graph TD
    A[create_reveal_op]
    B[modify_compositor]
    C[verify_test]
    %% NO ARROWS - All Independent
    style A stroke-dasharray: 5 5
    style B stroke-dasharray: 5 5
    style C stroke-dasharray: 5 5
```

---

## Tasks (Simultaneous Execution)

### Task 1: Create Reveal Op Module

**Complexity:** 2 | **Dependencies:** NONE

**File:** [NEW] [reveal_op.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/compositor/reveal_op.py)

**Description:**
Create `apply_reveal_mask(image: Image, progress: float) -> Image` function:
- Input: PIL Image + progress (0.0 to 1.0)
- Logic: Horizontal wipe left-to-right based on progress
- Returns: Masked image where width × progress is visible

**Acceptance:**
- [ ] Function signature matches spec
- [ ] Returns original image when progress >= 1.0
- [ ] Returns fully transparent when progress <= 0.0

---

### Task 2: Modify Compositor Module

**Complexity:** 3 | **Dependencies:** NONE

**File:** [MODIFY] [compositor_module.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/src/domain/modules/compositor/compositor_module.py)

**Description:**
1. Import `apply_reveal_mask` from `.reveal_op`
2. In `compose_psd_content` (after opacity op, line ~65):
   - Check if `state.reveal_progress < 1.0` exists
   - If so, apply: `img = apply_reveal_mask(img, state.reveal_progress)`
3. In `compose_from_render_states` (after opacity op, line ~135):
   - Same logic using `state.reveal_progress`

**Acceptance:**
- [ ] Import added at top
- [ ] Mask applied AFTER opacity, BEFORE blur
- [ ] Graceful handling when `reveal_progress` attribute missing

---

### Task 3: Verify with Existing Test

**Complexity:** 1 | **Dependencies:** NONE

**File:** [brush_reveal_test.py](file:///home/rakaarwaky/Work/App%20Project/client-app/engine/tests/brush_reveal_test.py)

**Description:**
Run existing test to visually verify layers "wipe in" sequentially.

**Acceptance:**
- [ ] Test runs without errors
- [ ] Output video shows progressive reveal animation
- [ ] Objects don't appear all at once

---

## Verification Plan

### Automated Tests

**Command:**
```bash
cd /home/rakaarwaky/Work/App\ Project/client-app/engine
source venv/bin/activate  # If using venv
python tests/brush_reveal_test.py
```

**Expected Output:**
- `tests/outputs/brush_reveal/brush_reveal_test_001.webm`
- `tests/outputs/brush_reveal/brush_reveal_test_001.gif`

### Visual Verification

Watch the output video and confirm:
1. Green rectangle wipes in from left (0s-3s)
2. Yellow box wipes in from left (3s-5s)  
3. Magenta box wipes in from left (5s-7s)

> [!IMPORTANT]
> Current test exists but does NOT validate reveal_progress. The visual check is manual after implementation.

---

## State Machine: Reveal Op

| Current | Trigger | Next | Action |
|---------|---------|------|--------|
| IDLE | progress > 0 | REVEALING | Start mask |
| REVEALING | progress < 1 | REVEALING | Update mask width |
| REVEALING | progress >= 1 | COMPLETE | Return full image |
| COMPLETE | - | - | No-op |
