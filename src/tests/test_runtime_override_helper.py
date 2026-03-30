import json

from src.training.utils.heel_logic import HeelConfigView, init_heel_state, update_heel_metrics
from src.training.utils.runtime_override_helper import atomic_write_json


def test_atomic_write_and_override(tmp_path):
    target = tmp_path / 'runtime_overrides.json'
    atomic_write_json(str(target), {"heel_eff_ratio": 0.5})
    data = json.loads(target.read_text())
    assert abs(data["heel_eff_ratio"] - 0.5) < 1e-9


def test_heel_metrics_progression():
    state = init_heel_state()
    cfg = HeelConfigView(
        heel_min_windows=1,
        heel_min_eff_floor=0.0,
        heel_eff_ratio=1.0,
        heel_curvature_tol=1e-6,
        heel_var_ratio_max=1.0,
        heel_peak_decay=1.0,
        heel_hold_consec=1,
    )
    # Simulate two windows with decreasing loss
    update_heel_metrics(state, cfg, pre_reset_raw_ce=10.0, supervised_tok=100)
    m2 = update_heel_metrics(state, cfg, pre_reset_raw_ce=9.0, supervised_tok=100)
    assert state['eff_peak'] >= state['eff_ema']
    assert m2['token_eff'] >= 0.0
