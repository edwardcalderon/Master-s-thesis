# Data boundary

Private source inputs are written under `data/raw/`; generated alignments go in `data/processed/`. Both directories are ignored by Git. Do not commit credentials, restricted CEX data, or large generated files.

The repository includes one small, openly licensed DEX event excerpt in [`samples/empirical-pilot/`](samples/empirical-pilot/), attributed under CC BY 4.0. It is not publicly paired with Kraken observations because no open redistribution license was identified for those CEX data. The ingestor, provenance, alignment rules, limits, and optional Azure storage are documented in [`experiments/empirical_data/README.md`](../experiments/empirical_data/README.md).

---

[Español](README.es.md)
