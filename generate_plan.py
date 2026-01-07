import networkx as nx
import os
import json

# 1. Define Plan Structure
PLAN_DIR = ".agent/doc/plan_smart_director_render_fix"
os.makedirs(PLAN_DIR, exist_ok=True)

# 2. Build Independent Task Graph
G = nx.DiGraph()
tasks = [
    "connect_animator_controller",
    "implement_state_aware_saving",
    "optimize_blank_frame_storage",
    "verify_animation_render"
]
G.add_nodes_from(tasks)

# 3. Validation: ABSOLUTE PARALLELISM
assert G.number_of_edges() == 0, f"Dependencies detected! {G.edges()}"
assert nx.is_directed_acyclic_graph(G), "Circular dependency detected!"

# 4. Define Agent State Machine (Renderer Agent)
renderer_agent_states = [
    {"state": "IDLE", "trigger": "Start Render", "next": "INITIALIZING", "action": "Load Config & Assets"},
    {"state": "INITIALIZING", "trigger": "Setup Complete", "next": "RENDERING_LOOP", "action": "Init AnimationController"},
    {"state": "RENDERING_LOOP", "trigger": "Frame < Start", "next": "SKIPPING", "action": "Skip Blank Frame"},
    {"state": "RENDERING_LOOP", "trigger": "Frame in Range", "next": "PROCESSING_FRAME", "action": "Update Anim State"},
    {"state": "PROCESSING_FRAME", "trigger": "State Ready", "next": "SAVING", "action": "Apply Transform & Save"},
    {"state": "SAVING", "trigger": "Save Complete", "next": "RENDERING_LOOP", "action": "Next Frame"},
    {"state": "RENDERING_LOOP", "trigger": "All Frames Done", "next": "COMPLETED", "action": "Write Manifest"},
    {"state": "SKIPPING", "trigger": "Continue", "next": "RENDERING_LOOP", "action": "Next Frame"},
]

# 5. Generate Plan Files

# 5.1 Overview
overview_content = """# Plan: Smart Director Render Fix (Parallel Execution)

## 🦅 Eagle View
**Goal**: operationalize the Smart Script Director by connecting the `LayerRenderer` to the `AnimationController`, ensuring layers move, appear, and persist correctly without converting to video formats yet (EXR sequences only).

## 📊 Computational Analysis
* **Execution Mode**: **PURE PARALLEL** (0 Dependencies)
* **Total Tasks**: 4
* **Agent Focus**: `RendererDev`

## 🕸️ Task Independence Graph
```mermaid
graph TD
    A[connect_animator_controller]
    B[implement_state_aware_saving]
    C[optimize_blank_frame_storage]
    D[verify_animation_render]
    %% NO ARROWS - PARALLEL EXECUTION
    style A stroke-dasharray: 5 5
    style B stroke-dasharray: 5 5
    style C stroke-dasharray: 5 5
    style D stroke-dasharray: 5 5
```
"""

with open(os.path.join(PLAN_DIR, "plan_overview.md"), "w") as f:
    f.write(overview_content)

# 5.2 Agent Tasks
agent_content = """## 2. Role: Renderer Developer
**Focus**: `src/domain/modules/animator`

### 3. Interface Contracts
**Input (Independent Source):**
```json
{
  "layer": "LayerEntity",
  "timeline": "TimelineObject",
  "config": "LayerRenderConfig"
}
```

**Output (Independent Sink):**
```json
{
  "manifest": "LayerManifest",
  "files": ["frame_0001.exr", "frame_0002.exr"]
}
```

### 4. State Machine (Logic Flow)
| Current | Trigger | Next | Action |
|---------|---------|------|--------|
"""
for s in renderer_agent_states:
    agent_content += f"| {s['state']} | {s['trigger']} | {s['next']} | {s['action']} |\n"

agent_content += """

### 5. Modular Tasks (Parallel Execution)

#### Task 1: Connect Animation Controller
**File**: `engine/src/domain/modules/animator/layer_renderer_module.py`
**Description**: 
-   Instantiate `AnimationController` in `render_layer`.
-   Iterate frames and call `controller.update(action, progress)`.
-   **Output**: Pass `LayerAnimState` to saver methods.

#### Task 2: Implement State-Aware Saving
**File**: `engine/src/domain/modules/animator/layer_renderer_module.py`
**Description**:
-   Update `_save_layer_frame` to accept `LayerAnimState`.
-   Use `state.position` instead of `layer.position`.
-   Use `state.opacity` instead of `layer.opacity`.
-   (Optional) Handle Brush logic if applicable.

#### Task 3: Optimize Blank Frame Storage
**File**: `engine/src/domain/modules/animator/layer_renderer_module.py`
**Description**:
-   In the frame loop, if `frame < start_frame`: **CONTINUE** (Do not generate file).
-   Ensure `LayerManifest` still records the correct `blank_frames` count.

#### Task 4: Verify Animation Render
**File**: `engine/tests/per_layer_render_test.py`
**Description**:
-   Run the integration test.
-   Check `outputs/per_layer_render` for existence of EXR files.
-   Verify NO files exist for blank regions.
"""

with open(os.path.join(PLAN_DIR, "tasks_renderer_dev.md"), "w") as f:
    f.write(agent_content)

print("Plan generated successfully.")
