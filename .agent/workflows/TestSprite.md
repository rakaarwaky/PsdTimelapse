---
description: Intelligent router for all TestSprite testing features
---

# TestSprite Intelligent Assistant

When this workflow is triggered via `/TestSprite`, analyze the user's request and automatically select the most appropriate tool from the TestSprite suite.

## Tool Selection Logic

Follow this mapping based on the user's need:

1. **"I'm starting a new test session"** or **"Setup tests"**
   - Action: Use `testsprite_bootstrap_tests`
   - Requirement: Identify `localPort` (default 3000 or check `yarn dev` output).

2. **"What does this code do?"** or **"Explain the project structure"**
   - Action: Use `testsprite_generate_code_summary`
   - Scope: Analyze the root repository.

3. **"I need requirements"** or **"Create a PRD"**
   - Action: Use `testsprite_generate_standardized_prd`
   - Output: Structured PRD markdown.

4. **"Test the UI/Frontend"** or **"How do I test the editor interface?"**
   - Action: Use `testsprite_generate_frontend_test_plan`
   - Note: Ask if login is required (`needLogin`).

5. **"Test the API/Backend"** or **"Check the server logic"**
   - Action: Use `testsprite_generate_backend_test_plan`.

6. **"Run the tests"** or **"Execute everything"**
   - Action: Use `testsprite_generate_code_and_execute`
   - Parameters: Use specific `testIds` from the plan or leave empty for all.

7. **"Fix failing tests"** or **"Run them again"**
   - Action: Use `testsprite_rerun_tests`.

## Instructions for Antigravity AI
1. Read the user's specific complaint or request.
2. Determine which of the 7 tools above solves the issue.
3. If information is missing (like a port), check the environment or ask the user.
4. Execute the tool immediately and report the results.

// turbo
## Initialize & Run Example
"Bootstrap and run all frontend tests for me"
1. `testsprite_bootstrap_tests` (port 3000)
2. `testsprite_generate_frontend_test_plan`
3. `testsprite_generate_code_and_execute`
