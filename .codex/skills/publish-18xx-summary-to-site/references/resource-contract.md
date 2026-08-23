# Resource package contract

Use this contract when deciding whether an upstream summary project can feed a Web summary.

## Required inputs

Every resource-derived site page needs:

- `source-inventory.md`: edition boundary, authority order, official URLs, local source paths, hashes when available, last verification date, and applied errata;
- a rule ledger such as `sr-or-rule-ledger.csv` or `rule-ledger.csv`: stable rule ID, source locator, authority, actor, timing/condition, action, value or limit, consequence, exception, target location, and status;
- `action-owner-map.md`: the acting player, company, bank, or system and the order of actions;
- `rulebook-outline.md`: coverage of the complete rulebook so that missing translation does not become missing rules;
- `uncertainty-register.csv`: conflicts, gaps, official silence, impact, state, and next action.

Recommended inputs are a content-boundary or omission log, a high-risk audit, accepted/forbidden phrase lists, and extracted rule text. A completed PDF, HTML print master, or older Japanese summary is secondary evidence only.

## Authority order

1. Current official errata and official FAQ.
2. The fixed official rulebook edition.
3. Official boards, charts, company charters, and component text.
4. Official designer or publisher clarifications, clearly identified.
5. User-approved table rulings, clearly labeled as rulings rather than official rules.
6. Existing summaries, digital implementations, and community rulings for comparison only.

Do not silently merge editions. Do not promote an unofficial source because it is more convenient or already translated.

## Readiness states

- `ready`: required resources exist, high-risk rules are traced, and no unresolved issue can change legal play or scoring.
- `conditional`: the page may be drafted, but named open items must either be outside the selected coverage or visibly represented without inventing a ruling.
- `blocked`: authoritative evidence, high-risk coverage, or a required user ruling is missing. Do not replace or publish the site page.

Traceability-only gaps may be `conditional`; missing auction resolution, money-transfer actor, end timing, or another high-risk rule is normally `blocked`.

## Upstream change rule

The summary-resource project remains canonical. Recheck official Web sources before site publication. If an official source changed, return to the upstream summary workflow first, update its inventory and ledger, and only then refresh the site's source manifest and page.

The site repository records what it consumed; it does not become a second independent rule ledger.

## Path resolution

Manifests store a portable `resource_project` folder name and paths relative to it. Do not store a machine-specific absolute source root. Supply the root only while validating:

```powershell
python scripts/validate_source_manifests.py --source-root "D:\My Document\1_Project\04_game\18xxサマリー作成"
```

Without `--source-root`, validation checks manifest shape and site paths only so CI can run without the private source archive.
