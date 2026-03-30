import sys

sys.path.insert(0, 'd:/Projects/impressioncore/src')
try:
    from training.rope.smoke_rope_demo import run_demo
    run_demo()
    print('OK')
except Exception:
    import traceback
    traceback.print_exc()
