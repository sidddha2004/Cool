# Evaluation

## Task and acceptance criteria (`src/coolguard/metrics.py`)
A scan is accepted when the detected page quad has **IoU ≥ 0.95** and **mean corner error ≤ 1% of the image diagonal**
(~8 px at 640×480) versus the ground truth quad produced by the known homography. NCC of the rectified output vs the true
flat page is reported but **not gated**: with *perfect* corners it is only 0.53-0.77 on blur/shadow images, so gating on it
would fail a perfect detector (found by an oracle check; see `test_oracle_always_accepted`).
Honest note on tolerances: they were fixed after inspecting the *clean-case* error distribution of v1 (IoU ≈ 0.98, error ≈
0.25%), before any candidate beyond v1 existed; they are task-motivated but not independently validated by user studies.
A constant "centred box" predictor passes only ~9-11% of cases (reviewer check), so the metric is not trivially satisfiable.

## Corpus (`synthetic.py`, generator v1.0)
10 categories × levels (clean, rotation, perspective, illumination gradient, shadow, blur, noise, low-res, JPEG, low contrast),
640×480, seeds recorded per case. Corpora: `dev` (seeds 0-3, 112), `heldout` (100-105, 168), `targeted-shadow` (300-303, 12),
`final` (200-205, 168).

## Data-use disclosure (important)
- Candidates v2-v7 were developed while looking at `dev`; v7 was additionally motivated by two `heldout` failures. Both are
  therefore *development/validation* sets, and `verify_candidate_fix` gates on them.
- `final` was not used to design any candidate. It is run once per loop execution (the loop was executed several times
  during hardening; no code changed in response to `final` results).
- All data come from one generator. 168/168 on `final` shows in-distribution generalisation across seeds only
  (n = 6 per category-level cell → ceiling effect); it is **not** evidence of robustness on real documents. v7's out-of-frame
  penalty would likely hurt pages cropped by the frame, which the generator never produces.
- Thresholds inside v6/v7 (`tau=12`, `pctl=20`, `probe=5`) are hand-tuned constants.

## Results (from `artifacts/last_loop_output.txt`)
v1: dev 99/112, heldout 147/168, final 151/168. v7: 112/112, 168/168, 168/168. Weakest v1 categories: shadow, low-contrast, illumination.

## Benchmark methodology
Local: `benchmark_vision_pipeline` (warm-up cycles over the images, N repeats, `perf_counter_ns`, raw latencies saved,
correctness computed in an *untimed* pass, peak memory via `ru_maxrss` on Linux / `peak_wset` on Windows - whole process,
not OpenCV-only; CPU% is process CPU time / wall). Comparison refuses attribution when workload, dataset, architecture or
detected corners (max delta > 0.5 px) differ. Local numbers are Windows x86-64 and **not** COOL/Graviton evidence.
Remote (`scripts/remote_bench.sh`, unexecuted): same instance, same Python minor version, CPUs pinned with `taskset`,
5 ABBA blocks, pip `opencv-python-headless==5.0.0.93` (generic aarch64) as baseline; build-info files saved for diffing.
Caveats: the workload is Python-heavy, so library-level differences are diluted - also benchmark isolated ops
(resize/blur/Canny/threshold/findContours) before making any per-operation claim; do not extrapolate vendor aggregate speedups.
