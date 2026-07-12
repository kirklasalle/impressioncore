# PRISM Confirm Dialog Migration Log

All native browser `confirm(...)` calls across the Operator dashboard frontend have been migrated to the new custom async confirmation modal (`showConfirm`).

## Migrated Call Sites

1. **Characters Tab (`tab-characters.js`)**
   - Imported `showConfirm` from `./dashboard-core.js`.
   - Replaced native `confirm(...)` with `await showConfirm(...)` in `window.deleteCharacterAssignment`.

2. **Channels Tab (`tab-channels.js`)**
   - Imported `showConfirm` from `./dashboard-core.js`.
   - Replaced native `confirm(...)` with `await showConfirm(...)` in `disconnectChannel`.

3. **Agentic Tab (`tab-agentic.js`)**
   - Imported `showConfirm` from `./dashboard-core.js`.
   - Replaced native `confirm(...)` with `await showConfirm(...)` in `deleteLocalModel`.

4. **Phase E3 Panels (`phase-e3-panels.js`)**
   - Since E3 panels operate independently, call sites utilize the global `window.showConfirm` directly.
   - Replaced native `confirm(...)` with `await window.showConfirm(...)` in the click handler for executing a utility.
   - Replaced native `confirm(...)` with `await window.showConfirm(...)` in the click handler for clearing a tool risk override.

## Test Harness & Mock Adjustments

Because the frontend unit tests run under JSDOM with a mocked representation of `dashboard-core.js`, the mock was extended to export `showConfirm` to prevent ES module resolution syntax errors:
- Updated `tests/tab-agentic-ui.test.ts`
- Updated `tests/tab-logs-ui.test.ts`
- Updated `tests/tab-workspace-ui.test.ts`

## Build & Test Status

- **Build**: Compiles successfully via `npm run build` with exit code `0`.
- **Unit Tests**: All 485 unit test cases pass with exit code `0`.
