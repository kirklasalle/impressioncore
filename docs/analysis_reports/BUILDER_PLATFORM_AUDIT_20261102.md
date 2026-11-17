# ImpressionCore Builder, runtime, artifact and market readiness audit

**Audit date:** November 2, 2026

**Status:** Evidence-based research-platform assessment; production certification withheld.

**Scope:** Builder workflow, native model identity/objectives, representative artifacts,
React/Triad connectivity, Kinect integration, documentation consistency and public alternatives.

## Repair addendum — November 2, 2026

The original audit below is a **pre-repair snapshot**, retained for traceability.
The user subsequently authorized implementation of the next priorities.
Current repair evidence and exact validation results are in the
[runtime repair report](../../src/memlog/runtime_repair_20261102_195218/REPAIR-REPORT.md).

- Replaced the broken cross-origin browser boundary with a guarded loopback
  same-origin gateway. Credentials remain in the supervising processes, not the
  browser bundle. Direct protected API requests still return 401; hostile-origin
  gateway requests are rejected. CORS covers actual error responses and
  WebSockets/media follow the authentication boundary.
- Background initialization exposes liveness/readiness and real startup errors.
  Model-load failure cannot silently become a mock READY; generation failures
  and empty outputs fail explicitly rather than masquerading as assistant text.
- The real browser received an answer from the existing **InternVL2-1B
  (InternVLChatModel, 938,158,976 parameters)**. This is an external pretrained
  runtime, not a native B1/B2/B3 checkpoint. Its weights and Kinect drivers
  were not replaced.
- Explicit camera Start/Stop replaces automatic capture. A native frame-release
  defect exhausted SDK buffers after six frames; fixed release handling now
  supports increasing color/depth/skeleton counters and a rendered 480x360
  browser preview. IR is unavailable while RGB occupies the shared sensor path.
  No camera frames or microphone recordings were saved for this repair.
- Added the optional `speech` extra; installed its missing dependency and cached
  the small CPU Whisper `tiny.en` model. STT reports available/model-loaded,
  **not listening**. This verifies readiness, not microphone transcription quality.
- Native preflight, checkpoints and exports now identify the measured
  implementation/configuration/count/tokenizer/objective and hashes. B1/B2
  execution is unavailable; B3 named references remain uncertified. Explicit
  small native B3 experiments remain supported under truthful reference labels.
- The objective is explicitly `prefix_next_token`; construction tests verify
  that a selected target's future suffix is not supplied as input. They do
  **not** prove general all-position causal isolation in the architecture.
- Added a scoped ESLint correctness configuration; lint/build now pass.
  The isolated native Builder browser workflow still trains, evaluates,
  generates, exports verified artifacts and reopens durable projects.

**Still open:** certified native offering adapters/dimensions; representative disjoint datasets and useful
held-out quality; actual speech and visual-language accuracy; sustained
peak-memory measurement on the 4GB target; comprehensive accessibility,
legacy archive `torch.load` cleanup, and full CI `ruff`/`mypy` enforcement.
The local Vite gateway is a developer boundary, not a public hosting solution.

## Immediate blockers & Phase 2–3 remediation addendum — November 16, 2026

Following the November 16, 2026 principal-engineer due-diligence audit, immediate stop-ship blockers and Phase 2–3 hardening items were remediated without modifying legacy `src/archive/` or `src/deployment/`:

