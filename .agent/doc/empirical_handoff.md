# Empirical State Report: Engine Integration

**Date**: 2026-01-06
**Objective**: Handoff verifiable system state to next agent.

## 1. Validated System State

### A. Asset Detection (Source: `debug_frames_test.py` Logs)
The PSD `test.psd` was verified to contain **4 distinct functional layers**:
1.  **`FRONT`** (Hoodie) - *Validated ID: root_0*
2.  **`DISTRESSED EMBROIDERY BY IFGOOD STD`** (Right Arm) - *Validated ID: root_1*
3.  **`DISTRESSED EMBROIDERY BY IFGOOD STD copy`** (Left Arm) - *Validated ID: root_2*
4.  **`DISTRESSED EMBROIDERY BY IFGOOD STD`** (Logo) - *Validated ID: root_3*

### B. "Missing Asset" Root Cause & Fix
**Issue**: The white `FRONT` layer was invisible in the output.
**Empirical Finding**:
-   Layer Data Inspection: `Extrema: ((0, 255), (0, 255), (0, 255), (0, 255))` (Proof: Layer contains pixel data).
-   Alpha Channel Inspection: `Alpha Range: (0, 255)` (Proof: Layer is not transparent).
-   **Defect**: `FrameCompositor` initialized the canvas with `(255, 255, 255, 255)` (Opaque White).
-   **Result**: White Asset + White Background = Invisible.

**Fix Applied (Code):**
`engine/src/domain/modules/compositor/compositor_module.py`:
```python
# BEFORE
psd = Image.new('RGBA', (self.world.width, self.world.height), (255, 255, 255, 255))

# AFTER (Verified)
psd = Image.new('RGBA', (self.world.width, self.world.height), (0, 0, 0, 0))
```

## 2. Architecture & Pipeline Verification

The system now enforces a **Strict 3-Pass Rendering Pipeline**, verified by `final_render_test.py`:

| Pass | Component | Status | Code Proof |
| :--- | :--- | :--- | :--- |
| **1. UI Shell** | `UIRendererCore` | **Verified** | `static_ui_frame = app_ui_renderer.render_frame(...)` in `final_render_test.py` |
| **2. Animation** | `FrameCompositor` | **Verified** | `compose_with_ui` removed. Now returns pure `content_frame`. |
| **3. Composition** | `PipelineManager` | **Verified** | `pipeline_manager.compose_frame(static_ui, content)` |

## 3. Physical Evidence (Artifacts)

| File | Path | Size | Confirms |
| :--- | :--- | :--- | :--- |
| **Final Video** | `engine/tests/outputs/final_render/final_render_test.webm` | ~1.6MB | Full integration success. |
| **Debug Frame** | `engine/tests/outputs/debug_frames/debug_front_layer.png` | ~51KB | Visibility of `FRONT` layer. |

## 4. Known Mappings (Timeline)
Based on `final_render_test.py`:
-   **0.5s - 2.5s**: **Drag** `FRONT` (Hoodie) +100px X-axis.
-   **3.0s - 5.0s**: **Reveal** `Right Arm` (Embroidery).
-   **3.5s - 5.5s**: **Reveal** `Left Arm` (Embroidery Copy).
-   **4.0s - 6.0s**: **Reveal** `Logo` (Embroidery).

---
**Next Steps for Agent**:
1.  Run `python3 engine/tests/final_render_test.py` to reproduce the validated state.
2.  Do NOT revert `compositor_module.py` initialization (Lines 50 & 169) or assets will vanish.
