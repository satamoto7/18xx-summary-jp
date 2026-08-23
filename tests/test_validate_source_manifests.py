from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_source_manifests import run_validation, validate_manifest


def valid_manifest() -> dict[str, object]:
    section = {
        "included_rule_ids": [],
        "omitted_rule_ids": [],
        "unresolved_issue_ids": [],
        "status": "not_audited",
    }
    return {
        "schema_version": 1,
        "game": "18Test",
        "site_page": "docs/games/18Test.md",
        "resource_project": "18Test",
        "edition_boundary": "Official rules v1 + official errata",
        "official_sources_last_checked": "2026-08-24",
        "content_authority": "resource-ledger",
        "inputs": {
            "source_inventory": "source-inventory.md",
            "rule_ledger": "sr-or-rule-ledger.csv",
            "action_owner_map": "action-owner-map.md",
            "rulebook_outline": "rulebook-outline.md",
            "uncertainty_register": "uncertainty-register.csv",
        },
        "readiness": {
            "status": "conditional",
            "blocking_issues": [],
            "open_issues": ["18TEST-U-001"],
            "notes": "",
        },
        "publication": {
            "state": "not_audited",
            "last_compared_to_site": None,
            "section_coverage": {
                "SR": dict(section),
                "OR": dict(section),
                "SETUP_REFERENCE": dict(section),
            },
            "approved_rulings": [],
            "notes": "",
        },
    }


class ValidateSourceManifestTests(unittest.TestCase):
    def test_legacy_audited_manifest_accepts_correction_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "games").mkdir(parents=True)
            (root / "docs" / "games" / "18Test.md").write_text("test", encoding="utf-8")
            payload = valid_manifest()
            payload["publication"]["state"] = "legacy_audited"  # type: ignore[index]
            for section in payload["publication"]["section_coverage"].values():  # type: ignore[index, union-attr]
                section["status"] = "audited"
                section["correction_rule_ids"] = ["18TEST-SR-001"]
            manifest_path = root / "18Test.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")

            result = validate_manifest(manifest_path, repo_root=root)

            self.assertEqual([], result.errors)

    def test_valid_manifest_passes_with_existing_site_and_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / "source-manifests"
            site_dir = root / "docs" / "games"
            source_dir = root / "sources" / "18Test"
            manifest_dir.mkdir()
            site_dir.mkdir(parents=True)
            source_dir.mkdir(parents=True)
            (site_dir / "18Test.md").write_text("# 18Test サマリー\n", encoding="utf-8")
            payload = valid_manifest()
            for relative_path in payload["inputs"].values():  # type: ignore[union-attr]
                (source_dir / relative_path).write_text("test\n", encoding="utf-8")
            manifest_path = manifest_dir / "18Test.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")

            result = validate_manifest(
                manifest_path, repo_root=root, source_root=root / "sources"
            )

            self.assertEqual([], result.errors)

    def test_missing_required_input_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "games").mkdir(parents=True)
            (root / "docs" / "games" / "18Test.md").write_text("test", encoding="utf-8")
            payload = valid_manifest()
            del payload["inputs"]["rule_ledger"]  # type: ignore[index]
            manifest_path = root / "18Test.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")

            result = validate_manifest(manifest_path, repo_root=root)

            self.assertTrue(any("rule_ledger" in issue.message for issue in result.errors))

    def test_blocked_manifest_requires_named_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "games").mkdir(parents=True)
            (root / "docs" / "games" / "18Test.md").write_text("test", encoding="utf-8")
            payload = valid_manifest()
            payload["readiness"]["status"] = "blocked"  # type: ignore[index]
            payload["readiness"]["blocking_issues"] = []  # type: ignore[index]
            manifest_path = root / "18Test.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")

            result = validate_manifest(manifest_path, repo_root=root)

            self.assertTrue(any("blocked manifest" in issue.message for issue in result.errors))

    def test_repository_manifests_pass_structural_validation(self) -> None:
        result = run_validation()
        self.assertEqual([], result.errors)
        self.assertGreaterEqual(result.checked, 3)


if __name__ == "__main__":
    unittest.main()