- **Builder API & Workbench confinement (`SEC-01`, `SEC-03`):** `src/interfaces/web/server.py` now binds `127.0.0.1` by default (`IMPRESSIONCORE_BUILDER_HOST`), disables Werkzeug debugger unless `IMPRESSIONCORE_DEBUG=1`, enforces `get_allowed_origins()` CORS instead of `*`, and requires `X-API-Key` (when `IMPRESSIONCORE_API_KEY` is set) or an authenticated session on `/api/*`. `src/interfaces/web/routes/workbench.py` (`bounded_file`) now confines reads to resolved project, data, checkpoint, and configured roots.
- **Safe checkpoint deserialization (`SEC-02`):** Active `torch.load` paths in `src/interfaces/web/routes/builder.py`, `src/core/assembly_of_experts.py`, and `src/core/models/impressioncore_b3_architecture.py` now enforce `weights_only=True`, and `builder.get_model_tokenizer()` rejects `.pt` paths outside allowed roots.
- **Cryptography, Safe Evaluation & Remote Code (`SEC-04`, `SEC-05`, `SEC-06`):** `src/core/security/identity/cryptographic_core.py` now uses real `ChaCha20Poly1305`/`AESGCM`, fails closed without XOR fallbacks, and disables simulated PQC unless `allow_simulated_pqc=True`; `src/core/security/encryption/aes_encryption.py` (`decrypt_file`) fixes an EOF infinite-loop/OOM bug on `infile.read(4) == b""`. `eval()` in `rule_engine.py` and `cli_tokenizer_utils.py` was replaced with `_safe_eval_formula()` (AST allowlist) and `ast.literal_eval()`; `os.system()` in `.mcp/vrgc/tools/covenant_guardian.py` was replaced with `subprocess.run(..., shell=False)`; `unified_triad.py` gates `trust_remote_code` and supports `model_revision` pinning.
- **Native B3 causal isolation & FAISS retrieval (`CRIT-01`, `CRIT-05`):** `EfficientMultiHeadLatentAttention` (standard, cached, sliding-window, and prefix-cumsum linear attention) and `AssemblyOfExperts.routing_attention` in `src/core/models/impressioncore_b3_architecture.py` now enforce causal masking and per-sample batch padding masks; `recombine_windows()` fixes span tracking and `(1, seq_len, 1)` normalization; `BrainInspiredTransformerLayer` reconstructs the actual FAISS indices returned by `retrieve_memory`.
- **Quantization & MHC correctness (`CRIT-02`, `CRIT-03`, `NOV-01`):** `src/core/quantization/turboquant.py` falls back to exact QR orthogonal rotations for non-power-of-2 dimensions and preserves floats when `enabled=False`. `builder.py` and `src/core/export/export_production_model.py` emit symmetric scale factors with `scale.clamp(min=1e-8)`. `src/models/layers/mhc.py` (`MHCProjection`) applies Sinkhorn-Knopp only to square matrices.
- **Governance, Containers & Portability (`ARCH-01`, `ARCH-02`, `ARCH-03`, `DOC-01`):** `agent0core/core/guardian_agent.py` checks actual workspace/tool/supervisor/MCP/ledger state instead of unconditional stubs; `docker/Dockerfile.python` copies `run_server.py` and runs as non-root `appuser`; `requirements.txt` and `pyproject.toml` add `websockets>=12.0` and `cryptography>=42.0.0` (removing duplicates/stale packages); `src/core/security/tests/test_integration_security.py` imports `src.core.security.*`; `src/interfaces/routes/rlm.py` and `builder.py` remove hardcoded machine-specific paths; `README.md` documents the preset matrix reference distinction.
- **Verification:** Covered by `src/tests/core/test_immediate_blockers.py` and `src/tests/core/test_phase2_phase3_hardening.py` alongside `src/tests/core/`, `test_turboquant.py`, `test_turboquant_kv_cache.py`, `test_b3_forward_pass.py`, and `test_agent0_guardian.py`.

## 1. Decision

**Keep the Unified Builder and develop it as ImpressionCore's native research IDE.**
The persistent experiment workflow has demonstrated value. It is not yet a certified
B1/B2/B3 training product, a validated general-purpose assistant, or a production-ready
camera/audio platform. Those are separate acceptance gates.

The immediate problem is **not established to be a missing Kinect or missing LLM**.
The supplied backend log records Kinect initialization and model loading. The React
interface cannot read protected runtime endpoints: its requests lack the required
API authentication, and the resulting HTTP 401 responses are obscured by missing CORS
headers. This was reproduced in a real browser and with direct HTTP probes.

Do not replace a working driver, download another model, or repeat training to fix
that frontend/API boundary. Fix authentication, error propagation and truthful
readiness first; then verify the actual sensor and inference paths.

### Capability verdict

