from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from alfabetizacao_pipeline.finops import record_cloud_cost
from alfabetizacao_pipeline.paths import ProjectPaths


class FinOpsTest(unittest.TestCase):
    def test_records_an_observed_cloud_cost_with_auditable_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = ProjectPaths(Path(temporary))
            result = record_cloud_cost(
                paths,
                period="2026-08",
                amount_brl=0.0,
                source="Cloud Billing report",
                project_id="tech-challenge-fase-2-506814",
            )
            saved = json.loads((paths.evidence / "gcp_cost_observation.json").read_text(encoding="utf-8"))

        self.assertEqual("observed", result["status"])
        self.assertEqual(0.0, saved["amount_brl"])
        self.assertEqual("2026-08", saved["period"])
        self.assertIn("recorded_at", saved)

    def test_rejects_a_cost_without_a_valid_period(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                record_cloud_cost(
                    ProjectPaths(Path(temporary)),
                    period="08-2026",
                    amount_brl=0.0,
                    source="Cloud Billing report",
                    project_id="tech-challenge-fase-2-506814",
                )


if __name__ == "__main__":
    unittest.main()
