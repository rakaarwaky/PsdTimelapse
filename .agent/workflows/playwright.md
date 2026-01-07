---
description: Intelligent router for all Playwright and Browser-based testing
---

# Playwright Intelligent Assistant

When this workflow is triggered via `/playwright`, analyze the user's request, complaint, or testing goal and automatically choose the right approach from the 33 available Playwright MCP features.

## 🎯 Core Capabilities & Smart Routing

### 1. **Test Code Generation & Recording**
- **"Record my actions"** or **"Generate test from my clicks"**
  - Use: `start_codegen_session` → interact → `end_codegen_session`
  - Purpose: Auto-generate Playwright test code from manual browser interactions
  - Example: Recording brush strokes, eraser usage, layer operations

- **"Check codegen status"** → Use: `get_codegen_session`
- **"Cancel recording"** → Use: `clear_codegen_session`

### 2. **Navigation & Page Control**
- **"Open the editor"** or **"Navigate to URL"**
  - Use: `playwright_navigate`
  - Ports: Client (`localhost:3000`), Editor (`localhost:3001`)
  - Options: Set browser type (chromium/firefox/webkit), viewport size, headless mode

- **"Go back"** → Use: `playwright_go_back`
- **"Go forward"** → Use: `playwright_go_forward`
- **"Close browser"** → Use: `playwright_close`

### 3. **Visual Testing & Screenshots**
- **"Take a screenshot"** or **"Show me how it looks"**
  - Use: `playwright_screenshot`
  - Options: Full page, specific element (selector), save as PNG, base64
  - Use case: Verify brush rendering, layer visibility, UI state

- **"Save as PDF"** → Use: `playwright_save_as_pdf`
  - Options: Page format (A4, Letter), margins, print background

### 4. **User Interactions**
- **"Click the brush tool"** → Use: `playwright_click`
- **"Fill the color picker"** → Use: `playwright_fill`
- **"Hover over the layer"** → Use: `playwright_hover`
- **"Select from dropdown"** → Use: `playwright_select`
- **"Press Enter/Escape"** → Use: `playwright_press_key`
- **"Drag layer to reorder"** → Use: `playwright_drag`
- **"Upload image file"** → Use: `playwright_upload_file`

### 5. **iFrame Handling** (for embedded editors)
- **"Click inside iframe"** → Use: `playwright_iframe_click`
- **"Fill input in iframe"** → Use: `playwright_iframe_fill`

### 6. **Advanced Interactions**
- **"Open in new tab"** → Use: `playwright_click_and_switch_tab`
- **"Execute custom JS"** → Use: `playwright_evaluate`
  - Use case: Trigger canvas operations, check internal state

### 7. **Debugging & Inspection**
- **"Show console errors"** or **"Check logs"**
  - Use: `playwright_console_logs`
  - Options: Filter by type (error/warning/log), search text, limit results
  - Use case: Debug brush/eraser bugs, canvas rendering issues

- **"Get page text"** → Use: `playwright_get_visible_text`
- **"Get page HTML"** → Use: `playwright_get_visible_html`
  - Options: Remove scripts/styles/comments, minify, clean HTML

### 8. **Viewport & Device Testing**
- **"Test on mobile"** or **"Resize to iPhone"**
  - Use: `playwright_resize`
  - Presets: 143+ devices (iPhone 13, iPad Pro, Pixel 7, Galaxy S24, Desktop Chrome)
  - Options: Manual width/height, device preset, orientation (portrait/landscape)

- **"Set custom user agent"** → Use: `playwright_custom_user_agent`

### 9. **HTTP/API Testing**
- **"GET request"** → Use: `playwright_get`
- **"POST data"** → Use: `playwright_post`
- **"PUT update"** → Use: `playwright_put`
- **"PATCH modify"** → Use: `playwright_patch`
- **"DELETE resource"** → Use: `playwright_delete`
- Options: Headers, bearer token, request body

### 10. **Network Monitoring**
- **"Wait for API response"** → Use: `playwright_expect_response` + `playwright_assert_response`
  - Pattern: Start waiting → Trigger action → Validate response
  - Use case: Verify image upload, layer save, export operations

