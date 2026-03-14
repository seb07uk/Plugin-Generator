# polsoft.ITS™ Plugin Generator v4.3.0

> Desktop tool for **polsoft.ITS™ Script Editor** — scaffold, validate and package plugins in seconds.

**Developer:** Sebastian Januchowski | **Company:** polsoft.ITS™ Group
**Contact:** polsoft.its@fastservice.com | **GitHub:** github.com/seb07uk
**License:** MIT | **Copyright:** 2026© Sebastian Januchowski & polsoft.ITS™

---

## Getting Started

`PluginGenerator.exe` is fully portable — no installation or Python required.

1. Copy `PluginGenerator.exe` anywhere on your disk
2. Double-click to launch
3. The GUI opens automatically

> On first run Windows SmartScreen may appear — click **"More info" → "Run anyway"**.

---

## Interface — 6 Tabs

**Generator** — Fill in plugin name, ID, author, profile and output folder, then click **✦ Generate**. The file list appears on the right; click any file to preview its content. Use **📦 Build ZIP** to pack the plugin into a `.pits-plugin.zip` archive.

**Wizard** — Four-step guided assistant. Walks you through name → profile → hooks → confirm without needing to know the technical details.

**Templates** — Jinja2 template system. Generate `.j2` scaffold files for a profile, validate them, or render a test plugin from a custom template.

**Options** — Toggle which extra files get generated: pytest tests, selftest runner, CHANGELOG, integrity hashes, install scripts, diagnostics, auto-update descriptor, and more. All are enabled by default.

**Validator** — Validate a single `manifest.yaml` or an entire plugin folder (10-area check: manifest, hooks, structure, UI, config, icons, libs, metadata). The **Verify SHA-256** button detects any file tampering after generation.

**About** — Version and author information.

---

## Plugin Profiles

| Profile | Best for |
|---------|----------|
| `minimal` | Single-file plugin, no dependencies |
| `advanced` | UI panel + helper library |
| `enterprise` | DI container, event bus, telemetry |
| `ui-heavy` | Theme engine, dynamic panel |
| `analysis` | Code analyzer + report builder |
| `terminal` | Shell runner, process lifecycle |
| `wizard` | Multi-step guided UI |
| `telemetry` | Metrics aggregation and push |
| `database` | Connection manager, query runner |
| `network` | HTTP client, request/response hooks |

---

## Generated Output

Every plugin includes: `manifest.yaml`, `main.py`, config, 5 SVG icon variants, UI panel (advanced+ profiles), profile-specific libraries, 4 pytest test files, `integrity.json` (SHA-256 + MD5), install scripts, and full diagnostics reports.

---

## System Requirements

| | |
|-|--|
| **OS** | Windows 10 / 11 (64-bit) |
| **RAM** | 256 MB minimum |
| **Disk** | ~50 MB |
| **Dependencies** | None — everything bundled in the EXE |

---

*2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.*