| Area | Evidence | Current verdict |
|---|---|---|
| Native Builder project lifecycle | Durable projects, bounded preflight, training, checkpoints, held-out evaluation, generation, export and reopen exercised | Demonstrated for a small native B3 text experiment |
| B1 Hope 39M identity | B1-labelled project executed a measured 4,567,641-parameter native B3 configuration | **Not B1/39M certification** |
| B1/B2/B3 default selections | Registered reference offerings populate project creation | Selection does not establish an executable native architecture or certified size |
| Model usefulness | Tiny synthetic run generated incoherent text; held-out loss did not improve | No demonstrated assistant-quality improvement |
| Kinect backend | Supplied log: one SDK sensor, streams, skeleton, successful face-tracking retry and brightness samples | Positive backend evidence; not a new independent sustained-stream test |
| React camera/model display | Real browser requests fail; protected endpoints return 401 | **Integration blocked**, not evidence that hardware/weights are absent |
| Speech transcription | Supplied log reports missing `faster_whisper` | Unavailable in that runtime session |
| Windows/4GB target | Existing GPU identified; one memory-usage snapshot taken | No full-model training, sustained multimodal or peak-memory certification |
| Production/security/accessibility | Limited prior responsive checks and focused tests, no comprehensive certification | Release gates remain open |

## 2. What the audit covered, and what it did not

This is a **cross-stack, risk-prioritized audit**, not a claim that every repository
line, binary, historical report or model weight was validated. Findings distinguish
observed behavior, source-level risks and unverified claims.

Git inventory at audit time contained **5,578 tracked files**, **2,066 Python files**,
**2,148 documentation/README files**, and **123 files under the tracked test tree**.
These counts include index entries and exclude ignored external model/data storage;
they are inventory, not review-coverage percentages or test-case counts.

A separate filesystem documentation inventory counted **3,238 files**, including
786 Markdown, 826 HTML and 853 PNG files; 140 files were under the documentation
archive. Filesystem counts include untracked files and are not directly comparable
to Git counts. This volume is one reason to maintain canonical documents and
supersession notices rather than silently rewriting every historical report.

### Review coverage

- **Executed:** local public/protected HTTP and CORS probes; browser fetch reproduction;
  focused isolated tests; sensory frontend build/lint commands; read-only OS/GPU/listener metadata.
- **Read:** frontend polling/device-merging paths, API middleware/lifecycle/status,
  Triad model lifecycle, Kinect connector contracts, canonical offering/native
  objective/inference paths, representative production metadata, active documentation
  and public entry-page claims.
- **Reused with attribution:** the earlier observed Builder walkthrough, saved runs,
  screenshot report, checkpoint/export hash verification and exact parameter count.
- **Public research:** official product/project documentation for alternative components
  and Microsoft/OpenKinect SDK/driver distinctions.
- **Not executed:** new camera/audio capture, inference-quality benchmark, full-size
  training, weight-by-weight legacy checkpoint validation, clean-machine installation,
  exhaustive test suite, dependency vulnerability scan, penetration test, or a new
  full accessibility/performance audit.
- **Not changed:** application source, drivers, models, dependency manifests, credentials
  or shared running services during this audit. Documentation/evidence were updated.
  The existing frontend build command regenerated ignored build output.

Primary local evidence:

- [Observed Builder walkthrough and 17 screenshots](../../src/memlog/live_workbench_20261102_184402/LIVE-TEST-REPORT.md).
- [Persistent runtime observations and validation results](../../src/memlog/audit_20261102/runtime-evidence.json).
- The user-supplied November 2 startup log was reviewed in place. It is not copied
  into public documentation; only relevant non-sensitive diagnostic facts are summarized.

## 3. Two applications, not one readiness signal

| Surface | Purpose | Entry point | Audit observation |
|---|---|---|---|
| Flask Unified Builder | Native experiment authoring and artifact workflow | `http://127.0.0.1:5000/unified_builder` | Previously exercised live; port 5000 was not listening during this audit's later probes |
| React sensory client | Conversational/sensory operator interface | `http://localhost:5173` | Running; protected runtime calls fail |
| Triad API | Sensory orchestration and configured model runtime | `http://127.0.0.1:8000` | Running; public root returns 200 |

The Builder launcher and full-stack launcher are different launch paths. A stopped
Builder listener is not proof of a broken saved project. A passing Builder test is
not proof that React camera/model integration works. Flask development login and
Triad API-key authentication are also separate mechanisms.

