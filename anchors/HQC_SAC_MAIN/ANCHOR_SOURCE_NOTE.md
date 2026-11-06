# Existing HQC-SAC main-method anchors

These three 400-EP checkpoints are reused as the Phase-I HQC-SAC main-method result; they are not retrained by the experiment launcher.

- Seeds: 7, 17, 27
- Each training CSV: 400 episodes, 160,000 environment steps, 78,001 optimizer updates.
- The model hashes match the archived checkpoint manifest used in the earlier frozen 30-scenario analysis.
- The original per-seed `run_config.json` files were not present in the available archive. The accompanying `run_config_reconstructed.json` files are explicitly reconstructed provenance records, not original logs.
- Seed 7 uses `07episodes.csv`, which matches the existing three-seed summary. A second file `07episodes(1).csv` was deliberately excluded because its last-five-episode reward/service statistics do not match the archived seed-7 summary.

Do not label reconstructed metadata as original training logs. Before final paper submission, recover the original per-seed config snapshots if they still exist on the training PC.
