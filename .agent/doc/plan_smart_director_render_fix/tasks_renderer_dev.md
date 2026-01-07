## 2. Role: Renderer Developer
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
| IDLE | Start Render | INITIALIZING | Load Config & Assets |
| INITIALIZING | Setup Complete | RENDERING_LOOP | Init AnimationController |
| RENDERING_LOOP | Frame < Start | SKIPPING | Skip Blank Frame |
| RENDERING_LOOP | Frame in Range | PROCESSING_FRAME | Update Anim State |
| PROCESSING_FRAME | State Ready | SAVING | Apply Transform & Save |
| SAVING | Save Complete | RENDERING_LOOP | Next Frame |
| RENDERING_LOOP | All Frames Done | COMPLETED | Write Manifest |
| SKIPPING | Continue | RENDERING_LOOP | Next Frame |


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
