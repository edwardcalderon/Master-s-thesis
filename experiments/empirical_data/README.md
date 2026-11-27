# Empirical CEX/DEX data path

This bounded ingestion and synchronization prototype belongs to the separate
empirical-validation task [`DATA-001`](../../.agents/tasks/in-progress/DATA-001/TASK.md).
It does not replace or recalibrate the synthetic thesis experiments.

**Progress (2026-11-26):** a bounded real-data capture and minute alignment prototype
are implemented; the local pilot produced a small, openly licensed DEX excerpt. Full
empirical acceptance remains open: CEX redistribution rights are unresolved, Azure
storage is not provisioned in this shell, and cost/latency/capital scenario inputs
remain uncalibrated.

## Pair and source rights

- **CEX:** Kraken Spot `ETH/USDT`, using the public Post-Trade endpoint. It supplies
  trade time, publication time, execution price, quantity, side, and trade ID. The
  endpoint is public, but no open redistribution license for its data was identified.
  Kraken terms govern its use. CEX rows and CEX-derived values are written only to
  Git-ignored local storage and, when enabled, a private Azure container. Do not commit
  or publicly publish them without written permission or a reviewed rights basis.
- **DEX:** Ethereum mainnet Uniswap V2 WETH/USDT pool
  `0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852`. Open Price / FairOnChain (DeepMining
  Lab) publishes swaps, block ordering, reserves, pool fee tier, effective trade price,
  volume, and trade-size-specific slippage measures. The dataset is licensed CC BY 4.0.
  Attribute DeepMining Lab and link to the dataset page and repository when reusing it.

At capture time (2026-11-26), the upstream DEX CSV was **9,067,109,904 bytes**. The
ingestor seeks by timestamp with HTTP byte ranges and retrieves only the requested
event window. It refuses a source that does not honor range requests and applies a
download cap. The upstream multi-gigabyte file is not copied into Git or Azure.

## Reproduce a bounded capture

Python 3.11+ standard library only; acquisition uses no user API keys.

```sh
python3 experiments/empirical_data/ingest.py \
  --start 2026-11-26T04:00:00Z \
  --end 2026-11-26T04:06:00Z \
  --raw-output data/raw/empirical-private \
  --processed-output data/processed/empirical-private \
  --max-source-mib 32
```

The checked-in [DEX-only pilot sample](../../data/samples/empirical-pilot/) contains
three swaps from this six-minute window. CEX rows, their derived minute aggregates,
and run manifests are written to Git-ignored local paths. The actual local pilot
produced a six-minute UTC alignment grid; it is for pipeline inspection only.

The join aggregates CEX executions and DEX block-time events separately into UTC
minutes. It sorts CEX executions by exchange trade timestamp and DEX events by block,
transaction, and log order. Missing DEX observations remain missing; the join does not
carry values forward. CEX bars come from observed trades. DEX effective swap price and
reserve-implied price remain distinct because executed prices include trade impact.
The DEX 0.30% pool fee and source slippage estimates are retained separately from
account-specific CEX fees. For minutes with observations from both venues, the output
records the CEX and DEX event timestamps and their signed time gap; same-minute prices
are not treated as simultaneous observations.

To retrieve Ethereum transaction receipts, set `ETHEREUM_RPC_URL` to a mainnet JSON-RPC
endpoint and add `--enrich-gas`. The ingestor records receipt gas used and effective
gas price. Its USDT conversion multiplies whole-transaction gas by that swap's
effective price. This is a labelled proxy, not a cost allocated to an individual pool
event when a transaction contains multiple swaps.

## Private Azure archival

`infra/azure/bicep/main.bicep` can optionally create a private Standard LRS StorageV2
account and Blob container. Storage creation defaults off: Blob Storage is not the
project's permanent free runtime tier, and a broad historical collection can incur
storage and retrieval charges. Ingest predeclared, rights-reviewed windows rather than
copying the full upstream file.

After reviewing the expected Azure cost and source terms, provision the optional
resources:

```sh
az login
az deployment group create \
  --resource-group rg-microworld \
  --template-file infra/azure/bicep/main.bicep \
  --parameters createHistoricalDataStorage=true
```

Grant the operator `Storage Blob Data Contributor` on the account. Then upload a
bounded private capture through Azure CLI OAuth/RBAC:

```sh
export AZURE_STORAGE_ACCOUNT='<historicalDataStorageAccountName deployment output>'
python3 experiments/empirical_data/ingest.py \
  --start 2026-11-26T04:00:00Z --end 2026-11-26T04:06:00Z \
  --upload --azure-prefix microworld
```

The container is private, shared-key access is disabled, HTTPS/TLS is required, and
the lifecycle rule moves run objects to Cool after 90 days. In this shell, `az` has
no signed-in account; the storage resource has **not** been deployed and no data has
been uploaded to Azure.

## Interpretation limits

This six-minute pilot validates acquisition and alignment only. It is not a finding,
calibration, or confirmation of H1-H3. CEX publication-minus-trade time is exchange
dissemination lag, not the agent's network, decision, or order-execution latency. The
public CEX feed does not provide the researcher's account fee tier, historical order
book depth, agent capital, or inventory. DEX slippage estimates are tied to specified
trade sizes, not realized costs for the thesis agent. Transaction gas remains absent
unless receipt enrichment is enabled; the resulting USDT value uses a same-swap price
proxy and should be replaced with a documented contemporaneous ETH/USDT price source
for substantive analysis.

[`execution_assumptions.example.json`](execution_assumptions.example.json) deliberately
leaves these scenario inputs null. Before substantive analysis, predeclare the target,
event-time rule, sample/holdout windows, and scenario values with their provenance.
Keep real-market observations separate from the existing synthetic evidence.

## Primary references

- [Kraken Post-Trade API](https://docs.kraken.com/api/docs/rest-api/get-post-trade)
- [Kraken public market-data endpoint guidance](https://support.kraken.com/in/articles/360000919986-public-endpoint-examples-you-can-try-them-directly-in-a-web-browser-)
- [Open Price ETH dataset and schema](https://github.com/DeepMining-Lab/Open_Price_Infra/blob/main/eth/README.md)
- [Open Price Ethereum data page](https://fair.deepmining.ch/ethereum)
- [Open Price access procedure and license](https://github.com/DeepMining-Lab/Open_Price_Infra)
- [Ethereum JSON-RPC receipt fields](https://ethereum.org/developers/docs/apis/json-rpc/)
- [PublicNode Ethereum mainnet endpoint](https://ethereum-rpc.publicnode.com/)
- [Azure Blob lifecycle management](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)
