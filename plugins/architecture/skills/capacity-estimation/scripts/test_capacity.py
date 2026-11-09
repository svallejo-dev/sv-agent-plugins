#!/usr/bin/env python3
"""Golden cases for the calculator: values computed by hand, independent of the code."""
import contextlib
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capacity as c  # noqa: E402


class TestCapacity(unittest.TestCase):
    def test_little(self):
        r = c.little(rps=1000, latency_ms=200, utilization=0.8)
        self.assertAlmostEqual(r["mean_concurrency"], 200)
        self.assertEqual(r["recommended_pool"], 250)

    def test_utilization_mm1(self):
        r = c.utilization(service_ms=10, rho=0.8, rps=0)
        self.assertAlmostEqual(r["response_ms_at_rho"], 50)
        self.assertAlmostEqual(r["response_ms_by_rho"]["0.90"], 100)

    def test_servers_for_rho(self):
        r = c.utilization(service_ms=20, rho=0.5, rps=1000)
        self.assertEqual(r["servers_for_rho"], 40)

    def test_fanout_tail_at_scale(self):
        r = c.fanout(n=100, p=0.01)
        self.assertAlmostEqual(r["prob_slow_response"], 0.634, places=3)

    def test_availability(self):
        r = c.availability(series=[0.999, 0.999], parallel=[])
        self.assertAlmostEqual(r["availability"], 0.998001)
        r = c.availability(series=[], parallel=["0.99:2"])
        self.assertAlmostEqual(r["availability"], 0.9999)

    def test_shards(self):
        r = c.shards(peak_qps=120_000, node_qps=10_000, total_bytes=0, node_bytes=0, utilization=0.7)
        self.assertEqual(r["shards"], 18)
        r = c.shards(peak_qps=1_000, node_qps=10_000, total_bytes=10e12, node_bytes=1e12, utilization=0.5)
        self.assertEqual(r["shards"], 20)
        self.assertEqual(r["limiting"], "size")

    def test_backlog(self):
        r = c.backlog(messages=3_600_000, production_s=1_000, consumption_s=2_000)
        self.assertAlmostEqual(r["drain_time_h"], 1.0)
        r = c.backlog(messages=10, production_s=5, consumption_s=5)
        self.assertIsNone(r["drain_time_s"])

    def test_burn(self):
        r = c.burn(slo=0.999, window_days=30, burn_rate=14.4)
        self.assertAlmostEqual(r["days_to_exhaustion"], 2.0833, places=3)
        self.assertAlmostEqual(r["error_budget_min"], 43.2, places=1)

    def test_measured(self):
        r = c.measured(current_peak_rps=1_000, annual_growth=4, horizon_months=6,
                       target_utilization=0.5, rps_per_instance=500)
        self.assertAlmostEqual(r["projected_peak_rps"], 2_000)
        self.assertEqual(r["instances_needed"], 8)

    def test_demand(self):
        r = c.demand(dau=86_400_000, writes_per_user_day=1, reads_per_write=10, peak=2,
                     object_bytes=1_000, retention_days=10, replicas=3, response_bytes=1_000)
        self.assertAlmostEqual(r["write_qps_avg"], 1_000)
        self.assertAlmostEqual(r["read_qps_peak"], 20_000)
        self.assertAlmostEqual(r["storage_total_bytes"], 86_400_000 * 1_000 * 10 * 3)


class TestExploratory(unittest.TestCase):
    def test_scenarios(self):
        r = c.scenarios(dau=[86_400, 8_640_000], writes_per_user_day=1, reads_per_write=10,
                        peak=2, object_bytes=1_000, retention_days=1, replicas=1, response_bytes=1_000)
        rows = r["scenarios"]
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["write_qps_peak"], 2)
        self.assertAlmostEqual(rows[1]["read_qps_peak"], 2_000)

    def test_threshold(self):
        # 1,000 writes/s at 50 % utilization, 10 actions per user per day, 2x peak
        r = c.threshold(qps_limit=1_000, actions_per_user_day=10, peak=2, utilization=0.5)
        self.assertAlmostEqual(r["dau_threshold"], 2_160_000)


class TestCli(unittest.TestCase):
    def test_every_subcommand_runs_from_the_cli(self):
        calls = [
            ["demand", "--dau", "1e6", "--writes-per-user-day", "2"],
            ["scenarios", "--dau", "1e4", "1e6", "--writes-per-user-day", "2"],
            ["threshold", "--qps-limit", "1000", "--actions-per-user-day", "10"],
            ["measured", "--current-peak-rps", "1000", "--annual-growth", "2", "--rps-per-instance", "200"],
            ["little", "--rps", "1200", "--latency-ms", "180"],
            ["utilization", "--service-ms", "10", "--rps", "100"],
            ["fanout", "--n", "100"],
            ["availability", "--series", "0.999", "--parallel", "0.99:3"],
            ["shards", "--peak-qps", "1000", "--node-qps", "100"],
            ["backlog", "--messages", "100", "--production-s", "1", "--consumption-s", "2"],
            ["burn", "--slo", "0.999", "--burn-rate", "14.4"],
        ]
        for argv in calls:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                c.main(argv)
            self.assertEqual(json.loads(out.getvalue())["calculation"], argv[0])


if __name__ == "__main__":
    unittest.main()
