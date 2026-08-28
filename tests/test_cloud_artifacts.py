from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


class CloudArtifactsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.gcp = cls.root / "cloud" / "gcp"

    def test_all_terraform_sql_references_exist(self) -> None:
        main = (self.gcp / "main.tf").read_text(encoding="utf-8")
        referenced = set(re.findall(r'"([a-z_]+\.sql)"', main))
        referenced.add("quality_checks.sql")
        referenced.add("export_gold_parquet.sql")
        missing = [name for name in sorted(referenced) if not (self.gcp / "sql" / name).exists()]
        self.assertEqual([], missing)

    def test_stream_schema_is_valid_json_and_contains_event_key(self) -> None:
        schema = json.loads((self.gcp / "schemas" / "alunos_stream.json").read_text(encoding="utf-8"))
        fields = {item["name"] for item in schema}
        self.assertIn("event_id", fields)
        self.assertIn("event_ts", fields)
        self.assertIn("id_municipio", fields)

    def test_no_credentials_are_committed(self) -> None:
        text_extensions = {".hcl", ".json", ".md", ".sql", ".tf", ".txt", ".yaml", ".yml"}
        for path in self.gcp.glob("**/*"):
            if path.is_file() and path.suffix.lower() in text_extensions:
                content = path.read_text(encoding="utf-8")
                self.assertNotIn('"type": "service_account"', content, path)
                self.assertNotIn("private_key_id", content, path)


if __name__ == "__main__":
    unittest.main()

