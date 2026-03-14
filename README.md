# polsoft.ITS™ Plugin Generator

> **Developer tool for [polsoft.ITS™ Script Editor](https://github.com/seb07uk)** — scaffold, validate, and ship editor plugins in seconds.

[![Version](https://img.shields.io/badge/version-4.3.0-6C63FF?style=flat-square)](https://github.com/seb07uk)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/seb07uk)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

---

## Overview

**polsoft.ITS™ Plugin Generator** is a portable, single-file developer tool that generates complete plugin packages for the polsoft.ITS™ Script Editor. It supports 10 built-in plugin profiles, a full Jinja2 template system, SHA-256 integrity verification, and a bilingual (PL/EN) GUI with a deep dark theme — all from one Python file with zero mandatory dependencies.

Run it with a graphical interface or drive it entirely from the command line, integrate it into CI, or embed it as a library.

![GUI Screenshot](docs/screenshot.png)

---

## Features

| Feature | Details |
|---|---|
| **10 plugin profiles** | `minimal` · `advanced` · `enterprise` · `ui-heavy` · `analysis` · `terminal` · `wizard` · `telemetry` · `database` · `network` |
| **Jinja2 template system** | Generate `.j2` scaffolds per profile, render them into full plugins, validate templates |
| **SHA-256 integrity** | Every generated file is hashed; `verify-integrity` detects any post-generation tampering |
| **Full validator** | 10-area plugin validator: manifest · hooks · structure · UI · config · icons · libs · metadata |
| **6-tab GUI** | Generator · Wizard · Templates · Options · Validator · About |
| **CLI with 8 commands** | Fully scriptable — no display required |
| **Bilingual** | Polish / English UI toggle |
| **Single-file, zero mandatory deps** | Runs with Python 3.8+ out of the box |

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | Required |
| tkinter | bundled | Required for GUI only |
| PyYAML | 6.0+ | Optional — enables full YAML manifest validation |
| Jinja2 | 3.0+ | Optional — enables full `.j2` template rendering |

Install optional dependencies:

```bash
pip install pyyaml jinja2
```

### Installation

No installation required. Download the single file and run it:

```bash
# Download
curl -O https://raw.githubusercontent.com/seb07uk/polsoft-plugin-generator/main/plugin_generator_5.py

# Launch GUI
python plugin_generator_5.py

# Or use CLI
python plugin_generator_5.py --help
```

---

## Usage

### GUI mode

Double-click `plugin_generator_5.py` or run:

```bash
python plugin_generator_5.py
python plugin_generator_5.py --gui
```

The GUI opens with six tabs:

- **Generator** — fill in plugin name, ID, profile, styles, and click **✦ Generate**
- **Wizard** — interactive four-step creation assistant
- **Templates** — generate `.j2` scaffolds, validate and test templates
- **Options** — toggle optional output files (tests, changelog, integrity, meta-plugins…)
- **Validator** — validate `manifest.yaml` or an entire plugin folder; verify SHA-256 hashes
- **About** — version and author information

### CLI mode

```bash
python plugin_generator_5.py --list-profiles
python plugin_generator_5.py --list-templates ./templates
python plugin_generator_5.py --generate MyPlugin --profile advanced --out ~/Desktop
python plugin_generator_5.py --test-template analysis --templates-dir ./templates --out /tmp
python plugin_generator_5.py --validate ./MyPlugin/manifest.yaml
python plugin_generator_5.py --validate-plugin ./MyPlugin
python plugin_generator_5.py --verify-integrity ./MyPlugin
```

#### All CLI options

```
usage: plugin_generator_5.py [--gui] [--list-profiles] [--list-templates [DIR]]
                              [--generate NAME] [--test-template PROFILE]
                              [--validate MANIFEST] [--validate-plugin DIR]
                              [--verify-integrity DIR]
                              [--profile PROFILE] [--pid PID] [--author AUTHOR]
                              [--license LICENSE] [--desc DESC]
                              [--icon-style {neon,pixel,symbolic,gradient,dark}]
                              [--code-style {PEP8,compact,verbose,enterprise}]
                              [--ui-layout {sidebar,tabs,modal,split}]
                              [--out DIR] [--templates-dir DIR]
                              [--no-validate] [--json]
```

---

## Plugin Profiles

| Profile | Description | Key hooks |
|---|---|---|
| `minimal` | Single-file, no dependencies | `onLoad` · `onCommand` |
| `advanced` | UI panel + helper library | +`onEditorReady` · `onFileOpen` · `onFileSave` |
| `enterprise` | DI container, event bus, telemetry | +`onEvent` · `onError` · `onTelemetry` |
| `ui-heavy` | Theme engine, dynamic panel | +`onThemeChange` · `onPanelResize` |
| `analysis` | Code analyzer + report builder | +`onAnalysisRequest` · `onDiagnostic` |
| `terminal` | Shell runner, process lifecycle | +`onTerminalInput` · `onProcessStart` |
| `wizard` | Multi-step guided UI | +`onWizardStep` · `onWizardComplete` |
| `telemetry` | Metrics aggregation + push | +`onTelemetry` · `onMetric` |
| `database` | Connection manager, query runner | +`onDbConnect` · `onDbQuery` |
| `network` | HTTP client, request/response hooks | +`onRequest` · `onResponse` · `onTimeout` |

---

## Generated Plugin Structure

```
MyPlugin/
├── manifest.yaml              # Plugin manifest (name, id, version, hooks, permissions)
├── main.py                    # Entry point — hook implementations
├── README.txt                 # Plugin documentation
├── CHANGELOG.md
├── requirements.txt
├── integrity.json             # SHA-256 + MD5 for every file
├── plugin-info.json           # API manifest
├── update.json                # Auto-update descriptor
├── .plugin-manifest.yaml      # Plugin Manager integration
├── install.ps1 / install.bat  # Windows installer scripts
│
├── config/
│   └── default.json
│
├── icons/
│   ├── plugin.svg             # 5 icon variants
│   ├── panel.svg
│   ├── toolbar.svg
│   ├── plugin_dark.svg
│   └── plugin_symbolic.svg
│
├── ui/                        # (advanced+ profiles)
│   ├── panel.html
│   └── panel.css
│
├── libs/                      # Profile-specific libraries
│   └── helper.py / analyzer.py / telemetry.py / …
│
├── tests/                     # pytest suite (4 files)
│   ├── test_load.py
│   ├── test_commands.py
│   ├── test_ui.py
│   └── test_config.py
│
├── selftest.py                # Standalone self-test runner
│
├── diagnostics/
│   ├── plugin_structure.json
│   ├── file_hashes.json
│   ├── manifest_report.json
│   └── plugin_report.json     # Full validation report
│
└── generator_plugins/         # Meta-plugin system
    ├── README.txt
    ├── add_enterprise_features.py
    ├── add_ui_themes.py
    ├── add_tests.py
    ├── add_telemetry.py
    └── add_database_support.py
```

---

## Template System

The generator includes a full Jinja2-compatible template system (§1–10 of the integration specification).

### Create templates for a profile

```bash
python plugin_generator_5.py --test-template advanced --templates-dir ./templates --out /tmp
```

This will:
1. Generate `.j2` scaffold files in `templates/advanced/`
2. Generate `template.json` descriptor
3. Validate the template (errors + warnings)
4. Render a test plugin and verify its SHA-256 integrity

### Template variables

Every `.j2` file can use:

```
{{ name }}        {{ plugin_id }}    {{ description }}   {{ author }}
{{ version }}     {{ profile }}      {{ company }}        {{ email }}
{{ github }}      {{ copyright }}    {{ license }}        {{ brand }}
{{ hooks }}       {{ commands }}     {{ panels }}         {{ permissions }}
{{ ui_layout }}   {{ icon_style }}   {{ code_style }}     {{ generated }}
{{ generator }}
```

### Add your own template

```
templates/
└── my_profile/
    ├── manifest.yaml.j2
    ├── main.py.j2
    ├── README.txt.j2
    ├── template.json          ← required descriptor
    └── …                      ← any additional .j2 files
```

**`template.json` format:**

```json
{
  "type": "advanced",
  "hooks": ["onLoad", "onCommand", "onFileOpen"],
  "commands": ["run", "analyze"],
  "panels": ["main"],
  "ui": "dark",
  "requires": {
    "filesystem": true,
    "editor": "full-access"
  }
}
```

---

## Integrity Verification

Every generated plugin includes `integrity.json` with SHA-256 + MD5 hashes for all files.

```json
{
  "algorithm": "SHA-256",
  "generator": "polsoft.ITS™ Plugin Generator v4.2.0",
  "files": {
    "manifest.yaml": {
      "algorithm": "SHA-256",
      "sha256": "a3f1…",
      "md5":    "c2b9…",
      "size":   1264
    }
  }
}
```

Verify at any time:

```bash
python plugin_generator_5.py --verify-integrity ./MyPlugin
```

```
✓ SHA-256 Integrity: PASS
  Checked: 30  Passed: 30  Failed: 0
  All files match their SHA-256 hashes.
```

If a file has been modified:

```
✗ SHA-256 Integrity: FAIL
  Checked: 30  Passed: 29  Failed: 1

  Mismatches:
    • main.py  [SHA-256 mismatch]
      Expected: a3f1c8d2…
      Actual:   77b3e91f…
```

---

## Validation

### Validate a manifest

```bash
python plugin_generator_5.py --validate ./MyPlugin/manifest.yaml
```

### Validate a full plugin directory

```bash
python plugin_generator_5.py --validate-plugin ./MyPlugin
```

The validator checks **10 areas**:

1. `manifest.yaml` — required fields, ID format, version, hooks, panels
2. `main.py` — required hooks, profile-specific hooks, author metadata
3. Folder structure — per-profile required paths
4. UI files — `panel.html` elements, `panel.css` selectors
5. `config/default.json` — JSON validity, `__meta`, profile-specific sections
6. Icons — 5 SVG variants, `<svg>` validity
7. `plugin-info.json` — API section, hooks, permissions
8. `integrity.json` — structure and generator field
9. Library files — profile-specific `libs/` contents
10. Optional recommended files — README, update.json, CHANGELOG

Reports are saved to `diagnostics/plugin_report.json`.

---

## Options

| Option | Default | Description |
|---|---|---|
| Pytest tests (4 files) | ✓ | `test_load` · `test_commands` · `test_ui` · `test_config` |
| `selftest.py` | ✓ | Standalone self-test runner (no pytest needed) |
| `CHANGELOG.md` | ✓ | Release notes stub |
| `requirements.txt` | ✓ | Profile-aware dependency list |
| Install scripts | ✓ | `.ps1` + `.bat` Windows installers |
| Diagnostics | ✓ | `plugin_structure.json` · `file_hashes.json` · `manifest_report.json` |
| `integrity.json` | ✓ | SHA-256 + MD5 hashes for all files |
| `update.json` | ✓ | Auto-update checker stub |
| `plugin-info.json` | ✓ | Full API manifest |
| `.plugin-manifest.yaml` | ✓ | Plugin Manager integration |
| `generator_plugins/` | ✓ | Meta-plugin extension system |
| **Auto-validate after generation** | ✓ | Runs full validator + saves report automatically |

---

## Meta-Plugin System

The `generator_plugins/` directory lets you extend the generator without modifying its core. Each file exposes a single function:

```python
def apply(staged: dict, context: dict) -> dict:
    # staged  = {rel_path: content}  — all files about to be written
    # context = {name, pid, profile, author, …}
    staged["libs/my_addon.py"] = "# injected by meta-plugin\n"
    return staged
```

Bundled meta-plugins:

| File | Effect |
|---|---|
| `add_enterprise_features.py` | Appends DI + telemetry stub comments |
| `add_ui_themes.py` | Injects extra CSS theme variables |
| `add_tests.py` | Appends integration test stubs |
| `add_telemetry.py` | Adds `libs/telemetry_stub.py` if absent |
| `add_database_support.py` | Adds `libs/sqlite_stub.py` if absent |

---

## Code Styles

| Style | Description |
|---|---|
| `PEP8` | Standard Python formatting (default) |
| `compact` | Blank lines between functions removed |
| `verbose` | Section separator comments before every hook |
| `enterprise` | Full docstrings, type hints, structured logging |

---

## Icon Styles (SVG)

| Style | Background | Appearance |
|---|---|---|
| `dark` | `#111116` | Double border rings, subtle grid lines, light text (default) |
| `neon` | `#07071a` | Radial glow, dual concentric rings, cross markers, centre dot |
| `pixel` | `#0d0e18` | 8 corner/edge pixel decorations, sharp square corners |
| `symbolic` | `#fafaf8` | Light theme, double dashed + solid border, inner grid lines |
| `gradient` | `#3C3489` | Linear gradient fill, highlight orb, translucent divider |

---

## UI Panel Layouts

| Layout | Description |
|---|---|
| `sidebar` | Vertical nav with active left-border indicator, output area fills remaining space |
| `tabs` | Horizontal tab bar (Run / Analyze / Config), underline active indicator |
| `modal` | Floating dialog with `backdrop-filter: blur` overlay, animated close button |
| `split` | Two-column grid: controls left (dark card), scrollable output right |

All layouts use **JetBrains Mono** (Google Fonts) with Consolas fallback, a 24 px dot-grid background texture, and a shared dark design system (`#0b0b14` base, `#6C63FF` accent).

---

## polsoft.ITS™ Plugin Standards

Every generated plugin complies with the full polsoft.ITS™ standard:

- ✅ `manifest.yaml` with `name`, `id`, `version`, `hooks`, `permissions`, `panels`
- ✅ `icons/` with minimum 2 SVG variants (5 generated)
- ✅ `README.txt` with description
- ✅ Author metadata in every file header (`name`, `company`, `email`, `github`, `copyright`)
- ✅ polsoft.ITS™ branding and copyright in all generated file types (`.py`, `.yaml`, `.md`, `.css`, `.html`, `.txt`, `.ps1`, `.bat`)
- ✅ Correct folder structure per profile
- ✅ pytest test suite (advanced+)
- ✅ `integrity.json` with SHA-256
- ✅ `plugin-info.json` API manifest

---

## Changelog

### v4.3.0

- **Dark GUI theme** — full migration from light (`#f5f4f0`) to deep dark (`#0d0d18`) across all 6 tabs; all fonts switched from Courier to Consolas
- **Window auto-sizing** — `update_idletasks()` + `geometry()` after build; `minsize(820, 580)` prevents content clipping
- **Widget–window integration** — all tab frames use `grid(sticky="nsew")` with `columnconfigure/rowconfigure weight=1`; notebook fills window fully
- **About tab redesign** — replaced scrollable `tk.Text` with centred label grid; all content visible without scrolling; language-aware key labels (PL/EN)
- **SVG icon redesign** — all 5 styles redrawn: `neon` adds radial gradient + cross markers; `pixel` has 8 decorations; `symbolic` double-border + grid; `gradient` uses `linearGradient`; `dark` adds inner grid lines
- **Panel CSS v2** — JetBrains Mono font, 24 px dot-grid background texture, `glassmorphism` modal (`backdrop-filter: blur`), 4 px custom scrollbar, button `transition` + `transform` on active, sidebar active-item left border
- **Author metadata completeness** — `hdr()` now injects `email` + `github` into `.md`, `.css`, `.txt`, `.ps1/.bat/.sh` headers; `LANG["about_body"]` refactored to use `AUTHOR_META` constants

### v4.2.0

- **Jinja2 template system** — `gen_j2_templates`, `validate_template`, `generate_from_template`, `render_j2` (with fallback)
- **`verify_integrity_on_disk()`** — SHA-256 tamper detection on any plugin folder
- **SHA-256 improvements** — `algorithm` field in all hash entries, explicit UTF-8 encoding, `_file_hashes()` helper
- **CLI** — 8 commands, `--json` output, `--no-validate` flag
- **Templates GUI tab** — generate, validate, and test templates from within the GUI
- **Integrity Verify button** in Validator tab
- **Lazy tkinter import** — CLI works without a display or tkinter install
- Fix: `App` class Windows compatibility (`TypeError: __bases__ assignment`)
- Fix: `manifest.yaml` YAML indentation bug (replaced `textwrap.dedent` + f-string with explicit `"\n".join`)

### v4.1.0

- `validate_plugin()` — 10-area full plugin validator
- `diagnostics/plugin_report.json` — structured error/warning report
- `REQUIRED_STRUCTURE`, `PROFILES_WITH_UI` — eliminated magic strings
- Auto-validation after generation (`opt_autovalidate`)
- Validator GUI tab: manifest section + full plugin folder section
- SHA-256 verify button

### v4.0.0

- 10 plugin profiles (added wizard, telemetry, database, network)
- 4 test files per plugin (test_load, test_commands, test_ui, test_config)
- `selftest.py` standalone runner
- `integrity.json` SHA-256 + MD5
- `update.json` auto-update checker
- Code styles: PEP8 / compact / verbose / enterprise
- UI layouts: sidebar / tabs / modal / split
- Meta-plugin system (`generator_plugins/`)
- Wizard mode GUI tab
- 5 SVG icon variants
- Bilingual PL/EN interface

---

## Project Information

| | |
|---|---|
| **Developer** | Sebastian Januchowski |
| **Company** | polsoft.ITS™ Group |
| **Email** | polsoft.its@fastservice.com |
| **GitHub** | [github.com/seb07uk](https://github.com/seb07uk) |
| **License** | MIT |
| **Copyright** | 2026© Sebastian Januchowski & polsoft.ITS™ |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure all existing profiles pass validation (`errors=0, warnings=0`) before submitting.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
```

---

*Generated with polsoft.ITS™ Plugin Generator v4.3.0*
