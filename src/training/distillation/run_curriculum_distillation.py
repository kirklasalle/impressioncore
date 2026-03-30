#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #multimodal #python #source_code #src/training/distillation\run_curriculum_distillation.py #training
**Category:** Training System
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #multimodal #python #source_code #src\\training\\distillation\\run_curriculum_distillation.py #training
# Category:** Training System
# Status:** Active

"""
Automated curriculum distillation runner for ImpressionCore B2.
Runs 3 progressive sessions per teacher model, increasing complexity each time.
"""

from training.distillation.b2_knowledge_distillation_trainer import B2KnowledgeDistillationTrainer

TEACHER_MODELS = [
    "qwen2:0.5b",  # Add more as needed
    # "qwen2:1b",
    # "tinyllama:1.1b",
    # "phi-3.5-mini"
]

CURRICULUM = [
    {"stage": "Foundation", "max_context_length": 128, "noise_level": 0.0, "notes": "Simple Q&A, clean data"},
    {"stage": "Intermediate", "max_context_length": 256, "noise_level": 0.1, "notes": "Longer context, some noise"},
    {"stage": "Advanced", "max_context_length": 512, "noise_level": 0.2, "notes": "Real-world, noisy, multimodal"},
]

def run_curriculum():
    import os

    from tqdm import tqdm
    # Define per-stage quality thresholds for adaptive progression
    STAGE_THRESHOLDS = {
        "Foundation": 6.0,
        "Intermediate": 7.0,
        "Advanced": 8.0
    }
    import datetime
    log_dir = "F:/impressioncore-b2-models/distillation/logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    log_file_path = os.path.join(log_dir, f"{timestamp}.log")
    for teacher in tqdm(TEACHER_MODELS, desc="Teacher Models", leave=True):
        print(f"\n=== Starting curriculum for teacher: {teacher} ===")
        for i, session in enumerate(CURRICULUM, 1):
            stage = session["stage"]
            threshold = STAGE_THRESHOLDS.get(stage, 6.0)
            with tqdm(total=1, desc=f"Session {i}: {stage}", leave=True, position=1) as session_bar:
                print(f"\n--- Session {i}: {stage} (Threshold: {threshold}) ---")
                use_wandb = os.environ.get("WANDB_DISABLED", "0") != "1"
                trainer = B2KnowledgeDistillationTrainer(
                    teacher_models=[teacher],
                    dataset_root="F:/datasets",
                    embedding_root="F:/b2_embeddings",
                    curriculum_params=session,
                    use_wandb=use_wandb,
                    wandb_project="impressioncore-b2",
                    log_file_path=log_file_path
                )
                results = trainer.execute_distillation_training(
                    num_epochs=30,  # Adjust as needed
                    max_examples=100,  # Adjust as needed
                    # session
                )
                session_bar.update(1)
                quality = results.get('final_quality', None)
                print(f"Session {i} complete. Quality: {quality}/10")
                # Adaptive progression: only continue if quality meets threshold
                if quality is None or quality < threshold:
                    print(f"[ADAPTIVE] Stage '{stage}' did not meet threshold ({quality} < {threshold}). Stopping curriculum for this teacher.")
                    break

if __name__ == "__main__":
    run_curriculum()
