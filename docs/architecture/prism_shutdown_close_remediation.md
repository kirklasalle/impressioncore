# PRISM Shutdown Close Remediation

This walkthrough explains the changes implemented to ensure that clicking the **Shutdown** button programmatically closes:
1. The client browser tab in which the PRISM dashboard is running.
2. The spawned `PRISM Server` cmd window running the server process.
3. The parent `start_*.bat` launcher cmd window that was originally used to boot PRISM.

## 1. Browser Tab Closing Logic

To close the browser tab programmatically (which was opened by the launcher script), we implemented a multi-tactic JavaScript closing routine within `triggerSystemShutdown` in [dashboard.ts](file:///d:/Projects/Prism/src/core/operator/templates/dashboard.ts#L236-L248):

```javascript
      setTimeout(() => {
        try {
          window.open('', '_self');
          window.close();
        } catch (e) {}
        try {
          window.open('about:blank', '_self').close();
        } catch (e) {}
        try {
          window.close();
        } catch (e) {}
      }, 1500);
```

## 2. Server Window Auto-Close

In the launcher scripts (`start_web.bat`, `start_individual.bat`, `start_enterprise.bat`, and `start_wizard.bat`), the server process was previously spawned using `cmd /k npm start`. The `/k` flag tells command prompt to remain open even after the process has terminated. We changed this to `/c` so that it closes immediately on server exit:

```batch
start "PRISM Server" cmd /c npm start
```

## 3. Launcher Window Auto-Close

Previously, the launcher batch files sat at a `pause` block indefinitely. We replaced this with a native port-monitoring loop that checks every 2 seconds if the PRISM server is still listening on its configured port. Once the server goes offline, the loop terminates and the batch window exits gracefully:

```batch
echo [MONITOR] PRISM is running. Monitoring for shutdown...
:monitor_loop
timeout /t 2 /nobreak >nul
netstat -ano | find "LISTENING" | find ":%PRISM_DASHBOARD_PORT%" >nul
if %errorlevel% equ 0 goto :monitor_loop

echo [SHUTDOWN] PRISM server has shut down. Exiting launcher.
goto :eof
```

## 4. Verification

1. Compiled the source files to the `dist/` directory using:
   ```powershell
   npm run build
   ```
2. Ran the full integration and unit test suite:
   ```powershell
   npm test
   ```
   All 28 tests suites passed successfully.
