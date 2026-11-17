# Local runtime and native Builder repair verification

Repair cycle: November 2, 2026. Runtime counters completed at
2026-11-02T19:58:17.820482-05:00.

## Result

The local sensory application now authenticates correctly and responds with the
existing external InternVL2-1B. Kinect capture is explicit and produces sustained
fresh frames rather than exhausting the SDK's six-frame buffers. Native Builder
experiments now identify what actually ran and what remains uncertified.

The [original audit and repair addendum](../../../docs/analysis_reports/BUILDER_PLATFORM_AUDIT_20261102.md)
retain the pre-repair evidence and scientific/release limits.
Sanitized machine-readable checks: [runtime-evidence.json](runtime-evidence.json).

## Actual runtime acceptance

| Gate | Observed result |
|---|---|
| Liveness and readiness | Public liveness 200; final readiness 200, phase READY |
| Direct protected API | Unauthenticated model request remains 401 |
| Actual CORS error | Allowed local origin receives readable 401 with matching CORS origin |
| Hostile-origin local gateway request | Rejected 403 |
| Real model | OpenGVLab/InternVL2-1B, InternVLChatModel, 938,158,976 measured parameters, external pretrained, not native B-series |
| Existing weights/driver | Existing cached LLM reused; Kinect driver unchanged |
| Browser WebSocket inference | Same-origin `/v1/chat/stream`: status, left/right thoughts, token events, one done event; answer rendered |
| Final browser answer | "Hello! It's nice to meet you. How can I assist you today?" |
| Session persistence | The local verification session contains four saved messages from two submitted test turns |
| Speech readiness | `available:true`, `model_loaded:true`, `running:false`, `last_error:null` |
| Capture lifecycle | Explicit Start succeeds; Stop releases resources/cache; stopped health remains 200 and never opens hardware |
| Browser camera preview | Actual image loaded, natural size 480x360; verified without saving camera imagery |
| RGB/IR | IR UNAVAILABLE while RGB owns the shared Kinect v1 path; not counted as another physical camera |
| Final operator state | Services running; camera stopped and Whisper not listening |

Sustained final-run measurements:

| Local sample time | Color count | Depth count | Skeleton count | Color age ms | Depth age ms |
|---|---:|---:|---:|---:|---:|
| 19:58:00 | 16 | 16 | 15 | 16 | 16 |
| 19:58:04 | 94 | 94 | 89 | 16 | 0 |
| 19:58:08 | 173 | 173 | 166 | 31 | 16 |
| 19:58:11 | 239 | 239 | 229 | 31 | 16 |
| 19:58:14 | 300 | 300 | 286 | 16 | 16 |

One physical sensor; all sampled initialized color/depth/skeleton streams were
fresh. These are measured samples, not a long-duration stability or 30fps guarantee.
Acceptance testing also exposed a stopped-health 404 after resource release;
that producer contract was fixed and regression-tested before the final pass.

## Changes delivered

- Server-only authentication for HTTP, media and WebSockets; guarded loopback
  same-origin development gateway; CORS wrapping authentication errors.
- Supervised cache-only startup with ephemeral shared credentials, staged
  readiness, explicit failures, no automatic model substitution, and no
  name-based process killing. Existing environment keys remain supported.
- Explicit camera Start/Stop, requested/enabled/initialized/fresh stream health,
  actual frame release, RGB/IR constraints and physical/logical inventory.
  UI stream controls consume health rather than asserting every stream active.
- Reconnect/error/session handling improvements; malformed historical session
  IDs are excluded with a warning, not deleted or rewritten. Empty/failed model
  generation is not returned as a successful assistant message.
- Actual external model identity, measured count and dtype displayed separately
  from native offerings. The sensory application is no longer titled "B3".
- Optional `speech` extra and missing faster-whisper installation; cached only
  the small CPU `tiny.en` speech model. No microphone capture was performed.
- Native preflight/run identity binds implementation source SHA, configuration
  hash, measured count, tokenizer hash and explicit `prefix_next_token`
  objective. Schema-2 checkpoints and hashed export manifests record provenance.
  Unsupported B1/B2 execution and uncertified B3 reference sizes stay explicit.
