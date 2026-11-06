# Final audited package status

Source package follows the screenshot's Phase I/II/III/IV experimental matrix, **not** the obsolete five-lambda-training queue.

## Verified in this container

- 34 tests passed with an isolated minimal gymnasium interface shim (no GPU or real gymnasium installed in the container).
- Three uploaded HQC-SAC 400-EP checkpoint hashes and model loads passed.
- Four RL algorithms each executed a full 400-slot single-episode CPU smoke run.
- CDA-SAC-Adapted completed an 11-EP CPU optimizer smoke, including 201 gradient updates.
- PI-BCD-SCA completed a 2-slot solver preview/runtime smoke, not a 30- or 100-scene experiment.
- Real checkpoint fixed-500 evaluation: 3 models x 1 scene x 400 slots; 4,800 relay-slot records; re-running correctly skips complete outputs.
- CDA vs HQC online trainable parameter counts: 365,245 vs 365,451 (difference ~0.0564%).
- The original historical HQC-SAC training CSV has no P95 per-episode field; plotting now emits a missing-data manifest and never fabricates the curve.
- Existing evaluation outputs now require expected seeds and 400-step relay/trajectory row counts before being marked complete.
- Note: local Windows uav_old + CUDA three-process preflight is still required; current container CPU tests do not establish actual GPU compatibility or speed.

## Caveats

- The embedded historic HQC-SAC main checkpoint trio is (reward lambda 0.10, scheduler lambda 0.10), with reconstructed configuration metadata. If an independently retrained LS020 main is finally selected, do not compare a different-scheduler RL baseline as if all scheduler settings match.
- The PI-BCD-SCA method is a causal project adaptation and is subject to the 0.5-s runtime gate.
- 100 final test seeds 10000-10099 must remain unused until all methods/configurations are frozen.


## RTX 4060 Ti 8-GB gate correction

The former 16-GB/12-GB threshold was a conservative hardware assumption, not a measured per-process requirement, and it blocked the user's 8-GB card before testing. The corrected package allows entry at >=7.5 GB total and >=6.0 GB free, then requires the actual concurrent three-process 11-EP GPU smoke to pass. This patch does not claim that the local GPU has passed; the user must run preflight. If the concurrent smoke OOMs, no 400-EP jobs are authorized. No model hyperparameters were changed.
