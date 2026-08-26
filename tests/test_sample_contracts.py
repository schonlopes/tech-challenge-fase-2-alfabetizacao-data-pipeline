from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from alfabetizacao_pipeline.contracts import CONTRACTS
from alfabetizacao_pipeline.sample_data import generate_sample_data


class SampleContractTest(unittest.TestCase):
    def test_generated_csvs_follow_official_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir)
            counts = generate_sample_data(destination)

            for table_name, contract in CONTRACTS.items():
                with (destination / f"{table_name}.csv").open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    self.assertEqual(list(contract.fields), reader.fieldnames)
                    self.assertEqual(counts[table_name], sum(1 for _ in reader))


if __name__ == "__main__":
    unittest.main()

