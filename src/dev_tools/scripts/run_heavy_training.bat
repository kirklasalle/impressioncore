@echo off
echo Starting Heavy B3 Training (Phase 17)...
echo Target: 50 Epochs, 100,000 samples
echo Base Model: F:\models\checkpoints\diverse_curriculum_mhc_ultra\step_1000.pt

d:\Projects\impressioncore\.venv310\Scripts\python.exe -m src.training.conversational_finetune --epochs 50 --max-samples 100000

echo Training Complete.
pause
