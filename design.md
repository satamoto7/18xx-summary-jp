# SIGNAL INDEX — Design System

## Design thesis

SIGNAL INDEX is a fast reference interface for people who already understand 18xx terminology. It should feel like a contemporary railway operations index: exact, calm, dense, and immediately usable during play. The content is the product; decoration never competes with it.

- **Genre:** modern-minimal
- **Theme:** Cobalt-derived custom theme, `SIGNAL INDEX`
- **Enrichment:** none beyond the existing game-cover thumbnails
- **Motion:** motion-cut; state changes only
- **Navigation:** N9 edge-aligned data bar on desktop, existing drawer pattern on small screens
- **Footer:** Ft2 restrained inline colophon

## User jobs

1. Find a title by name with almost no scrolling.
2. Compare year, player count, duration, and designer at a glance.
3. Open a summary and jump to SR, OR, or setup immediately.
4. Locate a section during play without losing the current tab or reading position.
5. Download an approved tabletop PDF when available, or report a play on X without leaving the reference workflow.

## Shared macrostructure

### Site shell

- A 48–52 px edge-aligned header carries the site name, the game-index link, and global search.
- The permanent desktop game tree is removed. The full game list remains available through the index page, global search, and the small-screen drawer.
- The page grid is allowed to expand to 88 rem. Summary pages keep a slim right-hand section map where space permits.
- The content canvas uses cool near-white paper, visible grid rules, and almost no elevation.

### Home — Index First

- Compact identity mast rather than a marketing hero.
- The existing introduction and primary game-index action remain authoritative.
- A generated quick index exposes every game title without duplicating game descriptions.
- Usage, update policy, feedback, and BGG attribution become quiet reference blocks below the index.

### Game catalogue — Tabular Index

- Replace large cards with full-width data rows.
- Desktop columns: cover, title/description, year, players, duration, designer, open affordance.
- The full row is the primary target; BGG remains a secondary text link.
- Search is always visible. Advanced filters remain available but visually secondary.
- Target density: 6–8 rows in a typical desktop viewport and 3–4 rows on a phone.
- Mobile rows keep title, year, players, and duration; secondary prose is clamped.

### Game summary — Reference Workbench

- The title, tabletop-PDF/X-report actions, author attribution, game-index link, and tab set form one clear operating header.
- The tabletop PDF is the primary action only when an approved file exists. The interface does not advertise unfinished PDFs.
- Author attribution stays quiet below the title. The note support link is visually separated from free downloads and reports.
- SR, OR, and setup tabs are full-width and sticky below the site bar.
- Body content is not wrapped in a decorative card. Headings, rules, and spacing establish hierarchy.
- Tables use clear rules and horizontal overflow affordances; no viewport-level horizontal scroll.
- Desktop keeps a narrow active section map. Smaller screens use the existing searchable section control as an inline disclosure directly below the tabs, so it never covers rule content.

## Theme

All authored colour tokens use OKLCH. The visual field is cool and low-chroma; cobalt is reserved for focus, selected tabs, active navigation, and the primary open action.

- **Paper:** cool near-white, never a gradient
- **Ink:** blue-black rather than pure black
- **Rules:** cool gray-blue at two strengths
- **Accent:** vivid cobalt, under 5% of the visible surface
- **Semantic colours:** muted green, amber, and red, used only when content requires them
- **Elevation:** hairline borders first; one restrained shadow token for drawers and overlays

## Typography

- **Display / game names:** `Bahnschrift`, `DIN Alternate`, `Arial Narrow`, then the Japanese body stack. Latin titles and numerals may read condensed; Japanese glyphs fall back cleanly.
- **Body:** system UI, `Noto Sans JP`, `Yu Gothic UI`, sans-serif.
- **Labels / metadata:** the condensed display stack at smaller sizes with tabular numerals. The live interface uses two active type roles, not a decorative third face.
- Titles are left-aligned and tight-set. Body measure is 68 ch. Metadata uses tabular numerals.
- No display line is forced into all caps when it contains Japanese.

## Spacing and geometry

- 4 px base scale only.
- Controls are at least 44 px on touch layouts and may reduce to 36–40 px on pointer layouts.
- Default radii are 4 px and 6 px. Larger 10 px radii are reserved for drawers/overlays.
- Pills are reserved for compact status/filter states, not for primary navigation or cards.
- Borders and whitespace, not shadows, separate information.

## Motion and interaction

- No entrance animation, parallax, shimmer, bounce, or decorative motion.
- Hover/focus changes use opacity, colour, and at most a 2 px translation over 120–180 ms.
- `prefers-reduced-motion: reduce` removes all transitions and smooth scrolling.
- Every clickable row and control has a visible keyboard focus state.
- Clickable labels must remain on one line; surrounding layout wraps instead.

## Responsive behaviour

- `320`, `375`, `414`: one-column rows, compact metadata grid, sticky tab strip, no covered content.
- `768`: list becomes denser; secondary details can reappear.
- `1024+`: full tabular catalogue and right summary map.
- Root overflow is clipped, but inner table wrappers remain horizontally scrollable.
- No element may create document-level horizontal scrolling.

## Per-page allowances

- Game covers may be absent. Missing covers use a neutral indexed placeholder without illustration.
- Long game titles may occupy two lines only when they are not interactive labels; linked title text remains a single-line ellipsis in dense catalogue rows.
- Summary Markdown and generated text remain unchanged. Structural wrappers and shared styles may alter presentation only.
- Print output remains governed by the existing print stylesheet and must not inherit sticky or overlay behaviour.

## Exports

- Portable tokens: `tokens.css`
- Site token mapping: `docs/stylesheets/theme-tokens.css`
- Site shell: `docs/stylesheets/site-shell.css` and `docs/javascripts/site-shell.js`
- Catalogue components: `main.py`, `docs/stylesheets/cards.css`, `docs/stylesheets/game-filter.css`, and `docs/javascripts/game-filter.js`
- Summary workbench: `docs/stylesheets/tabs.css`, `docs/stylesheets/summary-navigation.css`, and `docs/javascripts/summary-navigation.js`
