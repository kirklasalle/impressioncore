import importlib.util
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models.model_track_contracts import ModelTrackContracts


def _load_model_track_config_loader():
    config_path = PROJECT_ROOT / "src" / "core" / "config" / "model_track_config.py"
    spec = importlib.util.spec_from_file_location("model_track_config_module", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load model track config module from {config_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_model_track_config


load_model_track_config = _load_model_track_config_loader()


def main() -> int:
    config = load_model_track_config()
    contracts = ModelTrackContracts()
    report = contracts.validate_all(config)

    all_ok = all(section.get("ok", False) for section in report.values())
    payload = {
        "ok": all_ok,
        "report": report,
    }
    print(json.dumps(payload, indent=2))
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
