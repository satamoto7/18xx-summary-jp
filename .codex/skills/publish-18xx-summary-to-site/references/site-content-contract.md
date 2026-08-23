# Web summary content contract

The Web summary is a play-time reference for experienced 18xx players. It is not a transcript of the print aid and not a shortened copy of the rulebook.

## Source-to-page mapping

| Upstream resource | Web use |
|---|---|
| Source inventory | Edition and provenance boundary |
| Rule ledger | Every published rule, value, trigger, exception, and omission decision |
| Action-owner map | Action order and the grammatical subject of each instruction |
| Rulebook outline | Coverage check and discovery of rules outside SR/OR |
| Uncertainty register | Blocker, explicit official silence, or approved pre-game ruling |
| Content boundary | Deliberate omission reasons |
| Print aid / prior summary | Accepted terminology and omission comparison only |

## Site structure

- `SR`: initial auction or petition when it feeds the share round, share sales and purchases, company formation/float, presidency, limits, priority, and SR-end effects.
- `OR`: company order, track, tokens, routes, revenue, dividends, market movement, trains, emergency funding, company finance, and OR-end effects.
- `セットアップ / 早見`: setup, phases, trains, entities, limits, bonuses, and frequently consulted tables.
- Separate tabs are allowed for a genuinely distinct merger, nationalization, intermediate, or end-game process. Do not create a tab merely to mirror a print page.

Place a rule where the player needs it. Use a short cross-reference rather than duplicating the full rule in several tabs.

## Coverage boundary

Prioritize title-specific deviations, quantities, denominators, triggers, direction of market movement, transfers, surviving abilities, and state transitions. Universal 18xx mechanics may be omitted only when the target title does not modify them and the omission is recorded in the manifest.

Tables are preferred for repeated dimensions. Prose should use action first, condition second, and exception last. Name the real actor and receiver. Use the board's physical market directions when that is how players execute a move.

## Traceability

Before review, fill each manifest section's `included_rule_ids`, `omitted_rule_ids`, and `unresolved_issue_ids`. Every published numeric value or title-specific exception must trace to at least one stable ledger ID. Record an omission reason beside every intentionally omitted title-specific rule.

The visible page does not need source IDs in every sentence. The manifest is the review bridge and must be updated in the same change as the Markdown.

## Existing pages

Audit an existing page before replacing it. Classify differences as:

- confirmed and retained;
- corrected from authoritative resources;
- added because the current page omits a high-risk or title-specific rule;
- removed as unsupported, superseded, duplicated, or outside the coverage boundary;
- held for user decision.

Do not change accepted terminology for stylistic preference alone. The first source-derived replacement of an existing page requires an explicit user decision after the difference report.

## Publication completion

A page is publishable only when:

- its manifest is not `blocked`;
- official-source freshness has been checked for this revision;
- all high-risk statements are traced;
- unresolved play-affecting items are visibly handled or explicitly excluded with approval;
- the generated text file and full site checks pass;
- the user has approved content changes when replacing an existing summary.
