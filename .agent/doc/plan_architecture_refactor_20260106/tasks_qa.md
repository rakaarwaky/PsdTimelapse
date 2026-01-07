# Agent Task List: QA

## 1. 🦅 Eagle View
This project is **Client-App Refactor**, focusing on splitting Engine and Client and enforcing Hexagonal Architecture.
- **Architect**: High-level design and final wiring.
- **RefactoringSpecialist**: Code modifications and interface extraction.
- **QA**: Verification.

## 2. Tasks (Topologically Sorted)

### Task: verify_architecture
**Complexity:** 2 | **Dependencies:** wire_dependencies

**Description:**
Run static analysis or manual check to ensure no forbidden imports exist in `domain/modules`.

**Acceptance:**
- [ ] Code implements the change described.
- [ ] No regression in tests (if applicable).
