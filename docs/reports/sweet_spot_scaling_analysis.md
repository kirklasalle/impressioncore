# Sweet Spot Scaling Analysis

**Created:** August 10, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\reports\sweet_spot_scaling_analysis.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Generated automatically.

## Data Points

- N=101500000.0 params; loss=0.001187; VRAM=3400 MB; source=B3_SCALING_SWEET_SPOT_THEORY.md; note=Phase 1 success at ~101.5M params
- N=506000000.0 params; loss=NA; VRAM=NA MB; source=sweet_spot_recovery_training.log; note=Recovery run; parse log for best loss if available
- N=506045321.0 params; loss=0.999928; VRAM=5979.0 MB; source=log:sweet_spot_recovery_training.log

## Local scaling indicator

log(loss) vs log(N) slope: 4.193 (anomalous: loss increases with parameters; likely data/compute mismatch)

## Guidance

- Co-scale data tokens with parameter increases to stay compute-optimal.
- Measure tokens seen and wall-clock to compare fairly across N.
- Prefer active-parameter accounting for MoE when judging compute.
- Use early-stop based on improvement-per-hour to avoid wasted runs.