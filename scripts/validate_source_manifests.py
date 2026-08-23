from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable


MANIFEST_DIR = Path("source-manifests")
REQUIRED_INPUTS = {
    "source_inventory",
    "rule_ledger",
    "action_owner_map",
    "rulebook_outline",
    "uncertainty_register",
}
REQUIRED_SECTIONS = {"SR", "OR", "SETUP_REFERENCE"}
READINESS_STATES = {"ready", "conditional", "blocked"}
PUBLICATION_STATES = {
    "not_audited",
    "legacy_not_audited",
    "legacy_audited",
    "draft",
    "reviewed",
    "approved",
}
SECTION_STATES = {"not_audited", "audited", "draft", "reviewed", "approved"}


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    level: str
    message: str

    def format(self) -> str:
        return f"[{self.level}] {self.path.as_posix()}: {self.message}"


@dataclass
class ValidationSummary:
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    checked: int = 0

    def has_errors(self) -> bool:
        return bool(self.errors)


def _is_safe_relative_path(raw_value: object) -> bool:
    if not isinstance(raw_value, str) or not raw_value.strip():
        return False
    path = Path(raw_value)
    return not path.is_absolute() and ".." not in path.parts


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _require_string(
    data: dict[str, Any], key: str, manifest_path: Path, errors: list[ValidationIssue]
) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(
            ValidationIssue(manifest_path, "ERROR", f"`{key}` must be a non-empty string.")
        )
        return None
    return value


def _validate_string_list(
    value: object, field_name: str, manifest_path: Path, errors: list[ValidationIssue]
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(
            ValidationIssue(manifest_path, "ERROR", f"`{field_name}` must be an array of strings.")
        )
        return []
    return value


def validate_manifest(
    manifest_path: Path,
    repo_root: Path = Path("."),
    source_root: Path | None = None,
) -> ValidationSummary:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationSummary(
            errors=[ValidationIssue(manifest_path, "ERROR", f"Cannot read JSON: {exc}")],
            warnings=[],
            checked=1,
        )

    if not isinstance(data, dict):
        return ValidationSummary(
            errors=[ValidationIssue(manifest_path, "ERROR", "Manifest root must be an object.")],
            warnings=[],
            checked=1,
        )

    if data.get("schema_version") != 1:
        errors.append(ValidationIssue(manifest_path, "ERROR", "`schema_version` must be 1."))

    game = _require_string(data, "game", manifest_path, errors)
    if game and game != manifest_path.stem:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                f"`game` must match the manifest filename: expected `{manifest_path.stem}`.",
            )
        )

    site_page = _require_string(data, "site_page", manifest_path, errors)
    if site_page:
        if not _is_safe_relative_path(site_page):
            errors.append(
                ValidationIssue(manifest_path, "ERROR", "`site_page` must be a safe relative path.")
            )
        else:
            resolved_site_page = repo_root / site_page
            if not _is_within(resolved_site_page, repo_root):
                errors.append(
                    ValidationIssue(manifest_path, "ERROR", "`site_page` escapes the repository root.")
                )
            elif not resolved_site_page.is_file():
                errors.append(
                    ValidationIssue(
                        manifest_path, "ERROR", f"Site page does not exist: `{site_page}`."
                    )
                )

    resource_project = _require_string(data, "resource_project", manifest_path, errors)
    if resource_project and not _is_safe_relative_path(resource_project):
        errors.append(
            ValidationIssue(
                manifest_path, "ERROR", "`resource_project` must be a safe relative path."
            )
        )

    _require_string(data, "edition_boundary", manifest_path, errors)
    checked_date = _require_string(data, "official_sources_last_checked", manifest_path, errors)
    if checked_date:
        try:
            date.fromisoformat(checked_date)
        except ValueError:
            errors.append(
                ValidationIssue(
                    manifest_path,
                    "ERROR",
                    "`official_sources_last_checked` must use YYYY-MM-DD.",
                )
            )

    if data.get("content_authority") != "resource-ledger":
        errors.append(
            ValidationIssue(
                manifest_path, "ERROR", "`content_authority` must be `resource-ledger`."
            )
        )

    inputs = data.get("inputs")
    if not isinstance(inputs, dict):
        errors.append(ValidationIssue(manifest_path, "ERROR", "`inputs` must be an object."))
        inputs = {}
    missing_inputs = sorted(REQUIRED_INPUTS - inputs.keys())
    if missing_inputs:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                f"Missing required inputs: {', '.join(missing_inputs)}.",
            )
        )
    for input_name in REQUIRED_INPUTS & inputs.keys():
        relative_input = inputs[input_name]
        if not _is_safe_relative_path(relative_input):
            errors.append(
                ValidationIssue(
                    manifest_path,
                    "ERROR",
                    f"`inputs.{input_name}` must be a safe relative path.",
                )
            )
            continue
        if source_root is not None and resource_project:
            resource_file = source_root / resource_project / relative_input
            if not _is_within(resource_file, source_root):
                errors.append(
                    ValidationIssue(
                        manifest_path,
                        "ERROR",
                        f"`inputs.{input_name}` escapes the source root.",
                    )
                )
            elif not resource_file.is_file():
                errors.append(
                    ValidationIssue(
                        manifest_path,
                        "ERROR",
                        f"Source input does not exist: `{resource_project}/{relative_input}`.",
                    )
                )

    readiness = data.get("readiness")
    if not isinstance(readiness, dict):
        errors.append(ValidationIssue(manifest_path, "ERROR", "`readiness` must be an object."))
        readiness = {}
    readiness_status = readiness.get("status")
    if readiness_status not in READINESS_STATES:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                f"`readiness.status` must be one of: {', '.join(sorted(READINESS_STATES))}.",
            )
        )
    blocking = _validate_string_list(
        readiness.get("blocking_issues"), "readiness.blocking_issues", manifest_path, errors
    )
    _validate_string_list(
        readiness.get("open_issues"), "readiness.open_issues", manifest_path, errors
    )
    if readiness_status == "blocked" and not blocking:
        errors.append(
            ValidationIssue(
                manifest_path, "ERROR", "A blocked manifest must name at least one blocking issue."
            )
        )
    if readiness_status in {"ready", "conditional"} and blocking:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                "A ready or conditional manifest cannot contain blocking issues.",
            )
        )

    publication = data.get("publication")
    if not isinstance(publication, dict):
        errors.append(ValidationIssue(manifest_path, "ERROR", "`publication` must be an object."))
        publication = {}
    publication_state = publication.get("state")
    if publication_state not in PUBLICATION_STATES:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                f"`publication.state` must be one of: {', '.join(sorted(PUBLICATION_STATES))}.",
            )
        )
    if publication_state == "approved" and readiness_status == "blocked":
        errors.append(
            ValidationIssue(
                manifest_path, "ERROR", "A blocked resource package cannot be publication-approved."
            )
        )

    coverage = publication.get("section_coverage")
    if not isinstance(coverage, dict):
        errors.append(
            ValidationIssue(manifest_path, "ERROR", "`publication.section_coverage` must be an object.")
        )
        coverage = {}
    missing_sections = sorted(REQUIRED_SECTIONS - coverage.keys())
    if missing_sections:
        errors.append(
            ValidationIssue(
                manifest_path,
                "ERROR",
                f"Missing section coverage: {', '.join(missing_sections)}.",
            )
        )
    for section_name in REQUIRED_SECTIONS & coverage.keys():
        section = coverage[section_name]
        if not isinstance(section, dict):
            errors.append(
                ValidationIssue(
                    manifest_path,
                    "ERROR",
                    f"`publication.section_coverage.{section_name}` must be an object.",
                )
            )
            continue
        for field_name in ("included_rule_ids", "omitted_rule_ids", "unresolved_issue_ids"):
            _validate_string_list(
                section.get(field_name),
                f"publication.section_coverage.{section_name}.{field_name}",
                manifest_path,
                errors,
            )
        if "correction_rule_ids" in section:
            _validate_string_list(
                section.get("correction_rule_ids"),
                f"publication.section_coverage.{section_name}.correction_rule_ids",
                manifest_path,
                errors,
            )
        if section.get("status") not in SECTION_STATES:
            errors.append(
                ValidationIssue(
                    manifest_path,
                    "ERROR",
                    f"`publication.section_coverage.{section_name}.status` is invalid.",
                )
            )

    _validate_string_list(
        publication.get("approved_rulings"),
        "publication.approved_rulings",
        manifest_path,
        errors,
    )

    if publication_state in {"reviewed", "approved"}:
        for section_name in REQUIRED_SECTIONS:
            section = coverage.get(section_name, {})
            if isinstance(section, dict) and section.get("status") not in {"reviewed", "approved"}:
                errors.append(
                    ValidationIssue(
                        manifest_path,
                        "ERROR",
                        f"Publication state `{publication_state}` requires reviewed coverage for `{section_name}`.",
                    )
                )

    return ValidationSummary(errors=errors, warnings=warnings, checked=1)


