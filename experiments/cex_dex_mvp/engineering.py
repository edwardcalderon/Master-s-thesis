"""Supplementary engineering sensitivity with fresh seeds; see ENGINEERING_PROTOCOL.md."""
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import platform
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from abm import make_noise_schedule, run_condition, validate
from confirm import scaled_config, write_csv
from run import git_context, sha256_bytes

HERE = Path(__file__).resolve().parent


def tracking_metrics(rows, band, deadlines, tolerance=1e-12):
    """Observe a two-tick return only when its second tick has occurred."""
    observations = [(int(r['tick']), abs(float(r['log_error'])) <= band + tolerance)
                    for r in rows if int(r['tick']) >= 1]
    confirmation = next((tick for (previous, ok0), (tick, ok1)
                         in zip(observations, observations[1:])
                         if tick == previous + 1 and ok0 and ok1), None)
    recovered = confirmation is not None
    departed = recovered and any(t > confirmation and not ok for t, ok in observations)
    return {
        'recovered': int(recovered),
        'confirmation_tick': confirmation if recovered else '',
        'later_departure': int(departed),
        'terminal_in_band': int(observations[-1][1]),
        'outside_fraction': statistics.mean(not ok for _, ok in observations),
        **{f'recovered_by_{d}': int(recovered and confirmation <= d) for d in deadlines},
    }


def wilson(successes, n):
    p = successes / n
    z = 1.959963984540054
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n)) / denominator
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denominator
    return max(0.0, center-half), min(1.0, center+half)


def variant_config(model, depth, variant):
    if variant not in ('fixed_orders', 'proportional_orders', 'no_panic'):
        raise ValueError(f'Unknown variant: {variant}')
    config = scaled_config(model, depth)
    if variant == 'proportional_orders':
        config['noise_trader'] = copy.deepcopy(model['noise_trader'])
        config['trend_panic_trader'] = copy.deepcopy(model['trend_panic_trader'])
    if variant == 'no_panic':
        config['trend_panic_trader']['panic_max_orders_per_run'] = 0
    validate(config)
    return config


def summarize(group, deadlines):
    n = len(group)
    recovered = sum(r['recovered'] for r in group)
    departures = sum(r['later_departure'] for r in group)
    return {
        'runs': n,
        **{f'recovery_by_{d}': statistics.mean(r[f'recovered_by_{d}'] for r in group) for d in deadlines},
        'terminal_in_band_rate': statistics.mean(r['terminal_in_band'] for r in group),
        'later_departure_rate': departures/n,
        'later_departure_given_recovery': departures/recovered if recovered else '',
        'mean_outside_fraction': statistics.mean(r['outside_fraction'] for r in group),
        'mean_excess_area': statistics.mean(r['excess_area'] for r in group),
        'mean_max_response': statistics.mean(r['max_response'] for r in group),
    }