- Scoped ESLint correctness configuration and synchronized active documentation.

## Validation commands and results

From the repository root:

```powershell
.\.venv310\Scripts\python.exe -m pytest src\tests\core\test_workbench.py src\tests\core\test_walkthrough_handoff.py src\tests\core\test_runtime_mode_config.py src\tests\core\test_cors_config.py src\tests\core\test_runtime_access.py src\tests\core\test_triad_readiness.py src\tests\test_kinect_audio_health.py -q
```

**Passed: 116 tests.** Existing SWIG deprecation warnings remain.

From `src\interfaces\web_client`:

```powershell
node --test runtime-proxy.test.mjs
npm run lint
npm run build
node --check ..\web\static\js\workbench.js
```

**All passed**; one Node gateway boundary test. Existing Browserslist age warning
remains. Lint is a scoped syntax/correctness gate, not full accessibility/style
certification.

Session-only verification harnesses, run with `.\.venv310\Scripts\python.exe`:

- `C:\Users\kirkl\.copilot\session-state\3d6d08e0-35ed-46fa-82a7-890e99c851ce\files\verify_workbench_browser.py`
  **Passed:** real isolated HTML/JavaScript training, evaluation, generation,
  verified ZIP export, durable reopen, default offerings, revision conflicts,
  unsaved-draft guards, keyboard tabs, visible failures and 1440/768/360 layouts.
- `C:\Users\kirkl\.copilot\session-state\3d6d08e0-35ed-46fa-82a7-890e99c851ce\files\verify_runtime_repair.py`
  **Passed:** actual auth/CORS/model/speech checks, sustained Kinect samples and
  final stopped health/resource release.
- Real Playwright-controlled browser **passed** the authenticated streaming
  chat turn and visible model/speech/camera state checks.
- `C:\Users\kirkl\.copilot\session-state\3d6d08e0-35ed-46fa-82a7-890e99c851ce\files\verify_repair_documentation.py`
  **Passed:** 89 added/current local references and fragments; maintained
  operator-guide section and mirror match.
- Scoped `git --no-pager diff --check` across changed application,
  launcher/test and documentation paths **passed**. Git CRLF normalization
  notices are informational; unrelated user changes were preserved.

Live chat verification persisted normal test session/memory data. Existing
experiments/checkpoints and historical malformed session files were preserved.
No credentials, camera frames or microphone recordings are included in this report.

## Use it

The sensory stack has been left running at `http://127.0.0.1:5173`.
If restarting, from the repository root:

```powershell
.\.venv310\Scripts\python.exe src\dev_tools\scripts\run_local_runtime.py
```

Wait for readiness, proceed through the optional-warning overlay if present,
and choose **Start camera capture**. Select the Kinect feed in Configuration if
needed. Use **Stop camera capture** when finished. Microphone listening is
separate. Builder remains its separate port-5000 application/launcher.

Detailed operation and optional speech installation are in the
[canonical guide](../../../docs/user/user_guide.md#start-the-repaired-local-sensory-runtime).

## Remaining priorities - not certified by these repairs

1. Implement and independently certify actual B1/B2 execution adapters and B3
   reference dimensions. The prior 4,567,641-parameter B3 experiment is not B1/39M.
2. Add model-forward causal-isolation tests and representative disjoint
   held-out quality/provenance. Prefix construction tests alone do not prove
   general causal semantics or useful assistant quality.
3. Verify real microphone transcription and camera-to-model visual understanding
   with explicit consent and retention rules. Neither follows from stream health
   or Whisper readiness alone.
4. Measure peak memory/latency and sustained concurrent operation on the 4GB
   target. Approximately 2.08GB allocated/2.14GB reserved was a live inference
   snapshot, not peak multimodal or native-model training certification.
5. Harden public deployment, untrusted legacy checkpoint loading and broader
   accessibility/browser failure coverage. The loopback Vite gateway is local
   development infrastructure, not public production hosting.

No full repository test suite, comprehensive security/accessibility certification,
IDS rebuild, useful-model-quality certification or public deployment was performed.
