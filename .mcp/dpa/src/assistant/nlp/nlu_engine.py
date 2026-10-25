import sys
from pathlib import Path

# Add DPA root to sys.path
_dpa_dir = Path(__file__).resolve().parents[3]
if str(_dpa_dir) not in sys.path:
    sys.path.insert(0, str(_dpa_dir))

from nlp.nlu_engine import *
