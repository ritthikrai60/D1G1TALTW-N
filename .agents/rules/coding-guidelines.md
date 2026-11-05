---
trigger: always_on
description: LUDUS Digital Twin coding, UX/UI and safety rules. Full detail in docs/CODING_GUIDELINES.md.
---

# LUDUS Digital Twin — Agent Rules

1. Before editing, read `SKILL.md` and `docs/FEATURES_REQUIREMENTS.md`. Never remove or shrink existing features without explicit user approval.
2. Route `/` must never expose a link/button to `/admin`. Devices with `isPlaced:false` must never appear in public views (3D pins, stats, directory, `/api/public/state`).
3. Viewer menu keeps the 5 Accordion sections and all 8 layer switches (`exploded, showGlass, showWalls, showRoof, showBasketball, showArrows, showPlans, showRooms`).
4. UI: use design tokens (`bg-background`, `text-primary`, `--md-sys-*`) — no hard-coded hex or `slate-/purple-` colors in JSX. Status colors: Online `#22c55e`, Warning `#f59e0b`, Offline `#ef4444`; always pair color with icon/text.
5. Icon-only buttons need `aria-label`; toggles need `aria-pressed`; keep focus ring visible; respect reduced motion.
6. New UI goes in new components/hooks, not into `src/App.jsx` (152KB). Tests in `tests/api_and_schema.test.mjs` grep source strings — if you move code, update tests in the same change without weakening them.
7. Dispose Three.js geometry/material/texture; clean up effects and listeners.
8. Do not delete unrelated comments/docstrings. Never print or commit secrets from `.env`.
9. Finish every change with `npm run build; npm test` (all must pass), then summarize what changed.
10. Full conventions: `docs/CODING_GUIDELINES.md`.

