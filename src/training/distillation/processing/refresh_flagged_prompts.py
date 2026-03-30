"""Utility to refresh low-signal teacher prompts across multiple datasets.

This script replaces the previously flagged prompts with updated wording
and regenerated dual-teacher responses so that downstream datasets remain
aligned with regulator rehearing scenarios.

Run:
    python -m src.training.distillation.processing.refresh_flagged_prompts
"""
from __future__ import annotations

import json
import textwrap
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

# Prompts that require replacement along with their new text and responses.
PROMPT_PATCHES: dict[str, dict[str, object]] = {
    "I'm studying philosophy but I'm confused. Can you clarify?": {
        "new_prompt": (
            "During the regulator rehearing briefing, one analyst says they are "
            '"lost in the philosophy" of why the pause is necessary. Draft a '
            "coaching response that reconnects them to statutory requirements "
            "and lists three concrete next actions."
        ),
        "responses": {
            "llama3.2:3b": textwrap.dedent(
                """
                I hear that the pause can feel abstract when we describe it as philosophy, so let us anchor it to the rules that bind this room. Remind the analyst that the pause power comes directly from Title 17 remediation clauses and is triggered whenever evidence packets or terminology drifts could misstate the statutory record. Then pivot to immediate actions:
                1. Re-read the controlling clause aloud so the whole table hears the precise language that obligates the pause.
                2. Capture in the shared log which definitions or acronyms fell out of sync and assign the compliance notetaker to draft refreshed terminology cards within the next 15 minutes.
                3. Schedule a two minute huddle before the rehearing resumes so the analyst can rehearse how they will restate the statutory rationale back to regulators.
                Close by normalizing the confusion, thanking them for flagging it early, and reaffirming that clarity keeps the organization credible with both regulators and affected customers.
                """
            ).strip(),
            "phi3.5:3.8b-mini-instruct-q4_K_M": textwrap.dedent(
                """
                Let us translate the why from philosophy into procedure. The temporary pause is not optional - it is mandated once our terminology drift jeopardizes an accurate statutory record. Walk the analyst through the compliance anchors: cite the rehearing rule that forces the pause, explain that unclear language can be interpreted as misleading disclosure, and connect that risk to the penalties regulators outlined on the first slide. Then issue three grounded tasks: (a) the legal lead reissues the statutory snippet in plain language and uploads it to the rehearing workspace; (b) the comms partner rebuilds the shared glossary slide with the updated terms and timestamps the revision; (c) the analyst owns a reassurance loop where they brief impacted stakeholders on why pausing protects their interests. That keeps the conversation practical, shows respect for the analyst's concern, and reinforces that compliance is our north star, not abstract theory.
                """
            ).strip(),
        },
    },
    "What signals indicate the team must pause a rehearing to refresh terminology baselines?": {
        "new_prompt": None,
        "responses": {
            "llama3.2:3b": textwrap.dedent(
                """
                Several concrete signals should trigger a terminology-refresh pause during a rehearing. Look for: (1) repeating cross-talk in which regulators and internal responders are using different acronyms for the same control; (2) incident notes that show three or more edits where teams replace statutory language with shorthand; (3) stakeholders asking for clarification on a safeguard that was considered settled in the previous hearing; (4) risk matrices where confidence scoring diverges because the definitions column no longer matches the glossary; (5) any escalation log noting that outside counsel cannot reconcile terms across artifacts. When two or more of those appear in a single cycle, announce the pause, reset the glossary baseline, and document the restart time so the transcript proves we realigned language before resuming testimony.
                """
            ).strip(),
            "phi3.5:3.8b-mini-instruct-q4_K_M": textwrap.dedent(
                """
                There are reliable cues that the conversation is drifting away from a shared terminology baseline. Trigger the pause when you observe combinations of: regulators correcting our phrasing three times within a single agenda block; transcript reviewers flagging inconsistent abbreviations between engineering and legal statements; decision matrices losing their legend so severity colors no longer match the written categories; customer advocates asking which privacy tier we are referencing because shorthand replaced the canonical term; or compliance noting that evidence packets cite an outdated regulation number. Any cluster of those signals means definitions are splintering, and the only safe move is to pause, refresh the glossary, and restart with everyone reading from the same statutory script.
                """
            ).strip(),
        },
    },
    "Which follow-through assignments ensure privacy requirements remain addressed after rehearing decisions?": {
        "new_prompt": None,
        "responses": {
            "llama3.2:3b": textwrap.dedent(
                """
                Treat post-rehearing privacy as a tracked workstream. Assign (1) the privacy counsel to draft the binding decision memo within four hours, explicitly mapping each ruling to the applicable privacy clause and publishing it in the regulator workspace; (2) the data protection engineer to update logging guards and produce a before-and-after screenshot set for auditors; (3) the customer trust lead to send tailored notices that explain what data handling changes occur and how opt-out pathways were preserved; (4) the audit analyst to schedule a 30 day follow-up review with metrics showing whether mitigations held; and (5) the rehearsal coordinator to archive every artifact, including glossary revisions, so the compliance trail is reproducible. Close the checklist with an owner acknowledgment meeting so no task lingers unassigned.
                """
            ).strip(),
            "phi3.5:3.8b-mini-instruct-q4_K_M": textwrap.dedent(
                """
                Anchor the follow-through in clear ownership. First, legal privacy counsel documents the decision rationale and uploads the signed summary to the secure case library. Second, security engineering executes the remediation ticket, attaches evidence of control changes, and links the work to the rehearing ID. Third, product or customer experience leads craft external messaging that reiterates consent options and references the exact privacy safeguards regulators asked about. Fourth, compliance operations schedules verification checkpoints - seven day spot check and 30 day audit - to confirm the safeguards stay in place. Finally, governance records management updates the retention matrix and confirms destruction windows remain lawful. Each assignment should have an owner, due date, and verification method so regulators see continuous stewardship, not just promises during the hearing.
                """
            ).strip(),
        },
    },
}

