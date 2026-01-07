# Product Overview: PSD Timelapse (Timelapse Engine)

**Version:** 2.0.0  
**Status:** ✅ Production Ready (Core Features Implemented)

---

## 1. Executive Summary

The **Client App** (internally known as the *Timelapse Generation Engine*) is a specialized desktop-grade web application designed to automate the creation of "process videos" from static design files. By parsing Adobe Photoshop (PSD) files and applying procedural animation algorithms, it reverse-engineers a plausible creation process, generating high-quality MP4 video content suitable for social media marketing.

This tool bridges the gap between static design deliverables and dynamic video content, eliminating hours of manual screen recording.

---

## 2. Problem Statement

Professional designers and creative agencies face several challenges in marketing their work:
*   **Workflow Friction:** Recording a screen during the actual design process is resource-intensive and prone to interruption.
*   **Post-Production Costs:** Editing hours of raw footage into a 30-second clip requires video editing skills and time.
*   **Static Assets:** PSD files are "flat" deliverables that fail to capture the craftsmanship behind the design.

## 3. Solution Proposition

The Client App provides an **"Upload & Forget"** workflow:
1.  **Input**: Raw `.psd` file.
2.  **Process**: The engine analyzes layer hierarchy, groups, and blend modes to construct a logical "timeline" of creation.
3.  **Visualization**: It simulates a human cursor leveraging Bézier curves for natural movement.
4.  **Output**: A 1080p/4k MP4 video of the "design being made" with a Photoshop-like UI overlay.

---

## 4. Key Differentiators

| Feature | Competitor / Manual | PSD Timelapse |
|---------|---------------------|------------|
| **Input** | Screen Recording (Raw Video) | PSD File (Structured Data) |
| **Edit Time** | Hours (Manual Editing) | Zero (Procedural Generation) |
| **Quality** | Lossy Compression | Pixel-Perfect Rendering |
| **Flexibility** | Fixed Viewport | Dynamic Camera/Zoom Control |
| **UI Overlay** | Manual Addition | Automatic Photoshop-like Frame |

---

## 5. Current Implementation Status

### ✅ Completed Features
- **5-Role Architecture**: Fully implemented modular design
- **PSD Parsing**: Layer extraction and classification working
- **Animation System**: Drag & Drop and Brush Reveal animations
- **Video Encoding**: MP4 output via MoviePy
- **UI Overlay**: Photoshop iPad-like interface overlay rendered via Pillow
- **FastAPI Backend**: REST API for video generation
- **Vue Frontend**: Dashboard with upload and progress tracking

### 🔄 Performance Optimization (In Progress)
- Layer caching for static backgrounds
- Memory optimization for large PSD files

---

## 6. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Vue 3 + TypeScript | Reactive UI, File Upload |
| **Backend** | Python 3.12+ / FastAPI | REST API, Video Generation |
| **PSD Parsing** | `psd-tools` 1.9+ | Layer Extraction |
| **Image Processing** | `Pillow` 10.0+ | Frame Composition, UI Rendering |
| **Video Encoding** | `moviepy` 1.0+ | MP4 Export |

