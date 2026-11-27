# Manuscript v0.8.4

Immutable bilingual source and evidence snapshot. This revision preserves the approved v0.8.3 research questions while updating the H2 interpretation with an exploratory 9,000-path replay of existing seeds.

The archived run distinguishes single panic-associated departures in shallow static E1 from recurrent departures in E3, adds a matched no-panic ablation, and evaluates a shallow-depth fixed-initial-reserve capacity control. The control substantially reduces the E3 post-recovery area contrast but does not identify a universal causal share: it covers one depth and conditions the outcome on recovery. The full factorial remains open.

The bilingual source, question control, figures and data, replay protocol, compressed inputs, runner dependencies, raw 9,000-path output and checksums are preserved here. All results remain conditional on the specified zero-fee simulator and are not market validation. The reduced two-state map does not outperform scalar AR(1); the band-aware replay is not a real-time forecast.

## Reproduce the replay

From this directory, run:

    python3 experiments/cex_dex_mvp/analyze_h2_revision.py \
      --output-root /tmp/v0.8.4-h2-replay \
      --export-dir /tmp/v0.8.4-h2-export \
      --web-export /tmp/v0.8.4-h2-export/web_findings.json

This reuses seeds 2000--2299. The default input is the compressed archived engineering-metrics fixture under experiments/cex_dex_mvp/fixtures/. The frozen protocol is experiments/cex_dex_mvp/H2_REVISION_PROTOCOL_0.7.0.md; the archived source run and its manifest are under experiments/cex_dex_mvp/archived-run/. Use a new or empty --output-root for each run. The run ID and CSV checksums should match the archived manifest.

The snapshot keeps v0.8.3 and earlier immutable.

[Spanish](README.es.md)
