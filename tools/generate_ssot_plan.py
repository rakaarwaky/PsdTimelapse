import networkx as nx
import os
import json

# ==========================================
# 1. SETUP & GRAPH GENERATION
# ==========================================
try:
    import networkx as nx
except ImportError:
    import sys, subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "networkx"])
    import networkx as nx

# Define the Independent Tasks (Nodes only, NO EDGES)
tasks = [
    "refactor_producer_engine",  # Domain Layer: Expose methods in ProducerEngine
    "update_http_adapter",       # Adapter Layer: Switch type hints and calls to ProducerEngine
    "update_main_entrypoint",    # Application Layer: Inject adapters into ProducerEngine
    "create_verification_script" # QA: Verify the new wiring
]

G = nx.DiGraph()
G.add_nodes_from(tasks)

# CRITICAL: Assert Absolute Parallelism (Pareto 20%)
assert G.number_of_edges() == 0, f"Error! Dependencies detected: {G.edges()}"
assert nx.is_directed_acyclic_graph(G), "Circular dependencies detected!"

print(f"Graph Validated: {G.number_of_nodes()} independent tasks, 0 dependencies.")

# ==========================================
# 2. AGENT DEFINITIONS & STATE MACHINES
# ==========================================

AGENTS = {
    "DomainArchitect": {
        "role": "Core Logic & Interfaces",
        "description": "Owner of the pure domain layer. Ensures ProducerEngine exposes the correct facade.",
        "tasks": ["refactor_producer_engine"]
    },
    "AdapterSpecialist": {
        "role": "Integration & Infrastructure",
        "description": "Owner of external adapters. Updates the API to consume the new facade.",
        "tasks": ["update_http_adapter"]
    },
    "IntegrationLead": {
        "role": "Wiring & Verification",
        "description": "Owner of the composition root (main.py) and system verification.",
        "tasks": ["update_main_entrypoint", "create_verification_script"]
    }
}

# Universal FSM for all Agents
FSM_TABLE = """
| Current State | Trigger | Next State | Action |
|---------------|---------|------------|--------|
| IDLE          | Task Assigned | WORKING    | Checkout branch |
| WORKING       | Code Changes | REVIEW     | Run unit tests |
| REVIEW        | Tests Pass   | DONE       | Merge & Push |
| REVIEW        | Tests Fail   | ERROR      | Log failure |
| ERROR         | Fix Applied  | WORKING    | Retry implementation |
"""

# ==========================================
# 3. CONTENT GENERATION
# ==========================================

OUTPUT_DIR = ".agent/doc/plan_refactor_ssot"

def get_eagle_view(agent_name):
    return f"""## 1. 🦅 Eagle View

This project is **Timelapse Engine**, a hexagonal architecture system for generating videos from PSDs.
Current feature: **SSOT Refactor** which establishes `ProducerEngine` as the single entry point.

System has 3 agents:
- **DomainArchitect**: Core Logic (ProducerEngine)
- **AdapterSpecialist**: API Adapter
- **IntegrationLead**: Main Wiring & QA

**Your focus:** {agent_name}
**Execution Mode:** PARALLEL. Do NOT wait for other agents.
"""

def generate_overview():
    content = f"""# Plan: SSOT Refactor Overview

## Computational Analysis
**Tasks:** {len(tasks)} | **Execution Mode:** PARALLEL | **Framework:** Hexagonal (Independent Layers)

## Task Indepedence Graph
```mermaid
graph TD
    A[refactor_producer_engine]
    B[update_http_adapter]
    C[update_main_entrypoint]
    D[create_verification_script]
    
    %% NO ARROWS - PURE PARALLELISM
    style A stroke-dasharray: 5 5
    style B stroke-dasharray: 5 5
    style C stroke-dasharray: 5 5
    style D stroke-dasharray: 5 5
```

## Agent Allocation
| Agent | Role | Assigned Tasks |
|-------|------|----------------|
| **DomainArchitect** | Core Logic | `refactor_producer_engine` |
| **AdapterSpecialist** | Adapters | `update_http_adapter` |
| **IntegrationLead** | Wiring | `update_main_entrypoint`, `create_verification_script` |

"""
    with open(f"{OUTPUT_DIR}/plan_refactor_overview.md", "w") as f:
        f.write(content)

def generate_agent_file(agent_name, data):
    task_content = ""
    for task in data["tasks"]:
        task_content += f"""
### Task: {task}
**Complexity:** 2 | **Dependencies:** NONE
**Description:** Implement changes for {task}.
**Acceptance:**
- [ ] Code compiles and runs
- [ ] Interface types match strict definition
- [ ] No regression in tests
**Notes:** Assume interface contract is agreed upon. Mock external dependencies if needed.
"""

    content = f"""{get_eagle_view(agent_name)}

## 2. Role
**{data['role']}** - {data['description']}

**Responsibilities:**
- Execute assigned tasks immediately.
- Maintain Hexagonal boundaries.

**Constraints:**
- Must not modify code outside assigned layer.
- **MUST NOT BLOCK other agents.**

## 3. Interface Contracts
**Input (Independent Source):**
```json
{{
  "config": "RenderConfig",
  "dependencies": ["PsdPort", "VideoPort"]
}}
```

**Output (Independent Sink):**
```json
{{
  "instance": "ProducerEngine",
  "status": "Ready"
}}
```

## 4. Agent State Machine
{FSM_TABLE}

## 5. Modular Tasks (Parallel Execution)
{task_content}
"""
    filename = f"tasks_{agent_name}.md"
    with open(f"{OUTPUT_DIR}/{filename}", "w") as f:
        f.write(content)

# ==========================================
# 4. EXECUTION
# ==========================================

if __name__ == "__main__":
    generate_overview()
    for name, data in AGENTS.items():
        generate_agent_file(name, data)
    print("Plan formulation complete.")
