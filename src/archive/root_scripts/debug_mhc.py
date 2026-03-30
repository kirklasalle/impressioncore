import torch
from src.models.layers.mhc import SinkhornKnopp

def test_mhc():
    mhc = SinkhornKnopp(iterations=20, epsilon=1e-8)

    # Test cases
    cases = [
        ("Normal", torch.randn(2, 64, 64)),
        ("Large", torch.randn(2, 64, 64) * 1e5),
        ("Small/Zero", torch.zeros(2, 64, 64)),
        ("Very Small", torch.ones(2, 64, 64) * 1e-12),
        ("NaN", torch.tensor([[[float('nan')]] * 64] * 64).unsqueeze(0))
    ]

    for name, x in cases:
        try:
            out = mhc(x)
            print(f"Case: {name}, Out Max: {out.abs().max().item()}, HasNaN: {torch.isnan(out).any().item()}")
        except Exception as e:
            print(f"Case: {name}, Failed with error: {e}")

if __name__ == "__main__":
    test_mhc()
