# Live workbench acceptance report

Date: 2026-11-02, local timezone UTC-05:00.

Project: **B1 Hope 39M experiment - LIVE TESTING**  
Project ID: `d3c0663d86e342c986678975753e0308`  
Application: `http://127.0.0.1:5000/unified_builder`

## Result and important boundary

**The local native workflow passed end-to-end. This is NOT a B1 Hope 39M
architecture or quality certification.**

The saved project began at revision 1 with a B1 reference offering, but no
native architecture, dataset, tokenizer, or compatible checkpoint. The current
workbench runner implements native `ImpressionCoreB3Model` experiments; it does
not implement a verified B1-specific adapter. Initial preflight correctly blocked
training on the missing inputs.

The operator requested an observed browser walkthrough. A scope clarification
was attempted twice; the form returned unavailable both times (including after
the operator said they were available). The pragmatic continuation was announced
in chat: preserve the B1 reference and original settings, use an explicitly
labelled small native B3 workflow test, and do not claim that it trains B1 39M.
The same boundary is saved in the project's experiment notes.

The actual constructed model has **4,567,641 parameters**, not 39M.

## Preserved and populated inputs

- [Original revision 1 settings](original_project.json), before live edits.
- [Training input](train.txt): 24 original synthetic engineering sentences.
- [Held-out input](validation.txt): 8 distinct original synthetic sentences.
- Existing local tokenizer:
  `D:\Projects\impressioncore\src\training\tokenizers\b3_conversation_tokenizer_28k\tokenizer.json`.
  Measured vocabulary: 28,000, maximum token ID: 27,999.
- No downloaded data, tokenizer, model, or dependency was used.
- No existing training corpus or tokenizer was overwritten.

Executable configuration:

| Setting | Value |
|---|---|
| Architecture | Native B3, explicit small research configuration |
| Embedding / layers / heads | 64 / 2 / 4 |
| Experts / expert dimension / experts per token | 4 / 96 / 2 |
| Vocabulary / native context | 28,000 / 128 |
| MHC | Enabled, 20 iterations |
| Gradient checkpointing | Disabled for this bounded CPU test |
| Device / precision / microbatch | CPU / FP32 / 1 |
| Accumulation / learning rate / seed | 4 / 0.00005 / 42 |
| Training sequence length / epochs | 32 / 1 |
| Scratch limit | 6 optimizer steps |
| Fine-tuning limit | 2 optimizer steps, source = scratch checkpoint |

Preflight estimated a conservative 0.21 GiB FP32 training budget against about
19.8 GiB available RAM. This is a screening estimate, not a measured peak-RAM
profile. The detected GTX 1050 Ti has 4 GiB VRAM, but **these runs used CPU**;
they do not certify GPU training or larger-model fit.

## Browser walkthrough and evidence

All model configuration, saved-project edits, training, evaluation, generation,
and fine-tuning actions below were performed through the shared live browser,
not the isolated test server. Resource operations used the actual confirmation
dialogs.

1. Logged in locally and opened the existing named project; confirmed revision 1.
   Initial preflight blocked missing native config, data, tokenizer, and
   fine-tuning source. [Original project](01-original-project.png).
2. Preserved the B1 model reference and documented the small-native-test scope
   in experiment notes. Entered explicit native JSON rather than silently
   translating B1 dimensions. [Native configuration](02-native-configuration.png).
3. Populated the two local text paths and retained text format.
   [Data paths](03-dataset-paths.png).
4. Selected the existing 28,000-token tokenizer.
   [Tokenizer](04-tokenizer.png).
5. Chose scratch, CPU, one epoch, accumulation 4, sequence 32, maximum 6 steps;
   saved revision 2. Preflight passed all blocking checks. Warnings correctly
   identified random initialization and FP32/microbatch-1 research scope.
   [Ready preflight](05-preflight-ready.png).
6. Clicked Start and accepted confirmation. The native worker completed 6/6
   optimizer steps and wrote weights plus the exact tokenizer.
   [Completed scratch run](06-scratch-completed.png).
7. Inspected the durable native checkpoint.
   [Checkpoint view](07-checkpoint.png).
8. Selected the scratch checkpoint, confirmed held-out evaluation, and obtained
   real loss/perplexity on 8 records.
   [Scratch evaluation](08-scratch-evaluation.png).
9. Generated 16 tokens, temperature 0.7, prompt
   `The local experiment records`. Actual output was incoherent, with some
   control characters, as expected from almost-random weights after six steps.
   [Scratch generation](09-scratch-generation.png).
10. Clicked artifact export. The UI fetched the ZIP and reported a download.
    The integrated browser did not emit Playwright's download event; the
    waiter timed out. A separate authenticated **localhost** request retrieved
    the same endpoint's bundle, which was saved and verified.
    [Export UI](10-export-ui.png). This is an automation/download-observation
    limitation, not evidence that the exported model has useful quality.
11. Switched the saved project to fine-tuning, chose the scratch run as source,
    set a 2-step limit, and saved revision 3. Preflight confirmed exact native
    config and tokenizer identity. [Fine-tuning preflight](11-finetune-preflight.png).