def execute(output_root):
    names = ('engineering_config.json', 'abm_config.json', 'confirm_config.json')
    inputs = {n: (HERE/n).read_bytes() for n in names}
    cfg, model, confirmation = [json.loads(inputs[n]) for n in names]
    seeds = range(cfg['seed_start'], cfg['seed_start'] + cfg['seed_count'])
    if cfg['seed_count'] < 2 or model['horizon_ticks'] != 20 or model['sustained_band_ticks'] != 2:
        raise ValueError('Protocol requires >=2 seeds, 20 ticks and two-tick recovery')
    for stage in ('exploration', 'confirmation'):
        old = confirmation[stage]
        if set(seeds) & set(range(old['seed_start'], old['seed_start']+old['seed_count'])):
            raise ValueError('Engineering seeds overlap frozen protocol')
    deadlines = cfg['deadlines_ticks']
    if any(d < 2 or d > model['horizon_ticks'] for d in deadlines):
        raise ValueError('Recovery deadlines must be within the observable horizon')
    sources = {n: (HERE/n).read_bytes() for n in
               ('engineering.py', 'abm.py', 'confirm.py', 'run.py', 'ENGINEERING_PROTOCOL.md')}
    run_id = 'cex-dex-engineering-' + sha256_bytes(b''.join(inputs.values()) + b''.join(sources.values()))[:12]
    run_dir = output_root/run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    records = []
    for variant in cfg['variants']:
        for depth in cfg['depth_scales']:
            config = variant_config(model, depth, variant)
            for shock in cfg['shock_log_returns']:
                for seed in seeds:
                    schedule = make_noise_schedule(config, seed)
                    for condition, spec in confirmation['conditions'].items():
                        rows, summary = run_condition(config, shock, seed, condition,
                                                      spec['capacity'], spec['adaptive_lp'], schedule)
                        metrics = tracking_metrics(rows, config['no_arbitrage_band_log'], deadlines,
                                                   cfg['band_tolerance'])
                        base_price = rows[0]['dex_price']
                        records.append({'variant': variant, 'depth_scale': depth,
                                        'shock_log_return': shock, 'seed': seed, 'condition': condition,
                                        **metrics,
                                        'excess_area': sum(abs(r['excess_error']) for r in rows[1:]),
                                        'max_response': max(abs(math.log(r['dex_price']/base_price)) for r in rows[1:]),
                                        'capital_limited_orders': summary['capital_limited_orders']})
    cell_groups, condition_groups = defaultdict(list), defaultdict(list)
    index = {}
    for row in records:
        cell_groups[(row['variant'], row['condition'], row['depth_scale'], row['shock_log_return'])].append(row)
        condition_groups[(row['variant'], row['condition'])].append(row)
        index[(row['variant'], row['condition'], row['depth_scale'], row['shock_log_return'], row['seed'])] = row
    cells = []
    for (variant, condition, depth, shock), group in cell_groups.items():
        row = dict(variant=variant, condition=condition, depth_scale=depth, shock_log_return=shock,
                   **summarize(group, deadlines))
        for d in deadlines:
            low, high = wilson(sum(r[f'recovered_by_{d}'] for r in group), len(group))
            row[f'recovery_by_{d}_ci95_low'], row[f'recovery_by_{d}_ci95_high'] = low, high
        cells.append(row)
    conditions = [dict(variant=v, condition=c, **summarize(g, deadlines))
                  for (v, c), g in condition_groups.items()]
    effects = []
    for variant in cfg['variants']:
        for depth in cfg['depth_scales']:
            differences = [statistics.mean(
                index[(variant, 'E3-adaptive-lp-high-arb', depth, shock, seed)]['max_response'] -
                index[(variant, 'E1-arb-high-static', depth, shock, seed)]['max_response']
                for shock in cfg['shock_log_returns']) for seed in seeds]
            mean = statistics.mean(differences)
            half = 1.96*statistics.stdev(differences)/math.sqrt(len(differences))
            effects.append(dict(variant=variant, depth_scale=depth, seed_count=len(differences),
                                mean_paired_max_response=mean, ci95_low=mean-half, ci95_high=mean+half))
    for name, rows in [('run_metrics.csv', records), ('cell_summary.csv', cells),
                       ('condition_summary.csv', conditions), ('depth_effects.csv', effects)]:
        write_csv(run_dir/name, rows)
    for name, data in inputs.items():
        (run_dir/name).write_bytes(data)
    artifacts = sorted(p.name for p in run_dir.iterdir())
    metadata = dict(run_id=run_id, analysis_version=cfg['analysis_version'], model_version=model['model_version'],
                    run_count=len(records), seed_range=[min(seeds),max(seeds)], independent_unit='seed',
                    generated_at_utc=datetime.now(timezone.utc).isoformat(), python_version=platform.python_version(),
                    source_sha256={n:sha256_bytes(b) for n,b in sources.items()},
                    artifact_sha256={n:sha256_bytes((run_dir/n).read_bytes()) for n in artifacts},
                    **git_context())
    (run_dir/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return run_dir


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'output/engineering')
    args = parser.parse_args()
    print(execute(args.output.resolve()))
