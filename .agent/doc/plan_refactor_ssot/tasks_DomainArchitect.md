## 1. 🦅 Eagle View

This project is **Timelapse Engine**, a hexagonal architecture system for generating videos from PSDs.
Current feature: **SSOT Refactor** which establishes `ProducerEngine` as the single entry point.

System has 3 agents:
- **DomainArchitect**: Core Logic (ProducerEngine)
- **AdapterSpecialist**: API Adapter
- **IntegrationLead**: Main Wiring & QA

**Your focus:** DomainArchitect
**Execution Mode:** PARALLEL. Do NOT wait for other agents.


## 2. Role
**Core Logic & Interfaces** - Owner of the pure domain layer. Ensures ProducerEngine exposes the correct facade.

**Responsibilities:**
- Execute assigned tasks immediately.
- Maintain Hexagonal boundaries.

**Constraints:**
- Must not modify code outside assigned layer.
- **MUST NOT BLOCK other agents.**

## 3. Interface Contracts
**Input (Independent Source):**
```json
{
  "config": "RenderConfig",
  "dependencies": ["PsdPort", "VideoPort"]
}
```

**Output (Independent Sink):**
```json
{
  "instance": "ProducerEngine",
  "status": "Ready"
}
```

## 4. Agent State Machine

| Current State | Trigger | Next State | Action |
|---------------|---------|------------|--------|
| IDLE          | Task Assigned | WORKING    | Checkout branch |
| WORKING       | Code Changes | REVIEW     | Run unit tests |
| REVIEW        | Tests Pass   | DONE       | Merge & Push |
| REVIEW        | Tests Fail   | ERROR      | Log failure |
| ERROR         | Fix Applied  | WORKING    | Retry implementation |


## 5. Modular Tasks (Parallel Execution)

### Task: refactor_producer_engine
**Complexity:** 2 | **Dependencies:** NONE
**Description:** Implement changes for refactor_producer_engine.
**Acceptance:**
- [ ] Code compiles and runs
- [ ] Interface types match strict definition
- [ ] No regression in tests
**Notes:** Assume interface contract is agreed upon. Mock external dependencies if needed.

