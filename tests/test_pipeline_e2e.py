from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from alfabetizacao_pipeline.paths import ProjectPaths
from alfabetizacao_pipeline.pipeline import run_all
from alfabetizacao_pipeline.sample_data import generate_sample_data
from alfabetizacao_pipeline.streaming import consume_local, simulate_local, validate_local_dlq


class PipelineEndToEndTest(unittest.TestCase):
    def test_complete_pipeline_generates_gold_and_passes_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = ProjectPaths.from_root(temp_dir)
            generate_sample_data(paths.sample)

            manifest = run_all(paths, stream_events=8, run_id="test-e2e")

            self.assertEqual("PASS", manifest["status"])
            self.assertEqual(100.0, manifest["quality_score_pct"])
            self.assertEqual(12, manifest["row_counts"]["gold"]["indicador_municipio"])
            self.assertTrue(any((paths.gold / "indicador_municipio").glob("**/*.parquet")))
            report = json.loads((paths.evidence / "latest_quality.json").read_text(encoding="utf-8"))
            self.assertEqual(0, report["summary"]["critical_failures"])

    def test_stream_checkpoint_prevents_reprocessing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = ProjectPaths.from_root(temp_dir)
            generate_sample_data(paths.sample)
            simulate_local(paths, count=5)

            self.assertEqual(5, consume_local(paths, "stream-test-1"))
            self.assertEqual(0, consume_local(paths, "stream-test-2"))

    def test_invalid_stream_event_is_redirected_to_local_dlq(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = ProjectPaths.from_root(temp_dir)
            generate_sample_data(paths.sample)

            result = validate_local_dlq(paths, "dlq-test")
            evidence = json.loads((paths.evidence / "dlq_validation.json").read_text(encoding="utf-8"))

            self.assertEqual("PASS", result["status"])
            self.assertEqual(1, result["dlq_events"])
            self.assertEqual("missing_required_fields", evidence["reason"])


if __name__ == "__main__":
    unittest.main()