12. Confirmed Start. Strict checkpoint loading succeeded; the new optimizer
    completed 2/2 steps and saved a second checkpoint.
    [Fine-tuning completion](12-finetune-completed.png).
13. Evaluated the fine-tuned checkpoint on the same held-out shard.
    [Fine-tuning evaluation](13-finetune-evaluation.png).
14. Generated 16 tokens from the fine-tuned checkpoint with the same prompt and
    temperature. Output remained incoherent.
    [Fine-tuning generation](14-finetune-generation.png).
15. Clicked configuration export and inspected the saved configuration.
    A separately retrieved export was parsed and compared to the saved project.
    [Configuration export](15-configuration-export.png).
16. Reviewed capability labels: exact optimizer resume/pause and tokenizer
    training remain unavailable; multimodal execution is not exercised by this
    text adapter. [Capability map](16-capability-map.png).
17. Added measured outcomes and evidence location to notes, saved revision 4,
    reloaded the page, reopened the existing project, and selected the completed
    fine-tuning run. Run history and evaluation persisted.
    [Reopened durable run](17-reopened-durable-run.png).

## Measured outcomes

| Measurement | Scratch | Fine-tuning |
|---|---:|---:|
| Run ID | `c9af53851adf41dba966e2a560f66b8f` | `71a68a5f9ccc460ba8e8d77880a03638` |
| State | completed | completed |
| Completed optimizer steps | 6 | 2 |
| Actual parameters | 4,567,641 | 4,567,641 |
| Final reported training CE | 10.271772 | 10.087341 |
| Held-out prediction CE | 10.262544 | 10.263847 |
| Held-out perplexity | 28,639.55 | 28,676.90 |
| Held-out records / predicted targets | 8 | 8 |
| Generated new tokens | 16 | 16 |

Held-out loss became slightly **worse**, not better. No learning-quality
improvement is demonstrated. Training losses in the table are different small
microbatch groups and should not be treated as an apples-to-apples benchmark.

Scientific semantics: one prefix predicts its next token per usable record.
The native router attends across the prefix; this is not all-position causal
language-model training. Held-out scores are prefix-prediction CE/perplexity,
not standard full-corpus perplexity or reasoning benchmarks. Eight records are
far too few for a reliable capability assessment.

## Artifact verification

Both bundles were downloaded through authenticated localhost API requests after
the browser export action. Each ZIP passed CRC checks and contains:

- `checkpoint.pt`
- `tokenizer.json`
- `run.json`, including immutable run configuration and latest measured metrics
- `evaluation.json`

Verification checked checkpoint SHA-256, exact tokenizer SHA-256, native
configuration, optimizer-step count, evaluation run identity, finite metrics,
and held-out sample count. Checkpoints were parsed locally with
`torch.load(..., weights_only=True)`. Fine-tuned and scratch tensors have
matching shapes; **104 state tensors differ**, confirming that fine-tuning
produced real weight updates. This is a new optimizer, not exact resume.

Files:

- [Scratch artifact ZIP](scratch-artifacts.zip)
- [Fine-tuning artifact ZIP](finetune-artifacts.zip)
- [Saved configuration export](project-configuration.json)
- [Machine-readable verification and hashes](verification.json)
- [Scratch run metadata](scratch-run.json)
- [Scratch evaluation](scratch-evaluation.json)
- [Fine-tuning run metadata](finetune-run.json)
- [Fine-tuning evaluation](finetune-evaluation.json)

Authoritative server artifacts remain at:

`F:\models\checkpoints\workbench\d3c0663d86e342c986678975753e0308\<run-id>`

The report folder holds explicit copies for this requested walkthrough.
Original revision 1 is a recovery/reference snapshot; do not overwrite the
current project JSON with it, bypassing revision checks. Import it as a new
configuration if a separate original-settings project is needed.

## Findings and follow-up

1. **B1 identity is not yet executable as B1.** Implement and verify a B1-specific
   adapter/config/tokenizer/checkpoint contract before claiming an actual
   B1 Hope 39M run. The current B1-labelled project executed explicitly
   documented native B3 research dimensions.
2. **The bounded native workflow works:** save, preflight, real scratch training,
   strict checkpoint fine-tuning, held-out evaluation, local generation,
   artifact packaging, and durable browser reopen.
3. **No language-quality claim:** tiny synthetic data, tiny model, few steps,
   high loss, incoherent output, and no held-out improvement.
4. **Download observation is limited:** UI export fetched data, but the
   integrated browser download event was unavailable. Saved bundle integrity
   was verified independently; a normal Chrome download-directory check is
   still distinct from this evidence.
5. **Not exercised live:** cooperative stop/interruption, import into another
   project, server restart recovery, multi-user access, CUDA training,
   multimodal training, tokenizer training, exact resume, quantization, and
   deployment. Existing automated tests are not substituted for those live
   acceptance claims.

Final intended state: original project identity retained, outcome notes saved,
two completed runs, no active training, fine-tuning configuration retained with
a 2-step bound. The shared browser is left on the persisted evaluation result.
No application source code was changed for this live walkthrough.
