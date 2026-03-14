━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  polsoft.ITS™ Plugin Generator  v4.3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Developer:  Sebastian Januchowski
  Company:    polsoft.ITS™ Group
  Email:      polsoft.its@fastservice.com
  GitHub:     https://github.com/seb07uk
  2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DESCRIPTION
───────────
  Portable single-file developer tool for generating complete plugin
  packages for the polsoft.ITS™ Script Editor.
  No installation required. Runs with Python 3.8+ out of the box.

QUICK START
───────────
  GUI mode:
    python plugin_generator_5.py

  CLI — generate a plugin:
    python plugin_generator_5.py --generate MyPlugin --profile advanced --out ./output

  CLI — list all profiles:
    python plugin_generator_5.py --list-profiles

  CLI — validate a plugin:
    python plugin_generator_5.py --validate-plugin ./MyPlugin

  CLI — verify SHA-256 integrity:
    python plugin_generator_5.py --verify-integrity ./MyPlugin

OPTIONAL DEPENDENCIES
─────────────────────
  pip install pyyaml jinja2
  (without them the tool still works — reduced YAML validation and template rendering)

PROFILES  (10 total)
────────────────────
  minimal    advanced    enterprise    ui-heavy    analysis
  terminal   wizard      telemetry     database    network

WHAT GETS GENERATED
────────────────────
  manifest.yaml  main.py  README.txt  CHANGELOG.md  requirements.txt
  integrity.json  plugin-info.json  update.json  .plugin-manifest.yaml
  install.ps1 / install.bat  config/  icons/ (5 SVG variants)
  ui/ (advanced+ profiles)  libs/  tests/ (4 pytest files)
  selftest.py  diagnostics/  generator_plugins/

GUI TABS
────────
  Generator · Wizard · Templates · Options · Validator · About

CLI COMMANDS
────────────
  --gui                           Launch GUI
  --list-profiles                 Show available profiles
  --list-templates [DIR]          Show available templates
  --generate NAME --profile P     Generate plugin
  --test-template PROFILE [DIR]   Test a template
  --validate MANIFEST             Validate manifest.yaml
  --validate-plugin DIR           Full plugin validation (10 areas)
  --verify-integrity DIR          SHA-256 integrity check
  --json                          JSON output
  --no-validate                   Skip post-generation validation

CHANGELOG
─────────
  v4.3.0  Deep dark GUI theme · Consolas font · Window auto-sizing ·
          About tab redesign (no scroll) · SVG icon redesign ·
          Panel CSS v2 (JetBrains Mono, glassmorphism) ·
          Complete author metadata in all generated file headers

  v4.2.0  Jinja2 template system · verify_integrity_on_disk() ·
          CLI 8 commands · Templates GUI tab

  v4.1.0  validate_plugin() 10-area validator · auto-validation

  v4.0.0  10 profiles · meta-plugin system · Wizard GUI · 5 SVG icons ·
          PL/EN bilingual interface

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
