# Developer Guide & Setup

**Technical Manual for Contributors**

---

## 1. Environment Prerequisites

Before starting, ensure your development machine meets these requirements:

*   **Operating System**: Linux (Ubuntu 20.04+), macOS (M1/Intel), or Windows 10/11 (WSL2).
*   **Runtime**:
    *   Node.js `v18.16.0` (LTS) or higher.
    *   Python `3.12.x` or higher.
*   **System Libraries**:
    *   `ffmpeg` (Required for video encoding).

---

## 2. Installation (Local Development)

### Step A: Clone & Structure
```bash
git clone git@github.com:your-org/psd-timelapse.git
cd psd-timelapse
```

### Step B: Frontend Setup (Vue)
```bash
cd web
npm ci
```

### Step C: Backend Setup (Python)
It is **highly recommended** to use a virtual environment.

```bash
# Create Virtual Environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Install Dependencies (from engine root)
pip install -r engine/requirements.txt
```

---

## 3. Running the Application

**Terminal 1: UI Dev Server**
```bash
cd web
npm run dev
```

**Terminal 2: API Server**
```bash
source venv/bin/activate
cd engine
uvicorn main:app --reload --port 8000
```

---

## 4. Project Structure Overview

```
psd-timelapse/
├── engine/               # 🐍 Backend (Python)
│   ├── main.py           # FastAPI entry point
│   ├── src/              # Domain logic
│   └── tests/            # Tests (distributed in src/)
│
├── web/                  # 🟢 Frontend (Vue.js)
│   ├── src/
│   └── index.html
│
└── doc/                  # Documentation
```

---

## 5. Architecture Rules

> [!IMPORTANT]
> These rules are **NON-NEGOTIABLE**.

### The 300-Line Limit
*   **Ideal File Size:** < 200 lines
*   **Soft Limit:** 300 lines (Start planning refactoring)
*   **Hard Limit:** 500 lines (STOP. Refactor immediately)

### Hexagonal Architecture
*   **Domain:** Pure Python, no framework dependencies.
*   **Adapters:** Where messy external libs reside.
*   **Orchestrators:** Glue code connecting modules.

---

## 6. Running Tests

We use `unittest` with standard discovery.

### Distributed Test Suite
Run all tests from the project root (ensure `engine/src` is in PYTHONPATH):

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/engine/src
python3 -m unittest discover -s "engine/src" -p "test_*.py"
```

### Specific Test Scenarios
To run the render pipeline integration tests:

```bash
python3 -m unittest discover -s "engine/src/domain/modules/pipeline_manager/scenario/integration" -v
```

### Visual Regression Tests
```bash
python3 -m unittest discover -s "engine/src/domain/modules/pipeline_manager/scenario/visual" -v
```
**Output Location:** All test artifacts are generated in `engine/media/test_project/`.

---

## 7. Common Development Tasks

### Adding a New feature
Follow the Hexagonal pattern:
1. Define Entity/Value Object in `domain/entities` or `domain/value_objects`.
2. Define Port Interface in `domain/ports`.
3. Implement Domain Logic in `domain/modules`.
4. Implement Adapter in `adapters/driven`.
5. Wire it up in an Orchestrator.

### Debugging
The engine uses standard Python logging. Check the console output or configure a `FileLoggerAdapter` if needed.