## 🎨 Photo Editor Specific Use Cases

### Testing Brush Feature
```
1. Navigate: playwright_navigate("http://localhost:3001")
2. Click: playwright_click("button[data-tool='brush']")
3. Drag: playwright_drag("canvas", "canvas") // simulate stroke
4. Screenshot: playwright_screenshot(name="brush_stroke")
5. Console: playwright_console_logs(type="error") // check for errors
```

### Testing Eraser Bug Fix
```
1. Navigate to editor
2. Draw brush strokes (multiple clicks/drags)
3. Click eraser tool
4. Erase strokes
5. Evaluate: Check layer count didn't increase
6. Screenshot: Verify visual result
7. Console logs: Ensure no errors
```

### Mobile Responsiveness Test
```
1. Resize: playwright_resize(device="iPhone 13", orientation="portrait")
2. Navigate to client app
3. Screenshot: Capture mobile view
4. Resize: playwright_resize(device="iPad Pro 11", orientation="landscape")
5. Screenshot: Capture tablet view
```

### Full E2E Test Recording
```
1. start_codegen_session(outputPath="/home/rakaarwaky/Work/App Project/Photo Editor/tests")
2. Manual interactions (AI guides user)
3. end_codegen_session → Auto-generates test file
```

## 🚀 Quick Action Mapping

| User Request | Playwright Tool | Notes |
|--------------|----------------|-------|
| "Test the login flow" | `npx playwright test tests/login.spec.ts` | CLI command |
| "Show me the editor" | `playwright_navigate` + `playwright_screenshot` | MCP tools |
| "Debug canvas rendering" | `playwright_evaluate` + `playwright_console_logs` | Inspect state |
| "Test on mobile" | `playwright_resize` | Device presets |
| "Record new test" | `start_codegen_session` | Code generation |
| "Check API call" | `playwright_expect_response` + `playwright_assert_response` | Network monitoring |
| "Upload test image" | `playwright_upload_file` | File operations |
| "Verify no errors" | `playwright_console_logs(type="error")` | Error checking |

## 📋 Instructions for Antigravity AI

1. **Identify the Goal**: Understand if user wants to test, debug, record, or inspect
2. **Choose the Right Tool**: Pick from 33 features based on the mapping above
3. **Check Prerequisites**: 
   - Is the app running? (`yarn dev`)
   - Correct port? (3000 for client, 3001 for editor)
4. **Execute Smartly**:
   - For bugs: Start with `playwright_console_logs` and `playwright_get_visible_html`
   - For visual tests: Use `playwright_screenshot` with specific selectors
   - For flows: Consider `start_codegen_session` for reusability
5. **Provide Evidence**: Always screenshot or log results
6. **Photo Editor Context**: Remember canvas operations, layer management, tool switching

// turbo
## Auto-Run Examples
- "Test the brush" → Auto-navigate, click brush, draw, screenshot
- "Check for errors" → Auto-fetch console logs with error filter
- "Show mobile view" → Auto-resize to iPhone preset and screenshot

## 🔧 Advanced Patterns

### Pattern 1: Visual Regression Test
```
1. playwright_navigate(url)
2. playwright_screenshot(name="baseline")
3. [Make changes]
4. playwright_screenshot(name="updated")
5. Compare screenshots manually or with tools
```

### Pattern 2: Network-Dependent Test
```
1. playwright_expect_response(id="upload", url="/api/upload")
2. playwright_upload_file(selector="input[type=file]", filePath="...")
3. playwright_assert_response(id="upload", value="success")
```

### Pattern 3: Multi-Device Test
```
For device in [iPhone 13, iPad Pro, Desktop Chrome]:
  1. playwright_resize(device=device)
  2. playwright_navigate(url)
  3. playwright_screenshot(name=f"{device}_view")
```

---

**Remember**: All 33 features are now available. Choose the most efficient combination for the user's specific Photo Editor testing needs! 🎨✨