The Triad source defaults to **OpenGVLab/InternVL2-1B**, shared across three prompted
roles. It is not three independently trained native ImpressionCore brains and is
not the small native B3 model used by the Builder experiment. See
[Triad initialization](../../src/orchestrator/unified_triad.py#L64).

## 4. Reproduced camera/model display failure

### Observations

| Probe | Result |
|---|---|
| `GET /` on port 8000 | 200; reports `ONLINE` |
| `GET /openapi.json` | 200 |
| Unauthenticated `GET /v1/hardware` | 401 |
| Unauthenticated `GET /v1/model/status` with React origin | 401; no `Access-Control-Allow-Origin` |
| `OPTIONS /v1/hardware`, origin `http://localhost:5173` | 200; expected origin allowed |
| Browser fetch to public root from React origin | 200 |
| Browser fetch to protected hardware/model paths | `Failed to fetch`; CORS/network errors |

The default allowed-origin list already includes localhost and 127.0.0.1 on port
5173. **Successful preflight is not a successful authenticated request.**

### Root cause

1. The React application issues direct Axios calls without API-key/session integration:
   [request setup](../../src/interfaces/web_client/src/App.jsx#L9),
   [status polling](../../src/interfaces/web_client/src/App.jsx#L2682).
2. The API requires `X-API-Key` on protected HTTP paths:
   [authentication middleware](../../src/interfaces/triad_api.py#L203).
3. That outer middleware returns a 401 response without traversing the inner CORS
   middleware. The browser hides the response from frontend code and reports a
   network/CORS failure.
4. The UI converts missing status data into disconnected/zero/standby labels:
   [readiness overlay](../../src/interfaces/web_client/src/App.jsx#L1817).
   These labels conflate **unknown because unauthorized** with **confirmed absent**.

**Required repair:** establish one deliberate browser authentication/session boundary
for HTTP, WebSocket and image-stream transports, preferably through a same-origin
server-side boundary that does not publish a service secret in the JavaScript bundle.
Apply CORS to error responses where cross-origin requests remain necessary. Validate
runtime key configuration explicitly and display actionable unauthorized/unreachable/
initializing/degraded states.

Do **not** disable authentication, add wildcard credentialed CORS, hardcode a secret
in frontend source, or treat another model download as the remedy. A complete
security design/review remains a separate release requirement.

## 5. Kinect and audio evidence

The supplied session began at **18:53:10**; Uvicorn reported startup complete at
**18:56:15**. The log then records:

- Kinect SDK reports **one sensor**.
- Native enhanced bridge loaded; Kinect v1 linked.
- Color locked as **YUV 640 x 480**.
- Depth opening logged as **320 x 240**, plus skeleton tracking enabled.
- Initial face-model path failed with `0x80070002`; the NULL-path retry **succeeded**.
- Vision became active; later color/depth brightness samples were logged.
- A **Kinect USB Audio four-channel** device was enumerated through multiple audio
  host APIs. Multiple indices do not establish multiple physical microphones.
- InternVL weights loaded and VRAM allocation was reported successful.
- `faster_whisper` was missing; transcription was unavailable.

This contradicts a blanket conclusion of “no camera/no LLM.” It does not prove
every stream, physical channel, inference result or user-visible rendering is good.
The audit did not request new frames, audio recordings or inference.

### Remaining implementation risks

- [Kinect open](../../src/orchestrator/kinect_connector.py#L411) logs depth opening
  without checking its returned HRESULT, and `isOpened()` reflects a broad
  initialization flag rather than stream freshness. Log messages alone cannot certify
  successful frames from every advertised stream.
- [Hardware status](../../src/interfaces/routes/system.py#L32) creates logical depth/IR
  entries when Kinect color exists. Enabled/configured state is not measured
  availability; physical-sensor counts and logical-stream counts must be separate.
- Kinect v1 RGB and IR share a sensor path and are generally mutually exclusive;
  do not promise simultaneous RGB+IR simply because both controls exist.
- [Audio classification](../../src/orchestrator/audio_engine.py#L109) marks four-channel
  devices as PS Eye candidates, including the enumerated Kinect array.
- [Frontend device merging](../../src/interfaces/web_client/src/App.jsx#L2792) adds
  backend microphones to state and then overwrites that state with browser-only
  audio devices. Authentication repair alone will not correct this merging defect.
- Browser `enumerateDevices()` is not an authoritative inventory of SDK-managed
  Kinect streams. Browser media permission and backend SDK permission are different.
- [API startup](../../src/interfaces/triad_api.py#L99) automatically opens vision.
  Explicit capture consent, visible capture state, stop/release, retention and deletion
  controls need acceptance tests before routine sensory deployment.

### Platform compatibility

Read-only metadata identified **Windows 10 Pro build 19045**, a **GTX 1050 Ti**, a
4,096 MiB GPU and driver 582.78. A single `nvidia-smi` snapshot showed **2,556 MiB used**.
That is shared instantaneous GPU usage, not model-only allocation, a peak, or proof
that a complete workload fits.

The current connector uses **Kinect10.dll / Kinect v1 APIs**, not SDK 2.0.
Microsoft's SDK 1.8 download page lists older Windows versions; successful local
operation on Windows 10 is valuable evidence but not a vendor support certification.
SDK 2.0 targets Kinect v2 and is not an interchangeable driver upgrade for Xbox 360
Kinect. Preserve the observed working installation while fixing the application
boundary. Any future libfreenect experiment belongs in an isolated compatibility
plan; it is not a transparent replacement for Microsoft skeleton/face tracking.

## 6. Ranked code and scientific-readiness findings

Priorities below are product/scientific blockers, **not vulnerability severity
ratings**. “Observed” means directly reproduced or recorded in the supplied/live
evidence; “source” means a high-confidence implementation risk not triggered here.

| ID | Priority | Finding | Evidence type | Required acceptance gate |
|---|---|---|---|---|
| A01 | P0 | React/runtime authentication and CORS error boundary broken | Observed HTTP and real browser | Authorized browser status works; unauthorized responses remain understandable without weakening access control |
| A02 | P0 | Mock fallback can report a real model as ready | Source | Forced load failure cannot produce real-model `READY`/`llm_loaded`; mock/demo mode explicitly labelled |
| A03 | P0 for named-offering release | Offering names do not identify certified executable B1/B2/B3 models | Source plus live experiment | Native registry binds exact implementation/config/count/tokenizer/checkpoint identity |
| A04 | P1 | General B3 all-token training lacks demonstrated causal isolation | Source | Future-token perturbation/leakage tests across relevant attention/router paths; objective labelled precisely |
| A05 | P1 | Some inference paths use permissive checkpoint loads or unrelated tokenizer defaults | Source | Strict architecture/config/tokenizer hash match; explicit separation of generic HF and native inference |
| A06 | P1 | Legacy production artifact metadata/count/quality claims do not reconcile | Metadata review | Rebuildable manifest, exact count, hashes, lineage, evaluation and correct loader target |
| A07 | P1 | Cold startup blocks HTTP readiness behind heavyweight initialization | Observed log plus source | Cheap liveness independent of model/capture initialization; separate component readiness and visible progress/errors |
| A08 | P1 | Kinect flags/logs are not per-stream health; audio enumeration/merging is inconsistent | Source plus log | Fresh-frame counters/age and deduplicated provider-aware device inventory |
| A09 | P1 | STT dependency unavailable in supplied session | Observed log | Explicit optional capability status and separately approved dependency/model setup |
| A10 | P1 | Quality and low-memory claims exceed measured evidence | Documentation versus live metrics | Versioned held-out baseline/evaluation and reproducible peak-memory report |
| A11 | P1 | Frontend lint release command cannot run successfully | Executed | Checked-in compatible lint configuration and passing command |
| A12 | P1 before distribution | Capture consent, packaging and production assurance incomplete | Source/review boundary | Explicit capture lifecycle; clean install/recovery, access-control and release audits |

### A02: real versus mock readiness

[Triad model loading](../../src/orchestrator/unified_triad.py#L194) catches a load
failure and returns `MockBrainModel`; the caller subsequently sets the loading
phase to `READY`. [Model status](../../src/orchestrator/unified_triad.py#L832) derives
`llm_loaded` from that phase, not verified model identity. This is a **latent risk**;
the supplied log does not establish that this session used the mock.

### A03: model sizes must come from the implementation

[Canonical presets](../../src/core/config/presets.py#L10) are generic reference
dimensions. The [Workbench](../../src/interfaces/web/routes/workbench.py#L317)
deliberately preserves the offering as reference metadata rather than claiming
an architecture adapter exists.

With the current B3 implementation's separate token embedding and untied output
head, `2 x vocabulary x width` alone gives:

| Reference dimensions | Embedding plus output-head parameters, before any layers |
|---|---:|
| B1: 50,257 vocabulary, width 768 | 77,194,752 |
| B2: 50,257 vocabulary, width 832 | 83,627,648 |
| B3: 50,257 vocabulary, width 3,072 | 308,779,008 |

These are architectural lower bounds, **not measured complete model sizes** and
not evidence that the reference presets should be silently converted into B3
models. The B1/B2 named targets cannot be inferred from those dimensions under
this implementation. Tests must instantiate the intended architecture, count
parameters and enforce an explicitly documented tolerance.

### A04-A05: training and inference identity

The [B3 forward loss](../../src/core/models/impressioncore_b3_architecture.py#L1397)
shifts labels, while standard attention can use no mask and routing attention has
additional cross-token interactions. Shifting labels alone does not establish
causality. The [Workbench objective](../../src/interfaces/web/routes/workbench_runtime.py#L68)
instead predicts a held-out next token from a record prefix; it should remain
labelled **prefix-next-token**, not standard all-position causal LM training.

The [native inference utility](../../src/inference/b3_native_inference.py#L110) has
permissive checkpoint/tokenizer paths, and the
[legacy Builder loader](../../src/interfaces/web/routes/builder.py#L2710) can select
generic HF model defaults and `strict=False` loading. The stricter Workbench
checkpoint/tokenizer contract should become the common native contract, with
legacy/generic routes distinctly labelled and tested.

## 7. Artifact and quality audit

### Verified small-experiment evidence

The saved **B1 Hope 39M experiment - LIVE TESTING** project retained its B1 reference,
but executed a small **native B3, 4,567,641-parameter** model on CPU/FP32. It used
24 synthetic training records, eight held-out records, six scratch steps and two
fine-tuning steps. Fine-tuning began with a new optimizer, not exact optimizer resume.

| Metric | Scratch | Fine-tune |
|---|---:|---:|
| Held-out cross entropy | 10.2625437975 | 10.2638473511 |
| Held-out perplexity | 28,639.5468 | 28,676.9043 |
| Held-out records | 8 | 8 |

The held-out metric worsened slightly and generation was incoherent. These outcomes
are recorded, not hidden. Two native export bundles and their checkpoint/tokenizer
hashes were verified in the earlier walkthrough; 104 state tensors changed after
fine-tuning. This proves an operational training/artifact loop, **not useful model
quality, a 39M B1 model, or successful real-world fine-tuning**.

### Representative legacy artifact concerns

- External production `b3_hope_v1` metadata claims B3-39M and training stages, while
  its config/size do not by themselves reconcile that identity. The selected
  checkpoint file is **2,024,463,173 bytes**. File size alone cannot determine
  parameter count because dtype, optimizer state and serialization differ.
- Local production metadata names `model_production.pt`, but the
  [production inference loader](../../src/models/production/production_inference.py#L57)
  chooses `model.pt`. The artifact loaded must match the artifact evaluated.
- [Real-versus-simulation report](../../src/training/REAL_VS_SIMULATION_TRAINING_REPORT.md) quality
  claims conflict with the [metrics transparency report](../../src/training/METRICS_TRANSPARENCY_REPORT.md),
  which describes estimated scores and the need for actual evaluation.
- Root artifact directory counts were bounded metadata inventory only:
  `checkpoints` 2 files, `models` 22, `production_packages` 42, `output` 0.
  External storage, source-tree artifacts and unrelated locations were not fully
  enumerated. These counts establish neither validity nor completeness.

No arbitrary legacy weight file was deserialized, fully hashed or certified in this
audit. A historical “production” filename, ZIP, high rating or screenshot is not
sufficient provenance.

### Required release artifact contract

Every releasable model needs a manifest binding: native implementation/version,
complete configuration, measured parameter count, weight dtype, tokenizer/hash,
dataset/version/license/splits, seed, objective, optimizer/resume semantics,
training lineage, checkpoint hashes, environment and evaluation protocol/results.
Exports need a clean-environment import/inference test. Signing and distribution
controls should follow the actual release threat model; no cryptographic assurance
is implied by a plain hash.

## 8. Builder roadmap: next work in dependency order

These are acceptance gates, not calendar estimates. Do not start a large training
run merely because a later milestone appears on a roadmap.

1. **Restore trustworthy runtime connectivity.** Unify browser authentication and
   error-state handling across HTTP/WebSocket/stream transports. Test authorized
   success, unauthorized failure, allowed-origin error headers, unavailable API,
   startup and reconnect. Keep secrets server-side. Do not auto-restart shared services.
2. **Make readiness truthful.** Separate real/mock, configured/loaded/usable,
   discovering/initialized/receiving/rendered, and liveness/readiness. Initialization
   must expose progress and failures without blocking the cheap health interface.
3. **Certify native offerings.** Introduce explicit B1/B2/B3 implementation adapters
   or mark unsupported entries unavailable for execution. Bind configs, actual
   parameter counts, tokenizer, checkpoint schema and supported modalities. Preserve
   existing project reference metadata and require explicit migration.
4. **Validate learning semantics.** Add future-token leakage tests before causal-LM
   claims; keep prefix-next-token as a distinct supported objective. Unify strict
   checkpoint/tokenizer identity and test scratch/fine-tune/exact-resume separately.
5. **Harden the scientist workflow.** Dataset provenance/licensing, split/dedup
   reports, baseline comparisons, seeded repeatability, experiment comparison,
   checkpoint selection and measurable quality gates. Preserve raw metrics and
   failures; thresholds must be specified for a particular task before evaluation.
6. **Verify Kinect with explicit consent.** Start/stop/release, provider identity,
   physical-versus-logical inventory, per-stream HRESULT/error/freshness/FPS,
   RGB/IR constraints and unplug/reconnect behavior. Only then verify browser
   rendering and model-context ingestion; sensor detection alone is insufficient.
7. **Establish the hardware envelope.** Reproducible CPU and GTX 1050 Ti runs with
   exact shapes, precision, peak GPU/RAM, latency and resource contention. Set
   reject/queue/offload policies; a mock route test is not a 4GB training benchmark.
8. **Close release gates.** Restore lint, validate packaging and clean installation,
   backup/recovery, accessibility/keyboard states, access control and dependency
   review. Run failure-path and browser regressions, then update capability badges.

### Intended users and product boundary

The Builder is for **ImpressionCore researchers and engineers** defining native
experiments, comparing runs, validating models and handing off reproducible artifacts.
The sensory client is for operating an assistant with approved devices and a known
model. Keep their purposes distinct while sharing a durable model/artifact registry,
authentication and capability schema.

Keep the existing project/data/model/train/evaluate/infer/artifact workbench. Add
registry certification, comparisons and sensory integration only behind real
capability checks. More menus alone will not create the missing implementation.

## 9. Current alternatives and market positioning

This is a public-source **component comparison**, not a market-share forecast or a
claim that every possible competing product was assessed. No TAM/ARR/valuation,
“world-first,” “10/10,” or benchmark-superiority claim is certified here. Older
strategic forecasts should be treated as historical hypotheses unless sourced and
methodologically reproducible.

| Need | Closest component(s) | Important boundary |
|---|---|---|
| Useful local chat/inference now | llama.cpp or Ollama with Open WebUI; LM Studio as a desktop option | Published supported models, not automatic native ImpressionCore compatibility |
| Low-VRAM inference | llama.cpp quantized CPU/hybrid offload | Exact model, backend, driver and peak workload still need measurement; no GTX 1050 Ti guarantee |
| GUI fine-tuning of supported existing model families | LLaMA-Factory | Windows installation instructions exist; exact training-stack/card compatibility still needs validation. Not an out-of-box B1/B2/B3 native IDE |
| Larger-scale pretraining/fine-tuning framework | NVIDIA NeMo | Extensible research framework, not the intended 4GB Windows consumer workbench |
| Kinect v1 acquisition | Existing Microsoft SDK 1.8 integration; libfreenect for a separately planned community-driver path | SDK 2.0 is for Kinect v2; driver/API/skeleton/face contracts differ |
| Combined custom native Builder plus Kinect conversational system | No drop-in replacement established by this survey | Requires composition and integration; absence from this survey is not proof of uniqueness |

**Practical recommendation:** if the immediate goal is reliable useful conversation,
use a measured, supported published model/runtime as a clearly labelled inference
backend while retaining ImpressionCore's native Builder research track. Do not
silently replace the native architecture or represent external model output as
native B1/B2/B3 output. Kinect remains a separate approved acquisition/context layer.

### Primary public sources

Retrieved/reviewed November 2, 2026; recheck current installation, licensing and
hardware requirements before adoption. Project code licenses do not automatically
license model weights, training data or redistribution.

1. [llama.cpp official project](https://github.com/ggml-org/llama.cpp) - local inference,
   quantization, CPU/GPU backends and hybrid offload.
2. [Ollama Windows documentation](https://docs.ollama.com/windows) - Windows runtime
   installation and requirements.
3. [Open WebUI official project](https://github.com/open-webui/open-webui) - self-hosted
   inference frontend; its custom license includes branding conditions, so do not
   treat it as plain BSD-3-Clause. Inspect the current terms before redistribution.
4. [LM Studio documentation](https://lmstudio.ai/docs/app/basics) - local desktop inference,
   offline use and system requirements.
5. [LLaMA-Factory official project](https://github.com/hiyouga/LLaMA-Factory) - supported
   model families and fine-tuning/Web UI capabilities.
6. [NVIDIA NeMo official organization](https://github.com/NVIDIA-NeMo) - current
   training/speech framework projects; not evidence of this machine's compatibility.
7. [Microsoft Kinect for Windows SDK 1.8](https://www.microsoft.com/en-us/download/details.aspx?id=40278)
   - v1 SDK requirements and download.
8. [Microsoft Kinect for Windows SDK 2.0](https://www.microsoft.com/en-us/download/details.aspx?id=44561)
   - distinct v2 SDK requirements.
9. [OpenKinect libfreenect](https://github.com/OpenKinect/libfreenect) - community Kinect
   v1 device access; not an interchangeable Microsoft skeleton/face SDK.
10. [Open WebUI license](https://github.com/open-webui/open-webui/blob/main/LICENSE) -
    current redistribution/branding terms, distinct from model and dataset licenses.

## 10. Validation and open release gates

Executed from repository root unless a working directory is stated:

```powershell
.\.venv310\Scripts\python.exe -m pytest src\tests\core\test_workbench.py src\tests\core\test_walkthrough_handoff.py src\tests\core\test_runtime_mode_config.py src\tests\core\test_cors_config.py -q
```

**Passed: 77 tests**, with two existing SWIG deprecation warnings. This validates
the selected isolated paths, not all API/hardware/model behavior.

From `src\interfaces\web_client`:

```powershell
npm run build
npm run lint
```

- **Build passed**, with an outdated Browserslist data warning.
- **Lint failed, exit 2:** ESLint configuration not found. Dependencies are present;
  installing more packages would not remedy the absent configuration. No tooling
  or configuration was added as part of this documentation audit.
- **Live browser integration failed** at the authentication/CORS boundary as
  reproduced above. It remains unfixed in source; a successful production build
  does not overrule that runtime result.

The report, evidence JSON, documentation links and scoped whitespace are checked
as audit deliverables. Any validation limitation is recorded rather than presented
as a passing production gate.

## 11. Documentation policy after this audit

The [canonical user guide](../user/user_guide.md), [next steps](../process/next_steps.md),
[roadmap](../process/development_roadmap.md) and [PRD](../reference/prd.md) should
distinguish **demonstrated / limited / legacy / planned / blocked** capabilities.
Maintained mirrors stay synchronized; pointer redirects stay pointers.

Current-status notices supersede conflicting historical readiness claims without
silently changing the historical body. Public screenshots and fixed telemetry are
illustrative, not evidence that a visitor's current device/model is connected.
Archived reports remain historical evidence, not current release approvals.

**Bottom line:** the Builder is worth continuing. The next investment is truthful,
authenticated integration and reproducible native model identity, followed by
scientific and hardware validation - not more marketing claims or blind driver/model
replacement.