def run_validation(
    manifest_dir: Path = MANIFEST_DIR,
    repo_root: Path = Path("."),
    source_root: Path | None = None,
) -> ValidationSummary:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    manifest_paths: Iterable[Path] = sorted(
        path for path in manifest_dir.glob("*.json") if not path.name.startswith("_")
    )
    checked = 0
    for manifest_path in manifest_paths:
        result = validate_manifest(manifest_path, repo_root=repo_root, source_root=source_root)
        errors.extend(result.errors)
        warnings.extend(result.warnings)
        checked += result.checked
    if checked == 0:
        warnings.append(
            ValidationIssue(manifest_dir, "WARN", "No source manifests were found.")
        )
    return ValidationSummary(errors=errors, warnings=warnings, checked=checked)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate 18xx site source manifests.")
    parser.add_argument("--manifest-dir", type=Path, default=MANIFEST_DIR)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()

    if args.source_root is not None and not args.source_root.is_dir():
        print(f"[ERROR] Source root does not exist: {args.source_root}")
        return 1

    summary = run_validation(
        manifest_dir=args.manifest_dir,
        repo_root=args.repo_root,
        source_root=args.source_root,
    )
    for issue in summary.errors:
        print(issue.format())
    for issue in summary.warnings:
        print(issue.format())

    if summary.has_errors():
        print(
            f"Source manifest validation failed: {len(summary.errors)} error(s), "
            f"{len(summary.warnings)} warning(s)."
        )
        return 1

    print(
        f"Source manifest validation passed: {summary.checked} manifest(s), "
        f"0 error(s), {len(summary.warnings)} warning(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
