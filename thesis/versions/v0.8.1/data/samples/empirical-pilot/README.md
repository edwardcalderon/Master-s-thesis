# Open DEX pilot sample

This directory contains a six-minute excerpt of Ethereum mainnet Uniswap V2 WETH/USDT
swap events, 2026-11-26 04:00–04:06 UTC. The file contains three events. It preserves
the source timestamps, block/transaction ordering, reserves, effective swap prices,
pool fee tier, and source slippage estimates.

**Attribution:** Open Price / FairOnChain, DeepMining Lab, “Open Price ETH Data
Repository,” [dataset page](https://fair.deepmining.ch/ethereum) and
[source repository](https://github.com/DeepMining-Lab/Open_Price_Infra). The provider
publishes this dataset under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
These selected CSV rows are an excerpt; this project did not create or validate the
upstream measurements.

SHA-256 of `uniswap_v2_weth_usdt_swaps.csv`:

```text
31cf5ed4c2947a05c645a7ecacf4c6b2efc3fb38a12226e27f317ff228d3b789
```

The receipt status, gas used, and effective gas price were read from Ethereum mainnet
using JSON-RPC through [PublicNode](https://ethereum-rpc.publicnode.com/). The USDT gas
estimate multiplies whole-transaction gas by the same swap's effective price; it is a
proxy and is not allocated to the pool event.

Synchronized Kraken observations and CEX-derived values remain in private, Git-ignored
storage because no open redistribution license was identified for those data. See
[`experiments/empirical_data/README.md`](../../../experiments/empirical_data/README.md)
for the source treatment, pipeline, Azure plan, and limits.
