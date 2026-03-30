# Foundation Curriculum: "The Empathic Reasoner"

**Created:** December 24, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\foundation_curriculum.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

**Goal**: Train the B3-Triad to balance "Logical Reasoning" (Left) and "Creative Empathy" (Right) using the Colossus aggregator.
**Target Loss**: < 2.0
**Steps**: 5000 -> 10000

---

## 1. Data Sources (Weighted)

We will construct a dynamic curriculum from the following `F:/data` sources:

### A. The "Nexus" Core (Reasoning) - 40%

*   **Source**: `F:/data/reasoning/cot_logic`
*   **Format**: `(Question) -> (Chain of Thought) -> (Answer)`
*   **Purpose**: Train the "Left Hemisphere" capabilities.
*   **Nexus-L Integration**: All CoT steps will be wrapped in `(LOG "Reasoning: ...")`.

### B. The "Empathy" Layer (Conversation) - 30%

*   **Source**: `F:/data/conversation/therapy_transcripts` (Anonymized/Synthetic) & `everyday_dialogue`
*   **Format**: `(User) -> (Therapist/Friend)`
*   **Purpose**: Train the "Right Hemisphere" capabilities.
*   **Focus**: Emotional validation, active listening.

### C. The "Knowledge" Base (Grammar/Facts) - 20%

*   **Source**: `F:/data/english-grammar-clean` (OED/Webster snippets)
*   **Purpose**: Vocabulary precision and Colossus synthesis.
*   **Goal**: Ensure zero hallucinations on definitions.

### D. The "Self-Correction" (Nexus-L Syntax) - 10%

*   **Source**: Synthetic `nexus_syntax_examples.json`
*   **Purpose**: Fine-tune the model to output *valid* Nexus-L commands (`(SET-TEMP ...)`) perfectly.

---

## 2. Training Strategy: "Hemispheric Masking"

To simulate the Triad during training without training 3 separate models yet (which is slow):

1.  **Left-Masking**: Mask out "Emotional" tokens, force model to predict purely logical next-tokens.
2.  **Right-Masking**: Mask out "Logic" tokens, force model to predict purely conversational flow.
3.  **Colossus-Integration**: Present provided Left/Right outputs and force model to predict the "Synthesized" output.

## 3. Execution Plan

1.  **Generate Dataset**: Run `generate_curriculum_mix.py`.
2.  **Verify Batch**: Check token counts and masking.
3.  **Launch Trainer**: Using `diverse_curriculum_trainer.py`.
