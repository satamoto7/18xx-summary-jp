---
name: publish-18xx-summary-to-site
description: Create or revise an 18xx game page in this MkDocs site from an authoritative summary-resource package with a source inventory, rule ledger, action-owner map, and uncertainty register. Use for resource-derived Web summaries; do not use merely to import a user-supplied finished Markdown draft.
---

# Publish 18xx Summary to Site

Create a Web summary independently from the canonical rule resources. A finished player-aid PDF and an older site summary are comparison material, not the factual source.

## Read first

1. Read the repository `AGENTS.md` and `docs/_template.md`.
2. Read [references/resource-contract.md](references/resource-contract.md) to decide whether the upstream resource package is publishable.
3. Read [references/site-content-contract.md](references/site-content-contract.md) before selecting or arranging rules for the Web page.
4. Read the target game's `source-manifests/<game>.json`. Create it from `assets/source-manifest.template.json` when it does not exist.

## Authority boundary

- Treat the upstream source inventory and rule ledger as the canonical bridge. Prefer official errata and official FAQs over superseded rulebook wording.
- Use prior Japanese summaries and the finished print aid only to find omissions, compare terminology, and preserve accepted wording. Never use them as the sole authority for a rule.
- Never fill a gap by analogy with another 18xx title or by copying the site's template examples.
- Recheck Web-hosted official errata before a new publication or substantive revision. If the live source differs from the upstream inventory, stop publication and report that the upstream resource package must be reconciled first. Do not create a site-only interpretation.
- Keep unresolved rules visible. A play-affecting ambiguity must either remain blocked or be presented as an explicit pre-game ruling approved by the user.

## Workflow

1. **Identify the target and scope.** Confirm the game, edition boundary, site page, upstream resource folder, and whether this is an audit, draft, replacement, or new page.
2. **Validate the bridge.** Run `python scripts/validate_source_manifests.py --source-root "<summary-resource-root>"`. Read every required input named by the target manifest.
3. **Apply the readiness gate.** Do not write a publishable page while the manifest is `blocked`. A `conditional` package may proceed only when its open items cannot silently change the published rule or are explicitly represented in the page.
4. **Build section coverage.** Map stable ledger IDs to the Web tabs and record included, intentionally omitted, and unresolved IDs in the manifest. Use the action-owner map for execution order and the content boundary for deliberate omissions.
5. **Draft for Web lookup.** Organize by SR, OR, setup/quick reference, and genuinely separate game-specific rounds. Do not reproduce the print aid's four-page order. Keep each rule in the action where it is used.
6. **Audit high-risk content.** Check auctions, share transactions, capitalization and float, market movement, transfers, train purchase and emergency funding, routes, private abilities, phase transitions, end timing, scoring, and tie handling against stable ledger IDs.
7. **Compare, then replace.** For an existing page, produce a source-backed difference report before overwriting it. Preserve user-approved terminology when it remains consistent with the authoritative resources. Obtain explicit user approval for the first resource-derived replacement of an existing game page.
8. **Publish mechanically.** Preserve the site's actions block and supported tab structure. Update the game index and `.pages` only for a new title. Run `python scripts/export_text.py`, then `scripts/check_site.ps1`.
9. **Record the handoff.** Set the manifest publication state, comparison date, included and omitted ledger IDs, explicit rulings, and remaining open items. Report every changed `.md`, generated `.txt`, manifest, and index/navigation file.

## Stop conditions

Stop before publishing and report the exact issue when any of these is true:

- edition or source authority is not fixed;
- required source inventory or ledger files are missing;
- official errata changed after the upstream inventory was prepared;
- a high-risk rule lacks evidence or contradicts another authoritative source;
- a play-affecting unresolved issue has no approved visible treatment;
- the requested change would silently replace accepted Japanese terminology without user review.

Do not edit the upstream summary-resource project unless the user separately authorizes it. Do not edit `docs/assets/` manually.