# Datasets that should receive the refreshed content.
TARGET_DATASETS: list[Path] = [
    Path("src/training/distillation/kd_inputs/generated/ollama_phi35_teacher_20251020.json"),
    Path("src/training/distillation/kd_inputs/generated/ollama_llama32_teacher_20251020.json"),
    Path("src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_conflict_lab.json"),
    Path("src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_compliance.json"),
    Path("src/training/distillation/kd_inputs/generated/ollama_combined_teacher_20251025_regulator.json"),
]


def _update_examples(examples: Iterable[dict[str, object]]) -> bool:
    changed = False
    for example in examples:
        prompt = example.get("prompt")
        if not isinstance(prompt, str):
            continue
        patch = PROMPT_PATCHES.get(prompt)
        if not patch:
            continue
        new_prompt = patch.get("new_prompt")
        if isinstance(new_prompt, str) and new_prompt != prompt:
            example["prompt"] = new_prompt
            prompt = new_prompt
        responses = example.get("teacher_responses")
        if isinstance(responses, dict):
            for teacher_id, replacement in patch["responses"].items():
                if teacher_id in responses:
                    responses[teacher_id] = replacement
        timestamp_key = "timestamp"
        if timestamp_key in example:
            example[timestamp_key] = datetime.now(timezone.utc).isoformat()
        changed = True
    return changed


def refresh_dataset(path: Path) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[skip] missing dataset: {path}")
        return False
    except json.JSONDecodeError as exc:
        print(f"[error] invalid json in {path}: {exc}")
        return False

    examples = payload.get("examples")
    if not isinstance(examples, list):
        print(f"[skip] no examples array in {path}")
        return False

    if not _update_examples(examples):
        print(f"[skip] no matching prompts found in {path}")
        return False

    payload["generation_timestamp"] = datetime.now(timezone.utc).isoformat()
    payload["total_examples"] = len(examples)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] refreshed prompts in {path}")
    return True


def main() -> None:
    updates = 0
    for dataset in TARGET_DATASETS:
        if refresh_dataset(dataset):
            updates += 1
    if updates == 0:
        print("[info] no datasets required refreshing")


if __name__ == "__main__":
    main()
