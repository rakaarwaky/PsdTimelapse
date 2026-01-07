# Tasks: Engine Migrator Agent

## Assigned Tasks

| Task | Dependencies |
|---|---|
| CreateDirectories | None |
| MoveEngineRootFiles | CreateDirectories |
| MoveEngineSrcFiles | CreateDirectories |
| RefactorPythonImports | MoveEngineSrcFiles |
| VerifyEngineTests | RefactorPythonImports, MoveEngineRootFiles |

## Task Details

### CreateDirectories
- Create `engine/src`

### MoveEngineRootFiles
- Move `main.py`, `verify_setup.py`, `tools/`, `tests/`, `requirements.txt`, `.python-live-rules.json` to `engine/`

### MoveEngineSrcFiles
- Move `src/domain` to `engine/src/domain`
- Move `src/adapters` to `engine/src/adapters`

