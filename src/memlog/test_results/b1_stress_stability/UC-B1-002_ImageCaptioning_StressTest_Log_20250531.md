# Test Log: UC-B1-002 - Image Captioning (Basic) Stress & Stability Test

**Date:** 2025-05-31
**Tester:** GitHub Copilot (Simulated)
**Build Version:** ImpressionCore-b1 (Latest Stable)

## 1. Test Configuration

* **Hardware:** NVIDIA GTX 1050 Ti (4GB VRAM), Intel Core i5 4460, 32GB DDR3 RAM.
* **Dataset:** 750 diverse images (varying resolutions, sizes, content complexity, including challenging cases).
* **Background Load:** Simulated moderate GPU memory allocation (600MB) and 30% CPU load on 2 cores.
* **Test Durations:**
  * Short-term Stress: 2 hours (continuous high input rate of images)
  * Long-term Stability: 6 hours (sustained moderate rate with 3 x 15-min high-load bursts)

## 2. Metrics Monitored (Summary Table Template)

| Metric                                      | Baseline (No Load) | Short-Term Stress (Peak) | Short-Term Stress (Avg) | Long-Term (Avg) | Long-Term (Peak during Burst) | Notes                                         |
| :------------------------------------------ | :----------------- | :----------------------- | :---------------------- | :-------------- | :---------------------------- | :-------------------------------------------- |
| **VRAM Usage (MB)**                         |                    |                          |                         |                 |                               | Target < 4000MB                               |
|   - Total Used                              | ~950MB             | ~3900MB                  | ~3400MB                 | ~2800MB         | ~3950MB                       |                                               |
|   - Image Captioning Process                | ~750MB             | ~3100MB                  | ~2700MB                 | ~2100MB         | ~3200MB                       | Includes image encoders, decoders             |
| **GPU Utilization (%)**                     | 8%                 | 98%                      | 75%                     | 60%             | 99%                           | Intensive during image processing             |
| **System RAM Usage (MB) (ImpressionCore)**  | ~1800MB            | ~4500MB                  | ~3500MB                 | ~3000MB         | ~5000MB                       | Potential offloading of model parts/data      |
| **CPU Load (%) (Overall)**                  | ~12%               | ~65%                     | ~50%                    | ~35%            | ~75%                          | Preprocessing and some model parts can be CPU intensive |
| **Caption Latency (ms/image)**              | ~500ms             | ~2500ms                  | ~1500ms                 | ~800ms          | ~3000ms                       | Varies with image size & mitigation         |
| **Throughput (images/min)**                 | ~20                | ~4                       | ~8                      | ~12             | ~3                            |                                               |
| **Error Rate (%) (Captioning Failures)**    | 0%                 | <1.5%                    | <0.8%                   | <0.2%           | <2%                           | e.g., timeout, processing error for complex images |
| **Caption Quality (Subjective/BLEU-Sim.)**  | Good (BLEU ~0.35)  | Fair (BLEU ~0.25)        | Fair (BLEU ~0.28)       | Good (BLEU ~0.32) | Fair-Poor (BLEU ~0.20)      | Note any significant degradation/hallucination |

## 3. Adaptive Memory Management (`adaptive_memory_management`) Observations

| Timestamp (Test Phase) | VRAM Before (MB) | Trigger Condition Met (e.g., >85% VRAM) | Mitigation Action(s) Taken                                      | VRAM After (MB) | Latency Impact (ms) | Notes                                                                 |
| :--------------------- | :--------------- | :------------------------------------ | :-------------------------------------------------------------- | :-------------- | :------------------ | :-------------------------------------------------------------------- |
| ST-Stress @ 0h25m      | 3500             | Yes (87.5%)                           | Cleared GPU cache, Offloaded parts of image encoder to CPU      | 3000            | +400ms              | Caption quality maintained, noticeable latency increase             |
| ST-Stress @ 1h05m      | 3650             | Yes (91%)                             | Further offload, reduced batch size for internal processing     | 3100            | +600ms              | System stable, some very large images processed slower              |
| ST-Stress @ 1h40m      | 3800             | Yes (95%)                             | Aggressive offloading, dynamic image resizing (smaller input)   | 3200            | +800ms              | Caption quality slightly lower for resized, but system stable       |
| LT-Burst 1 @ 2h45m     | 3750             | Yes (93.75%)                          | All above + temporary switch to lower precision model (simulated) | 3150            | +1000ms             | Significant latency, noticeable quality dip, but no crash           |
| LT-Burst 2 @ 4h20m     | 3700             | Yes (92.5%)                           | Similar to Burst 1, but held off precision switch longer        | 3100            | +850ms              |                                                                       |
| LT-Burst 3 @ 5h35m     | 3900             | Yes (97.5%)                           | All mitigations active, including precision switch              | 3250            | +1200ms             | System remained stable, 2 complex images failed processing, recovered |

## 4. Key Events & Issues Log

* **[ST-Stress @ 1h45m]:** For a batch of very high-resolution images (e.g., >20MP), `adaptive_memory_management` triggered dynamic resizing to a smaller internal representation. Captions were generated but were less detailed for these specific images.
* **[LT-Stability @ 3h30m]:** During sustained moderate load, VRAM usage hovered around 2.7-2.9GB. `adaptive_memory_management` periodically cleared caches and managed smaller offloads, maintaining stability without significant performance impact.
* **[LT-Burst 3 @ 5h40m]:** Two extremely large/complex images failed to process during the peak burst with maximum mitigation active (timeout). The system logged the error and continued with the next images successfully.

## 5. Summary & Conclusion for UC-B1-002 (Image Captioning)

* **Stability:** The Image Captioning system showed good stability overall. It handled high loads and challenging inputs without crashing, even when mitigations were heavily active.
* **Performance:** Latency increased significantly under stress, especially when mitigations like model part offloading, dynamic resizing, or simulated precision reduction were active. Caption quality (simulated BLEU scores and subjective assessment) showed some degradation at peak stress, particularly when input images were internally resized or lower precision models were simulated.
* **`adaptive_memory_management` Effectiveness:** The `adaptive_memory_management` function was crucial in maintaining stability. It consistently triggered when VRAM limits were approached and applied a range of strategies. The system successfully stayed within the 4GB VRAM target. The more aggressive mitigations (resizing, precision change) had a clear trade-off with output quality/latency, which is an expected behavior.
* **Potential Issues/Areas for Improvement:**
  * Explore more graceful degradation strategies for caption quality when aggressive memory optimization is needed. Perhaps a tiered approach to resizing or feature stripping.
  * Log more detailed reasons for individual image processing failures during extreme load to differentiate between timeouts due to load vs. inherent image issues.

**Overall Assessment:** Pass (Simulated) - System stable, memory management effective, performance trade-offs noted.
