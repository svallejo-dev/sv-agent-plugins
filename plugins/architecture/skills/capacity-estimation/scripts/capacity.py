#!/usr/bin/env python3
"""Capacity calculator for system design (stdlib only).

Each subcommand is an explicit formula; the output is JSON with the inputs,
the results and the formula used, so the reasoning can be audited.

Subcommands:
  demand        Projected demand from users (new system).
  measured      Projection from measured traffic (existing system).
  scenarios     Demand for several orders of magnitude (no metrics).
  threshold     Scale beyond which a decision stops working.
  little        Little's law: concurrency and pool size.
  utilization   Response time vs utilization (M/M/1 approximation).
  fanout        Probability of hitting the latency tail with fan-out.
  availability  Availability composition in series and in parallel.
  shards        Number of shards/nodes by throughput and by size.
  backlog       Drain time of a backed-up queue.
  burn          Error budget consumption at a given burn rate.

Example:
  python3 capacity.py little --rps 1200 --latency-ms 180 --utilization 0.7
"""
import argparse
import json
import math
import sys

SEC_DAY = 86_400
MIN_MONTH = 30 * 24 * 60


def human(n, unit=""):
    for div, suf in ((1e15, "P"), (1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return f"{n / div:.2f}{suf}{unit}"
    return f"{n:.2f}{unit}"


def demand(dau, writes_per_user_day, reads_per_write, peak, object_bytes,
           retention_days, replicas, response_bytes):
    w_avg = dau * writes_per_user_day / SEC_DAY
    r_avg = w_avg * reads_per_write
    bytes_day = dau * writes_per_user_day * object_bytes
    total = bytes_day * retention_days * replicas
    return {
        "formula": "qps = dau * actions / 86400; peak = qps * factor; storage = writes/day * bytes * retention * replicas",
        "write_qps_avg": w_avg,
        "write_qps_peak": w_avg * peak,
        "read_qps_avg": r_avg,
        "read_qps_peak": r_avg * peak,
        "storage_per_day_bytes": bytes_day,
        "storage_total_bytes": total,
        "storage_total": human(total, "B"),
        "ingress_peak_bytes_s": w_avg * peak * object_bytes,
        "egress_peak_bytes_s": r_avg * peak * response_bytes,
    }


def scenarios(dau, writes_per_user_day, reads_per_write, peak, object_bytes,
              retention_days, replicas, response_bytes):
    rows = []
    for d in dau:
        r = demand(d, writes_per_user_day, reads_per_write, peak, object_bytes,
                   retention_days, replicas, response_bytes)
        rows.append({
            "dau": d,
            "write_qps_peak": r["write_qps_peak"],
            "read_qps_peak": r["read_qps_peak"],
            "storage_total": r["storage_total"],
            "egress_peak": human(r["egress_peak_bytes_s"], "B/s"),
        })
    return {
        "formula": "demand() evaluated for each scenario; per-user factors are archetype assumptions",
        "scenarios": rows,
        "note": "Design for the likely scenario at 12-18 months and check what breaks at the next one.",
    }


def threshold(qps_limit, actions_per_user_day, peak, utilization):
    dau = qps_limit * utilization * SEC_DAY / (actions_per_user_day * peak)
    return {
        "formula": "dau_threshold = qps_limit * utilization * 86400 / (actions_per_user_day * peak)",
        "dau_threshold": dau,
        "dau_threshold_readable": human(dau),
        "note": "Beyond this scale the decision (a single node, a single partition, etc.) stops working; use it in the 'change it when…' column.",
    }


def measured(current_peak_rps, annual_growth, horizon_months, target_utilization,
             rps_per_instance):
    factor = annual_growth ** (horizon_months / 12)
    projected = current_peak_rps * factor
    out = {
        "formula": "projected = current_peak_rps * annual_growth^(months/12)",
        "growth_factor": factor,
        "projected_peak_rps": projected,
    }
    if rps_per_instance:
        out["instances_needed"] = math.ceil(projected / (rps_per_instance * target_utilization))
        out["instances_formula"] = "ceil(projected / (rps_per_instance * target_utilization))"
    return out


def little(rps, latency_ms, utilization):
    concurrency = rps * latency_ms / 1000
    return {
        "formula": "L = lambda * W; pool = ceil(L / utilization)",
        "mean_concurrency": concurrency,
        "recommended_pool": math.ceil(concurrency / utilization),
        "note": "Use the latency at the percentile you want to absorb without queuing (p99 for connection pools to dependencies).",
    }


def utilization(service_ms, rho, rps):
    if not 0 <= rho < 1:
        raise ValueError("rho must be in [0, 1)")
    table = {f"{u:.2f}": service_ms / (1 - u) for u in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)}
    out = {
        "formula": "R = S / (1 - rho)  (M/M/1: Poisson arrivals, one server; indicative)",
        "response_ms_at_rho": service_ms / (1 - rho),
        "response_ms_by_rho": table,
    }
    if rps:
        out["servers_for_rho"] = math.ceil(rps * service_ms / 1000 / rho)
        out["servers_formula"] = "ceil(lambda * S / rho)"
    return out


def fanout(n, p):
    return {
        "formula": "P(at least one slow) = 1 - (1 - p)^n",
        "prob_slow_response": 1 - (1 - p) ** n,
        "note": "p = probability that a backend responds above its percentile (0.01 for p99).",
    }


def availability(series, parallel):
    total = 1.0
    detail = []
    for a in series:
        total *= a
        detail.append({"series": a})
    for item in parallel:
        a, k = item.split(":")
        a, k = float(a), int(k)
        comp = 1 - (1 - a) ** k
        total *= comp
        detail.append({"parallel": a, "replicas": k, "composed": comp})
    return {
        "formula": "series: product; independent parallel: 1 - (1 - a)^k",
        "availability": total,
        "downtime_min_month": (1 - total) * MIN_MONTH,
        "detail": detail,
        "note": "Parallel assumes independent failures; correlated failures (same zone, same deploy, same config) break that assumption.",
    }


def shards(peak_qps, node_qps, total_bytes, node_bytes, utilization):
    by_qps = math.ceil(peak_qps / (node_qps * utilization)) if node_qps else 0
    by_bytes = math.ceil(total_bytes / (node_bytes * utilization)) if node_bytes else 0
    return {
        "formula": "max(ceil(qps / (node_qps * u)), ceil(bytes / (node_bytes * u)))",
        "by_throughput": by_qps,
        "by_size": by_bytes,
        "shards": max(by_qps, by_bytes),
        "limiting": "throughput" if by_qps >= by_bytes else "size",
        "note": "If the distribution is skewed, compute on the hottest key/partition, not on the average.",
    }


def backlog(messages, production_s, consumption_s):
    net = consumption_s - production_s
    out = {"formula": "t = backlog / (consumption - production)", "net_drain_s": net}
    if net <= 0:
        out["drain_time_s"] = None
        out["note"] = "The backlog never drains: consumption does not exceed production."
    else:
        t = messages / net
        out["drain_time_s"] = t
        out["drain_time_h"] = t / 3600
    return out


def burn(slo, window_days, burn_rate):
    budget_min = (1 - slo) * window_days * 24 * 60
    return {
        "formula": "time to exhaustion = window / burn_rate",
        "error_budget_min": budget_min,
        "days_to_exhaustion": window_days / burn_rate,
        "hours_to_exhaustion": window_days * 24 / burn_rate,
    }


def _demand_args(parser, multiple_dau=False):
    if multiple_dau:
        parser.add_argument("--dau", type=float, nargs="+", required=True, help="e.g. 1e4 1e6 1e8")
    else:
        parser.add_argument("--dau", type=float, required=True)
    parser.add_argument("--writes-per-user-day", type=float, required=True)
    parser.add_argument("--reads-per-write", type=float, default=10.0)
    parser.add_argument("--peak", type=float, default=2.0)
    parser.add_argument("--object-bytes", type=float, default=1e3)
    parser.add_argument("--retention-days", type=float, default=365)
    parser.add_argument("--replicas", type=float, default=3)
    parser.add_argument("--response-bytes", type=float, default=1e3)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    _demand_args(sp.add_parser("demand"))
    _demand_args(sp.add_parser("scenarios"), multiple_dau=True)

    th = sp.add_parser("threshold")
    th.add_argument("--qps-limit", type=float, required=True, help="capacity of the option under evaluation")
    th.add_argument("--actions-per-user-day", type=float, required=True)
    th.add_argument("--peak", type=float, default=2.0)
    th.add_argument("--utilization", type=float, default=0.7)

    m = sp.add_parser("measured")
    m.add_argument("--current-peak-rps", type=float, required=True)
    m.add_argument("--annual-growth", type=float, default=1.0, help="factor, e.g. 2 = doubles every year")
    m.add_argument("--horizon-months", type=float, default=12)
    m.add_argument("--target-utilization", type=float, default=0.6)
    m.add_argument("--rps-per-instance", type=float, default=0)

    lt = sp.add_parser("little")
    lt.add_argument("--rps", type=float, required=True)
    lt.add_argument("--latency-ms", type=float, required=True)
    lt.add_argument("--utilization", type=float, default=0.7)

    u = sp.add_parser("utilization")
    u.add_argument("--service-ms", type=float, required=True)
    u.add_argument("--rho", type=float, default=0.7)
    u.add_argument("--rps", type=float, default=0)

    f = sp.add_parser("fanout")
    f.add_argument("--n", type=int, required=True)
    f.add_argument("--p", type=float, default=0.01)

    a = sp.add_parser("availability")
    a.add_argument("--series", type=float, nargs="*", default=[])
    a.add_argument("--parallel", nargs="*", default=[], help="availability:replicas, e.g. 0.99:3")

    s = sp.add_parser("shards")
    s.add_argument("--peak-qps", type=float, required=True)
    s.add_argument("--node-qps", type=float, required=True)
    s.add_argument("--total-bytes", type=float, default=0)
    s.add_argument("--node-bytes", type=float, default=0)
    s.add_argument("--utilization", type=float, default=0.7)

    b = sp.add_parser("backlog")
    b.add_argument("--messages", type=float, required=True)
    b.add_argument("--production-s", type=float, required=True)
    b.add_argument("--consumption-s", type=float, required=True)

    br = sp.add_parser("burn")
    br.add_argument("--slo", type=float, required=True)
    br.add_argument("--window-days", type=float, default=30)
    br.add_argument("--burn-rate", type=float, required=True)

    x = p.parse_args(argv)
    args = {k: v for k, v in vars(x).items() if k != "cmd"}
    fn = {
        "demand": demand, "scenarios": scenarios, "threshold": threshold, "measured": measured,
        "little": little, "utilization": utilization, "fanout": fanout, "availability": availability,
        "shards": shards, "backlog": backlog, "burn": burn,
    }[x.cmd]
    out = {"calculation": x.cmd, "inputs": args, "result": fn(**args)}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
