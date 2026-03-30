import sys, os
sys.path.insert(0, os.getcwd())
from src.training.scripts.train_unified_sweet_spot import main
sys.argv = ['train_unified_sweet_spot.py','--resume','F:/models/checkpoints/b3_ollama_enhanced/b3_ollama_enhanced_final_step_1500.pth','--steps','90000']
main()
