# Feature Specifications

**Core Logic: The "Blender" Model**

To ensure consistent behavior with the Editor App, the Client App (Timelapse Engine) adopts the same **World-Camera-Viewport** architectural model commonly found in 3D software (Blender/Unity).

---

## 1. Domain Entities (The Virtual Studio)

### F1: The World (Infinite Canvas) ✅
*   **Definition**: The absolute 2D coordinate space where the artwork exists.
*   **Implementation**: `WorldEntity` in `engine/src/domain/entities/world_entity.py`
*   **Logic**:
    *   Origin (0,0) is the top-left of the PSD document.
    *   Contains the **Scene Graph** (Layer Hierarchy).
    *   Independent of the output video resolution.

### F2: The Camera (Virtual Director) ✅
*   **Definition**: A floating object that defines *what* part of the World is currently visible.
*   **Implementation**: `CameraEntity` in `engine/src/domain/entities/camera_entity.py`
*   **Logic**:
    *   **Translation (Pan)**: Moving the camera X/Y to focus on specific details.
    *   **Scale (Zoom)**: Altering the Field of View.
    *   **Pathing**: Moves along Cubic Bézier curves to simulate smooth, human-like focus shifts.

### F3: The Viewport (Output Frame) ✅
*   **Definition**: The fixed-resolution window (e.g., 1920x1080) that the video encoder sees.
*   **Implementation**: `ViewportEntity` in `engine/src/domain/entities/viewport_entity.py`
*   **Logic**:
    *   Acts as the "Lens" capturing the World through the Camera.
    *   Supports output presets (HD, FullHD, 4K, Vertical/Horizontal).

---

## 2. Animation Features

### F4: Drag & Drop Animation ✅
**"From Asset Library to Canvas"**

Used for adding new independent elements.
*   **Implementation**: `AnimationController.calculate_drag_state()` in animator module
*   **Visual**: Element "flies" in with EaseOutBack (overshoot effect)
*   **Used For**: Logos, Panels, Shapes

### F5: Brush Reveal Animation ✅
**"Magic Wand Effect"**

Used for intricate details that are already "there" but hidden.
*   **Implementation**: `AnimationController.calculate_brush_state()` in animator module
*   **Visual**: Particles appear along a spline path behind the cursor
*   **Used For**: Stitching, Beads, Complex edges

### F6: Background Animation ✅
**Instant Appear**

Used for full-canvas background layers.
*   **Implementation**: Automatic detection based on layer size
*   **Visual**: Fade in without cursor interaction

---

## 3. Classification System

### F7: Action Classification ✅
The engine analyzes layer metadata to assign an Action Type.

**Automatic Rules (by layer size):**
| Layer Size | Action Type | Animation |
|------------|-------------|-----------|
| < 100px | `DRAG_DROP` | Fly in from edge |
| 100-500px | `DRAG_DROP` | Fly in from edge |
| > 500px | `BRUSH_REVEAL` | Reveal along cursor path |
| Full Canvas | `BACKGROUND` | Fade in |

**Manual Override (by naming convention):**
| Prefix | Forces | Example |
|--------|--------|---------|
| `[D]` | Drag & Drop | `[D] Huge Background` flies in |
| `[B]` | Brush Reveal | `[B] Small Logo` gets brush reveal |
| `[BG]` | Background | `[BG] Pattern` fades in |

### F8: Layer Classification ✅
Additional image-based classification for sophisticated decisions.
*   **Implementation**: `layer_classifier_module.py`

---

## 4. UI Overlay System

### F9: Photoshop-like Frame ✅
Static UI overlay rendered via Pillow (not Vue).

**Components rendered:**
- Header bar with menus and controls
- Left toolbar with drawing tools
- Right toolbar with context tools
- Bottom toolbar with view controls
- Layers panel (dynamic based on scene)
- Canvas area with PSD content

**Resolution**: Fixed 1080x1920 (Vertical, Mobile-first)

---

## 5. Coordinate Mapping

### F10: World ↔ Viewport Transformation ✅
*   **Implementation**: `CoordinateMapper` in layout_manager module
*   **Logic**:
    *   `world_to_viewport()`: Convert world coordinates to output pixels
    *   `viewport_to_world()`: Convert viewport pixels to world coordinates

---

## 6. Timeline Planning

### F11: Sequencing Strategies ✅
*   **Implementation**: `SequencingStrategy` enum in script_director module

| Strategy | Description |
|----------|-------------|
| `STAGGERED` | Actions overlap with slight delays |
| `SEQUENTIAL` | One action completes before next starts |
| `PARALLEL` | All actions start simultaneously |

---

## 7. Technical Requirements

| Component | Library | Version | Status |
|-----------|---------|---------|--------|
| **Core** | `Python` | 3.10+ | ✅ |
| **Parsing** | `psd-tools` | 1.9+ | ✅ |
| **Imaging** | `Pillow` | 10.0+ | ✅ |
| **Video** | `moviepy` | 1.0+ | ✅ |
| **API** | `FastAPI` | 0.100+ | ✅ |
| **Frontend** | `Vue` | 3.0+ | ✅ |

