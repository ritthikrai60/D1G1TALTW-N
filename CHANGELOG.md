# Changelog

All notable changes to the LUDUS Digital Twin project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-11-05

### Added
- **Material 3 Expressive Component System**:
  - `M3IconButton`: Standard, tonal, filled, outlined variants with interactive hover, active states, custom sizing, and accessible tooltips.
  - `M3SegmentedButton` & `M3SegmentedButtonSet`: Segmented toggle groups with active elevation, check indicator, and keyboard focus states.
  - `M3Badge`: Real-time status counter badge for ribbon items, tabs, and alerts.
  - `M3Divider`: Vertical and horizontal subtle layout dividers adhering to Material 3 design tokens.
- **Admin Symbolic CAD Workspace**:
  - `AdminToolRibbon`: Compact vertical CAD tool ribbon on the left viewport margin featuring quick keys (`[W]` Move, `[E]` Rotate, `[R]` Scale, `[A]` Vertices, `[D]` Draw, `[T]` Top-Down, Labels, and Save Default View).
  - `AdminBottomDock`: Floating snapping and action capsule providing shape switching (Rectangle vs Polygon), snapping toggles (Grid, Wall, Auto), Undo/Redo counter badges, and active drawing HUD status.
  - Symbolic Right Sidebar: Redesigned header with icon-only active tabs (`Layers`, `Placement`, `Rooms`, `Audit`), reducing visual clutter and maximizing 3D viewport canvas.
- **Viewer Material 3 Controls**:
  - Segmented quick floor selector (`All`, `F1`, `F2`, `F3`, `F4`) with active indicator.
  - Material 3 reset view and camera tools.

### Changed
- **Rollup Vendor Splitting**: Configured `manualChunks` in `vite.config.js` to split large bundles into `vendor-three` (~644 KB), `vendor-ui` (~111 KB), and `vendor-icons` (~29 KB), optimizing initial page load and caching.
- **Viewport Dimension Caching**: Cached half-width and half-height calculations on window resize in `ThreeViewport.jsx`, preventing layout thrashing and DOM reflow during 60 FPS animation loops.
- **Authentication Resilience**: Enforced strict password verification in `server/store.js` disabling hardcoded fallback defaults (`admin123`/`admin`) when a dedicated password hash is configured.

### Fixed
- **Express 5 SPA Fallback Compatibility**: Replaced deprecated wildcard route `app.get('*', ...)` with universal fallback middleware `app.use((req, res) => ...)` in `server/index.js`, eliminating `PathError: Missing parameter name at index 1: *` on startup.
- **Three.js WebGL VRAM Memory Leak**: Implemented recursive resource deallocation (`safeDisposeGroup`) for removed meshes, textures, and geometry, with safe guards for shared rack models (`isSharedModelInstance`).
- **Asset Cache Busting Overhead**: Removed dynamic timestamp query strings from `/models/building.glb` in `ThreeViewport.jsx`, allowing browser HTTP caching of the 3.36 MB 3D asset.
- **Network Scanner Command Injection Vulnerability**: Replaced raw shell string execution (`execAsync`) in `server/scanner.js` with parameterized binary execution (`execFileAsync`) and strict IPv4 input validation regex.
- **Server Proxy SSRF Protection**: Hardened `/api/proxy` in `server/api.js` against Server-Side Request Forgery by blocking local loopback addresses (`127.0.0.1`, `localhost`, `::1`) and cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`). Disallowed query parameter token transmission.
- **PostgreSQL Test Suite Resilience**: Updated `tests/api_and_schema.test.mjs` (tests 9, 10, 12) with connection health checks and safe disconnect teardowns, allowing unit test execution (12/12 passing) regardless of whether local Docker DB is active or offline.

### Removed
- **Legacy Dead Code**: Removed unreferenced legacy file `src/main.js` (1,809 lines, 73 KB) from the project root.

---

## [2.0.0] - 2026-10-31
- Initial major baseline release with LUDUS 4-story architectural CAD model, Three.js 3D viewport, Rackula rack elevation designer, multi-network ping scanner, and admin dashboard.

