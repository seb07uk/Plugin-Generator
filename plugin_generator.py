#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
polsoft.ITS™ Plugin Generator v4.2.0 — GUI portable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Programista:  Sebastian Januchowski
Firma:        polsoft.ITS™ Group
Email:        polsoft.its@fastservice.com
GitHub:       https://github.com/seb07uk
2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nowe w v4.0.0:
  • Profile: +wizard, +telemetry, +database, +network (10 profili łącznie)
  • Rozbudowane testy: test_load / test_commands / test_ui / test_config
  • selftest.py — wbudowany self-test runner
  • integrity.json — SHA-256 + MD5 wszystkich plików
  • update.json — wersja pluginu / auto-update checker
  • manifest_report.json — szczegółowy raport walidacji
  • Profile kodu: PEP8 / compact / verbose / enterprise
  • Layout panelu UI: sidebar / tabs / modal / split
  • Meta-plugin system (generator_plugins/)
  • Wizard mode — interaktywny kreator (zakładka GUI)
  • 5 wariantów SVG na plugin (plugin/panel/toolbar/dark/symbolic)
  • Pełna integracja PL/EN

Nowe w v4.1.0:
  • validate_plugin() — pełny walidator pluginu (10 obszarów kontroli):
      manifest.yaml · main.py · struktura folderów · UI (HTML/CSS) ·
      config/default.json · ikony SVG · plugin-info.json · integrity.json ·
      pliki libs per profil · metadane autora
  • diagnostics/plugin_report.json — raport w formacie {errors, warnings}
  • Auto-walidacja po generacji (opcja opt_autovalidate)
  • Zakładka Walidator — sekcja „Waliduj cały plugin" (folder browser)
  • REQUIRED_STRUCTURE — słownik struktury per profil
  • PROFILES_WITH_UI — stały zbiór profili z panelem UI

Nowe w v4.2.0:
  • System szablonów Jinja2 (templates/ + pliki .j2 + template.json)
      render_j2() — renderer bez zewn. zależności (fallback regex), + Jinja2
      gen_j2_templates() — generuje pliki .j2 dla każdego profilu
      gen_template_json() — generuje template.json per profil
      generate_from_template() — renderuje szablon → gotowy plugin
  • validate_template() — walidator szablonu → diagnostics/template_report.json
      sprawdza: pliki .j2 · zmienne · template.json · manifest.yaml.j2
  • verify_integrity_on_disk() — weryfikacja SHA-256 po zapisie na dysk
      porównuje hashes z integrity.json z faktyczną zawartością plików
  • SHA-256: pole algorithm, encoding UTF-8 jawnie, hash pliku po write
  • CLI: --test-template · --generate · --validate · --validate-plugin
        --verify-integrity · --list-profiles · --list-templates
  • Zakładka GUI „Templates" — przeglądarka/generator/walidator szablonów
  • TEMPLATE_TYPES, TEMPLATE_VARS, J2_REQUIRED_FILES stałe

Użycie CLI:
  python plugin_generator_5.py --gui                         # tryb GUI
  python plugin_generator_5.py --list-profiles               # lista profili
  python plugin_generator_5.py --list-templates [DIR]        # lista szablonów
  python plugin_generator_5.py --generate NAME --profile P   # generuj
  python plugin_generator_5.py --test-template PROFILE [DIR] # testuj szablon
  python plugin_generator_5.py --validate MANIFEST.yaml      # waliduj manifest
  python plugin_generator_5.py --validate-plugin PLUGIN_DIR  # waliduj plugin
  python plugin_generator_5.py --verify-integrity PLUGIN_DIR # weryfikuj SHA-256
"""

import os, sys, json, hashlib, zipfile, textwrap, re, string, argparse
from pathlib import Path
from datetime import datetime

try:
    import yaml
    YAML_OK = True
except ImportError:
    YAML_OK = False

try:
    import jinja2
    JINJA2_OK = True
except ImportError:
    JINJA2_OK = False

# ── Tkinter: optional — only needed for GUI mode ──────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TK_OK = True
except ImportError:
    tk = ttk = messagebox = filedialog = None  # type: ignore
    TK_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

VERSION = "4.2.0"
BRAND   = "polsoft.ITS™ Script Editor"

AUTHOR_META = {
    "name":    "Sebastian Januchowski",
    "company": "polsoft.ITS™ Group",
    "email":   "polsoft.its@fastservice.com",
    "github":  "https://github.com/seb07uk",
    "year":    "2026",
    "copy":    "2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.",
}

PROFILES = {
    "minimal":    {"pl":"Minimal",    "en":"Minimal"},
    "advanced":   {"pl":"Advanced",   "en":"Advanced"},
    "enterprise": {"pl":"Enterprise", "en":"Enterprise"},
    "ui-heavy":   {"pl":"UI-Heavy",   "en":"UI-Heavy"},
    "analysis":   {"pl":"Analysis",   "en":"Analysis"},
    "terminal":   {"pl":"Terminal",   "en":"Terminal"},
    "wizard":     {"pl":"Wizard",     "en":"Wizard"},
    "telemetry":  {"pl":"Telemetry",  "en":"Telemetry"},
    "database":   {"pl":"Database",   "en":"Database"},
    "network":    {"pl":"Network",    "en":"Network"},
}

ICON_STYLES  = ["neon", "pixel", "symbolic", "gradient", "dark"]
CODE_STYLES  = ["PEP8", "compact", "verbose", "enterprise"]
UI_LAYOUTS   = ["sidebar", "tabs", "modal", "split"]

HOOKS_BY_PROFILE = {
    "minimal":    ["onLoad","onCommand"],
    "advanced":   ["onLoad","onUnload","onEditorReady","onFileOpen","onFileSave","onCommand","onSettingsChanged"],
    "enterprise": ["onLoad","onUnload","onEditorReady","onFileOpen","onFileSave","onCommand","onSettingsChanged","onEvent","onError","onTelemetry"],
    "ui-heavy":   ["onLoad","onUnload","onEditorReady","onCommand","onThemeChange","onPanelResize"],
    "analysis":   ["onLoad","onFileOpen","onFileSave","onCommand","onAnalysisRequest","onDiagnostic"],
    "terminal":   ["onLoad","onCommand","onTerminalInput","onTerminalOutput","onProcessStart","onProcessEnd"],
    "wizard":     ["onLoad","onWizardStep","onWizardComplete","onWizardCancel","onCommand"],
    "telemetry":  ["onLoad","onUnload","onTelemetry","onMetric","onEvent","onError","onCommand"],
    "database":   ["onLoad","onUnload","onDbConnect","onDbQuery","onDbError","onDbClose","onCommand"],
    "network":    ["onLoad","onUnload","onRequest","onResponse","onError","onTimeout","onCommand"],
}

PERMS_BY_PROFILE = {
    "minimal":    ["editor:read-write"],
    "advanced":   ["editor:full","filesystem:rw","network:restricted"],
    "enterprise": ["editor:full","filesystem:rw","network:full","terminal:allowed","diagnostics:full"],
    "ui-heavy":   ["editor:full","filesystem:rw"],
    "analysis":   ["editor:full","filesystem:rw"],
    "terminal":   ["editor:full","filesystem:rw","terminal:allowed"],
    "wizard":     ["editor:read-write"],
    "telemetry":  ["editor:full","network:full","diagnostics:full"],
    "database":   ["editor:full","filesystem:rw","network:restricted","db:rw"],
    "network":    ["editor:full","network:full"],
}

# Required folder/file structure per profile (trailing "/" = directory)
REQUIRED_STRUCTURE = {
    "minimal":    ["manifest.yaml","main.py","icons/"],
    "advanced":   ["manifest.yaml","main.py","ui/","libs/","config/","icons/"],
    "enterprise": ["manifest.yaml","main.py","ui/","libs/","config/","icons/",
                   "telemetry/","diagnostics/"],
    "ui-heavy":   ["manifest.yaml","main.py","ui/","libs/","config/","icons/"],
    "analysis":   ["manifest.yaml","main.py","ui/","libs/","config/","icons/"],
    "terminal":   ["manifest.yaml","main.py","libs/","config/","icons/"],
    "wizard":     ["manifest.yaml","main.py","libs/","config/","icons/"],
    "telemetry":  ["manifest.yaml","main.py","libs/","config/","icons/"],
    "database":   ["manifest.yaml","main.py","libs/","config/","icons/"],
    "network":    ["manifest.yaml","main.py","libs/","config/","icons/"],
}

# Profiles that generate a UI panel
PROFILES_WITH_UI = {"advanced","enterprise","ui-heavy","analysis"}

# ── Template system constants ──────────────────────────────────────────────────

# All supported template types (matches profile names + "custom")
TEMPLATE_TYPES = list(PROFILES.keys()) + ["custom"]

# Jinja2 / render_j2 variables available in every .j2 template
TEMPLATE_VARS = [
    "name", "plugin_id", "description", "author", "version",
    "brand", "year", "ui_style", "hooks", "commands", "panels",
    "license", "profile", "company", "email", "github", "copyright",
    "code_style", "ui_layout", "icon_style",
    "generated", "generator", "permissions",
]

# Required .j2 files every template must have
J2_REQUIRED_FILES = ["manifest.yaml.j2", "main.py.j2", "README.txt.j2"]

# Optional but expected files per template (warning if absent)
J2_OPTIONAL_FILES = {
    "advanced":   ["ui/panel.html.j2","ui/panel.css.j2","libs/helper.py.j2",
                   "config/default.json.j2","icons/plugin.svg.j2"],
    "enterprise": ["ui/panel.html.j2","ui/panel.css.j2","libs/helper.py.j2",
                   "libs/container.py.j2","libs/telemetry.py.j2",
                   "config/default.json.j2","icons/plugin.svg.j2"],
    "ui-heavy":   ["ui/panel.html.j2","ui/panel.css.j2","libs/theme.py.j2",
                   "config/default.json.j2","icons/plugin.svg.j2"],
    "analysis":   ["ui/panel.html.j2","ui/panel.css.j2","libs/analyzer.py.j2",
                   "libs/reporter.py.j2","config/default.json.j2","icons/plugin.svg.j2"],
    "terminal":   ["libs/shell.py.j2","config/default.json.j2","icons/plugin.svg.j2"],
    "wizard":     ["libs/wizard_engine.py.j2","config/default.json.j2","icons/plugin.svg.j2"],
    "telemetry":  ["libs/telemetry.py.j2","libs/metrics.py.j2",
                   "config/default.json.j2","icons/plugin.svg.j2"],
    "database":   ["libs/db.py.j2","config/default.json.j2","icons/plugin.svg.j2"],
    "network":    ["libs/network.py.j2","config/default.json.j2","icons/plugin.svg.j2"],
    "minimal":    ["config/default.json.j2","icons/plugin.svg.j2"],
}

# ══════════════════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ══════════════════════════════════════════════════════════════════════════════

LANG = {
    "pl": {
        "title":         "polsoft.ITS™ Generator Pluginów",
        "subtitle":      f"Script Editor · narzędzie deweloperskie v{VERSION}",
        "tab_gen":       "Generator",
        "tab_wizard":    "Wizard",
        "tab_tmpl":      "Szablony",
        "tab_opts":      "Opcje",
        "tab_valid":     "Walidator",
        "tab_about":     "O programie",
        "plugin_name":   "Nazwa pluginu",
        "plugin_id":     "ID pluginu",
        "author":        "Autor",
        "license":       "Licencja",
        "description":   "Opis",
        "profile":       "Profil",
        "icon_style":    "Styl ikon SVG",
        "code_style":    "Styl kodu",
        "ui_layout":     "Layout panelu UI",
        "out_dir":       "Katalog wyjściowy",
        "browse":        "Przeglądaj...",
        "generate":      "✦ Generuj plugin",
        "build_zip":     "📦 Buduj ZIP",
        "open_dir":      "Otwórz folder",
        "copy_btn":      "Kopiuj",
        "copied":        "Skopiowano!",
        "files_label":   "Wygenerowane pliki:",
        "preview":       "Podgląd:",
        "lang_btn":      "EN",
        "opts_extras":   "Dodatkowe pliki",
        "opt_tests":     "Testy pytest (4 pliki)",
        "opt_selftest":  "selftest.py (wbudowany tester)",
        "opt_changelog": "CHANGELOG.md",
        "opt_reqs":      "requirements.txt",
        "opt_install":   "Skrypty instalacyjne (.ps1 + .bat)",
        "opt_diag":      "Diagnostics/ (structure + hashes + report)",
        "opt_integrity": "integrity.json (SHA-256 wszystkich plików)",
        "opt_update":    "update.json (auto-update checker)",
        "opt_apimanif":  "plugin-info.json (API manifest)",
        "opt_pmmanif":   ".plugin-manifest.yaml (Plugin Manager)",
        "opt_metaplug":  "generator_plugins/ (meta-plugin system)",
        "valid_path":        "Ścieżka do manifest.yaml:",
        "valid_browse":      "Przeglądaj...",
        "validate":          "✔ Waliduj manifest",
        "valid_folder_lbl":  "Ścieżka do folderu pluginu:",
        "valid_folder_btn":  "Folder...",
        "validate_plugin":   "✦ Waliduj cały plugin",
        "opt_autovalidate":  "Auto-walidacja po generacji",
        "tmpl_dir_lbl":      "Katalog szablonów (templates/):",
        "tmpl_dir_btn":      "Przeglądaj...",
        "tmpl_profile_lbl":  "Typ szablonu:",
        "tmpl_gen_btn":      "✦ Generuj pliki .j2 szablonu",
        "tmpl_valid_btn":    "✔ Waliduj szablon",
        "tmpl_test_btn":     "▶ Testuj szablon (generuj plugin)",
        "tmpl_out_lbl":      "Katalog wyjściowy testu:",
        "tmpl_status_ok":    "Szablon OK",
        "tmpl_status_err":   "Błędy szablonu",
        "tmpl_jinja2_tip":   "Tip: pip install jinja2  — pełny renderer Jinja2",
        "tmpl_no_j2":        "Brak plików .j2 w wybranym katalogu.",
        "integrity_verify":  "⚙ Weryfikuj SHA-256 na dysku",
        "wiz_title":     "Kreator interaktywny",
        "wiz_step1":     "Krok 1: Podstawowe dane",
        "wiz_step2":     "Krok 2: Profil i styl",
        "wiz_step3":     "Krok 3: Hooki i uprawnienia",
        "wiz_step4":     "Krok 4: Potwierdzenie",
        "wiz_next":      "Dalej →",
        "wiz_back":      "← Wstecz",
        "wiz_finish":    "✦ Generuj",
        "err_title":     "Błąd",
        "success_msg":   "Plugin wygenerowany pomyślnie!",
        "zip_success":   "ZIP zbudowany!",
        "about_body": (
            f"polsoft.ITS™ Plugin Generator v{VERSION}\n\n"
            f"Programista:\n{AUTHOR_META['name']}\n\n"
            f"Firma:\n{AUTHOR_META['company']}\n\n"
            f"Kontakt:\n{AUTHOR_META['email']}\n\n"
            f"GitHub:\n{AUTHOR_META['github']}\n\n"
            f"{AUTHOR_META['copy']}\n"
            "Wszelkie prawa zastrzeżone."
        ),
    },
    "en": {
        "title":         "polsoft.ITS™ Plugin Generator",
        "subtitle":      f"Script Editor · developer tool v{VERSION}",
        "tab_gen":       "Generator",
        "tab_wizard":    "Wizard",
        "tab_tmpl":      "Templates",
        "tab_opts":      "Options",
        "tab_valid":     "Validator",
        "tab_about":     "About",
        "plugin_name":   "Plugin name",
        "plugin_id":     "Plugin ID",
        "author":        "Author",
        "license":       "License",
        "description":   "Description",
        "profile":       "Profile",
        "icon_style":    "SVG icon style",
        "code_style":    "Code style",
        "ui_layout":     "UI panel layout",
        "out_dir":       "Output directory",
        "browse":        "Browse...",
        "generate":      "✦ Generate plugin",
        "build_zip":     "📦 Build ZIP",
        "open_dir":      "Open folder",
        "copy_btn":      "Copy",
        "copied":        "Copied!",
        "files_label":   "Generated files:",
        "preview":       "Preview:",
        "lang_btn":      "PL",
        "opts_extras":   "Extra files",
        "opt_tests":     "Pytest tests (4 files)",
        "opt_selftest":  "selftest.py (built-in test runner)",
        "opt_changelog": "CHANGELOG.md",
        "opt_reqs":      "requirements.txt",
        "opt_install":   "Install scripts (.ps1 + .bat)",
        "opt_diag":      "Diagnostics/ (structure + hashes + report)",
        "opt_integrity": "integrity.json (SHA-256 all files)",
        "opt_update":    "update.json (auto-update checker)",
        "opt_apimanif":  "plugin-info.json (API manifest)",
        "opt_pmmanif":   ".plugin-manifest.yaml (Plugin Manager)",
        "opt_metaplug":  "generator_plugins/ (meta-plugin system)",
        "valid_path":        "Path to manifest.yaml:",
        "valid_browse":      "Browse...",
        "validate":          "✔ Validate manifest",
        "valid_folder_lbl":  "Path to plugin folder:",
        "valid_folder_btn":  "Folder...",
        "validate_plugin":   "✦ Validate full plugin",
        "opt_autovalidate":  "Auto-validate after generation",
        "tmpl_dir_lbl":      "Templates directory (templates/):",
        "tmpl_dir_btn":      "Browse...",
        "tmpl_profile_lbl":  "Template type:",
        "tmpl_gen_btn":      "✦ Generate .j2 template files",
        "tmpl_valid_btn":    "✔ Validate template",
        "tmpl_test_btn":     "▶ Test template (generate plugin)",
        "tmpl_out_lbl":      "Test output directory:",
        "tmpl_status_ok":    "Template OK",
        "tmpl_status_err":   "Template errors",
        "tmpl_jinja2_tip":   "Tip: pip install jinja2  — full Jinja2 renderer",
        "tmpl_no_j2":        "No .j2 files found in selected directory.",
        "integrity_verify":  "⚙ Verify SHA-256 on disk",
        "wiz_title":     "Interactive Wizard",
        "wiz_step1":     "Step 1: Basic info",
        "wiz_step2":     "Step 2: Profile & style",
        "wiz_step3":     "Step 3: Hooks & permissions",
        "wiz_step4":     "Step 4: Confirm",
        "wiz_next":      "Next →",
        "wiz_back":      "← Back",
        "wiz_finish":    "✦ Generate",
        "err_title":     "Error",
        "success_msg":   "Plugin generated successfully!",
        "zip_success":   "ZIP built!",
        "about_body": (
            f"polsoft.ITS™ Plugin Generator v{VERSION}\n\n"
            f"Developer:\n{AUTHOR_META['name']}\n\n"
            f"Company:\n{AUTHOR_META['company']}\n\n"
            f"Contact:\n{AUTHOR_META['email']}\n\n"
            f"GitHub:\n{AUTHOR_META['github']}\n\n"
            f"{AUTHOR_META['copy']}\n"
            "All rights reserved."
        ),
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  FILE HEADER GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def hdr(ext, name, pid, author, desc, code_style="PEP8"):
    m  = AUTHOR_META
    d  = datetime.now().strftime("%Y-%m-%d")
    g  = f"polsoft.ITS™ Plugin Generator v{VERSION}"
    sep = "─" * 58

    if ext == ".py":
        style_tag = f"  Code style: {code_style}" if code_style != "PEP8" else ""
        lines = [
            "# -*- coding: utf-8 -*-",
            f"# {sep}",
            f"#  {name}  |  {pid}",
            f"#  {desc}",
            f"#  Generated: {d} by {g}",
        ]
        if style_tag:
            lines.append(f"#{style_tag}")
        lines += [
            "#",
            f"#  Developer: {author}",
            f"#  Company:   {m['company']}",
            f"#  Email:     {m['email']}",
            f"#  GitHub:    {m['github']}",
            f"#  {m['copy']}",
            f"# {sep}",
            "",
        ]
        return "\n".join(lines)

    if ext in (".yaml", ".yml"):
        return (f"# {sep}\n# {name}  |  {pid}\n# {desc}\n"
                f"# Generated: {d} by {g}\n"
                f"# Developer: {author}  |  {m['company']}\n"
                f"# {m['email']}  |  {m['github']}\n"
                f"# {m['copy']}\n# {sep}\n")
    if ext == ".md":
        return (f"<!-- {sep}\n"
                f"     {name}  |  {pid}\n"
                f"     Developer: {author}  |  {m['company']}\n"
                f"     Email:     {m['email']}\n"
                f"     GitHub:    {m['github']}\n"
                f"     Generated: {d} by {g}\n"
                f"     {m['copy']}\n"
                f"     {sep} -->\n")
    if ext == ".html":
        return (f"<!--\n  {name}  |  {pid}\n  Developer: {author} | {m['company']}\n"
                f"  {m['email']}  |  {m['github']}\n  Generated: {d}\n  {m['copy']}\n-->\n")
    if ext == ".css":
        return (f"/*\n"
                f" * {name} — styles\n"
                f" * Developer: {author}  |  {m['company']}\n"
                f" * Email:     {m['email']}\n"
                f" * GitHub:    {m['github']}\n"
                f" * Generated: {d} by {g}\n"
                f" * {m['copy']}\n"
                f" */\n")
    if ext in (".ps1", ".bat", ".sh"):
        return (f"# {sep}\n"
                f"# {name} installer\n"
                f"# Developer: {author}  |  {m['company']}\n"
                f"# Email:     {m['email']}\n"
                f"# GitHub:    {m['github']}\n"
                f"# {m['copy']}\n"
                f"# {sep}\n")
    if ext == ".txt":
        return (f"{sep}\n"
                f"  {name}\n"
                f"  Developer: {author}  |  {m['company']}\n"
                f"  Email:     {m['email']}\n"
                f"  GitHub:    {m['github']}\n"
                f"  {m['copy']}\n"
                f"{sep}\n")
    return ""

# ══════════════════════════════════════════════════════════════════════════════
#  SVG ICON GENERATOR  (5 variants per plugin)
# ══════════════════════════════════════════════════════════════════════════════

_SVG_STYLES = {
    "neon":     {"bg":"#07071a","rx":"8","fc":"#d4d0ff","fw":"bold",
                 "deco":(
                     '<defs>'
                     '<radialGradient id="ng" cx="50%" cy="50%" r="50%">'
                     '<stop offset="0%" stop-color="#534AB7" stop-opacity="0.35"/>'
                     '<stop offset="100%" stop-color="#534AB7" stop-opacity="0"/>'
                     '</radialGradient>'
                     '</defs>'
                     '<rect width="32" height="32" rx="8" fill="url(#ng)"/>'
                     '<circle cx="16" cy="16" r="13" fill="none" stroke="#7F77DD" stroke-width="0.6" stroke-dasharray="2 3" opacity="0.6"/>'
                     '<circle cx="16" cy="16" r="9" fill="none" stroke="#AFA9EC" stroke-width="1.2" opacity="0.9"/>'
                     '<circle cx="16" cy="16" r="3" fill="#c9c5ff" opacity="0.7"/>'
                     '<line x1="16" y1="3" x2="16" y2="7" stroke="#AFA9EC" stroke-width="1" stroke-linecap="round" opacity="0.5"/>'
                     '<line x1="16" y1="25" x2="16" y2="29" stroke="#AFA9EC" stroke-width="1" stroke-linecap="round" opacity="0.5"/>'
                     '<line x1="3" y1="16" x2="7" y2="16" stroke="#AFA9EC" stroke-width="1" stroke-linecap="round" opacity="0.5"/>'
                     '<line x1="25" y1="16" x2="29" y2="16" stroke="#AFA9EC" stroke-width="1" stroke-linecap="round" opacity="0.5"/>'
                 )},
    "pixel":    {"bg":"#0d0e18","rx":"0","fc":"#AFA9EC","fw":"bold",
                 "deco":(
                     '<rect x="0" y="0" width="32" height="32" fill="#0d0e18"/>'
                     '<rect x="2" y="2" width="4" height="4" fill="#534AB7"/>'
                     '<rect x="26" y="2" width="4" height="4" fill="#534AB7"/>'
                     '<rect x="2" y="26" width="4" height="4" fill="#534AB7"/>'
                     '<rect x="26" y="26" width="4" height="4" fill="#534AB7"/>'
                     '<rect x="6" y="6" width="2" height="2" fill="#7F77DD" opacity="0.5"/>'
                     '<rect x="24" y="6" width="2" height="2" fill="#7F77DD" opacity="0.5"/>'
                     '<rect x="6" y="24" width="2" height="2" fill="#7F77DD" opacity="0.5"/>'
                     '<rect x="24" y="24" width="2" height="2" fill="#7F77DD" opacity="0.5"/>'
                     '<rect x="14" y="2" width="4" height="1" fill="#534AB7" opacity="0.4"/>'
                     '<rect x="14" y="29" width="4" height="1" fill="#534AB7" opacity="0.4"/>'
                     '<rect x="2" y="14" width="1" height="4" fill="#534AB7" opacity="0.4"/>'
                     '<rect x="29" y="14" width="1" height="4" fill="#534AB7" opacity="0.4"/>'
                 )},
    "symbolic": {"bg":"#fafaf8","rx":"6","fc":"#26215C","fw":"600",
                 "deco":(
                     '<rect x="3" y="3" width="26" height="26" rx="5" fill="none" stroke="#AFA9EC" stroke-width="0.8" stroke-dasharray="3 2"/>'
                     '<rect x="6" y="6" width="20" height="20" rx="3" fill="none" stroke="#534AB7" stroke-width="1.2"/>'
                     '<line x1="6" y1="14" x2="26" y2="14" stroke="#534AB7" stroke-width="0.6" opacity="0.4"/>'
                     '<line x1="6" y1="18" x2="26" y2="18" stroke="#534AB7" stroke-width="0.6" opacity="0.4"/>'
                 )},
    "gradient": {"bg":"#3C3489","rx":"8","fc":"#ffffff","fw":"bold",
                 "deco":(
                     '<defs>'
                     '<linearGradient id="gg" x1="0" y1="0" x2="1" y2="1">'
                     '<stop offset="0%" stop-color="#7F77DD"/>'
                     '<stop offset="100%" stop-color="#3C3489"/>'
                     '</linearGradient>'
                     '</defs>'
                     '<rect width="32" height="32" rx="8" fill="url(#gg)"/>'
                     '<circle cx="26" cy="6" r="10" fill="white" opacity="0.07"/>'
                     '<rect x="1" y="1" width="30" height="30" rx="7" fill="none" stroke="white" stroke-width="0.6" opacity="0.25"/>'
                     '<line x1="0" y1="22" x2="32" y2="22" stroke="white" stroke-width="0.5" opacity="0.12"/>'
                 )},
    "dark":     {"bg":"#111116","rx":"7","fc":"#e8e6ff","fw":"500",
                 "deco":(
                     '<rect x="1" y="1" width="30" height="30" rx="6" fill="none" stroke="#534AB7" stroke-width="0.8"/>'
                     '<rect x="4" y="4" width="24" height="24" rx="4" fill="none" stroke="#3C3489" stroke-width="0.5" opacity="0.6"/>'
                     '<line x1="4" y1="12" x2="28" y2="12" stroke="#534AB7" stroke-width="0.4" opacity="0.35"/>'
                     '<line x1="4" y1="20" x2="28" y2="20" stroke="#534AB7" stroke-width="0.4" opacity="0.35"/>'
                 )},
}

def gen_svg(name, pid, author, style, variant="plugin"):
    m  = AUTHOR_META
    d  = datetime.now().strftime("%Y-%m-%d")
    letter = name[0].upper() if name else "P"
    s  = _SVG_STYLES.get(style, _SVG_STYLES["dark"])
    label = f"{letter}{variant[0].upper()}" if variant != "plugin" else letter
    return (
        f'<!-- {name} | {variant} | {style} | {m["copy"]} | {d} -->\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">\n'
        f'  <rect width="32" height="32" rx="{s["rx"]}" fill="{s["bg"]}"/>\n'
        f'  {s["deco"]}\n'
        f'  <text x="16" y="21" text-anchor="middle" font-size="13" fill="{s["fc"]}"\n'
        f'        font-family="Consolas,monospace" font-weight="{s["fw"]}">{label}</text>\n'
        f'</svg>'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  UI PANEL HTML/CSS — layout variants
# ══════════════════════════════════════════════════════════════════════════════

def gen_panel_html(name, pid, author, desc, layout="sidebar"):
    h = hdr(".html", name, pid, author, desc)
    layouts = {
        "sidebar": textwrap.dedent(f"""
            <div class="panel sidebar">
              <div class="panel-header"><h2>{name}</h2></div>
              <nav class="sidebar-nav">
                <button class="nav-btn active" onclick="api.command('{pid}.run')">▶ Run</button>
                <button class="nav-btn" onclick="api.command('{pid}.analyze')">⚙ Analyze</button>
                <button class="nav-btn" onclick="api.command('{pid}.config')">◈ Config</button>
              </nav>
              <div id="output" class="output"></div>
              <footer class="panel-footer">{AUTHOR_META['copy']}</footer>
            </div>
            <script>
            function appendOutput(msg) {{
              var el = document.getElementById('output');
              if (el) el.textContent += msg + '\\n';
            }}
            </script>"""),
        "tabs": textwrap.dedent(f"""
            <div class="panel tabs">
              <div class="tab-bar">
                <button class="tab active" onclick="showTab('run')">Run</button>
                <button class="tab" onclick="showTab('analyze')">Analyze</button>
                <button class="tab" onclick="showTab('config')">Config</button>
              </div>
              <div id="tab-run" class="tab-content active">
                <button onclick="api.command('{pid}.run')">▶ Run {name}</button>
                <div id="output" class="output"></div>
              </div>
              <div id="tab-analyze" class="tab-content">
                <button onclick="api.command('{pid}.analyze')">Analyze current file</button>
              </div>
              <div id="tab-config" class="tab-content">
                <p>Config panel — coming soon.</p>
              </div>
              <footer>{AUTHOR_META['copy']}</footer>
            </div>
            <script>
            function showTab(id) {{
              document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
              document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
              document.getElementById('tab-'+id).classList.add('active');
              event.target.classList.add('active');
            }}
            </script>"""),
        "modal": textwrap.dedent(f"""
            <div class="panel modal-panel">
              <div class="modal-trigger">
                <button onclick="openModal()">Open {name}</button>
              </div>
              <div id="modal" class="modal" style="display:none">
                <div class="modal-box">
                  <div class="modal-header">
                    <span>{name}</span>
                    <button class="close-btn" onclick="closeModal()">✕</button>
                  </div>
                  <div class="modal-body">
                    <button onclick="api.command('{pid}.run')">▶ Run</button>
                    <button onclick="api.command('{pid}.analyze')">⚙ Analyze</button>
                    <div id="output" class="output"></div>
                  </div>
                </div>
              </div>
              <footer>{AUTHOR_META['copy']}</footer>
            </div>
            <script>
            function openModal() {{ document.getElementById('modal').style.display='flex'; }}
            function closeModal() {{ document.getElementById('modal').style.display='none'; }}
            </script>"""),
        "split": textwrap.dedent(f"""
            <div class="panel split-panel">
              <div class="split-left">
                <h3>{name}</h3>
                <button onclick="api.command('{pid}.run')">▶ Run</button>
                <button onclick="api.command('{pid}.analyze')">⚙ Analyze</button>
              </div>
              <div class="split-right">
                <div id="output" class="output">Output appears here...</div>
              </div>
              <footer class="split-footer">{AUTHOR_META['copy']}</footer>
            </div>
            <script>
            function appendOutput(msg) {{
              var el = document.getElementById('output');
              if (el) el.textContent += msg + '\\n';
            }}
            </script>"""),
    }
    return h + layouts.get(layout, layouts["sidebar"]).strip()


def gen_panel_css(name, pid, author, layout="sidebar"):
    h = hdr(".css", name, pid, author, "Panel styles")
    base = textwrap.dedent("""
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        :root{
          --bg:#0b0b14;
          --bg2:#0f0f1c;
          --card:#13131f;
          --card2:#191928;
          --fg:#e8e6ff;
          --fg2:#b8b5d8;
          --muted:#6a6890;
          --accent:#6C63FF;
          --accent2:#534AB7;
          --accent3:#8B85FF;
          --border:#1e1e32;
          --border2:#2a2a42;
          --success:#1D9E75;
          --warn:#E8A020;
          --radius:6px;
          --shadow:0 2px 12px rgba(0,0,0,.5);
        }
        *{box-sizing:border-box;margin:0;padding:0}
        html,body{height:100%;overflow:hidden}
        body{
          background:var(--bg);
          color:var(--fg);
          font-family:'JetBrains Mono',Consolas,monospace;
          font-size:12px;
          line-height:1.5;
          background-image:
            linear-gradient(rgba(108,99,255,.03) 1px,transparent 1px),
            linear-gradient(90deg,rgba(108,99,255,.03) 1px,transparent 1px);
          background-size:24px 24px;
        }
        .panel{display:flex;flex-direction:column;height:100vh}
        .panel-header{
          padding:10px 14px 9px;
          background:var(--card);
          border-bottom:1px solid var(--border2);
          display:flex;align-items:center;gap:8px;
          background:linear-gradient(180deg,var(--card2) 0%,var(--card) 100%);
        }
        .panel-header::before{
          content:'◈';
          font-size:14px;
          color:var(--accent);
          flex-shrink:0;
        }
        h2,h3{
          font-size:13px;
          font-weight:600;
          color:var(--fg);
          letter-spacing:.4px;
          margin:0;
        }
        button{
          background:var(--accent2);
          color:var(--fg);
          border:none;
          padding:5px 12px;
          cursor:pointer;
          border-radius:var(--radius);
          font-family:inherit;
          font-size:11px;
          font-weight:500;
          letter-spacing:.3px;
          transition:background .15s,transform .1s,box-shadow .15s;
          box-shadow:0 1px 4px rgba(0,0,0,.35);
        }
        button:hover{background:var(--accent);box-shadow:0 2px 8px rgba(108,99,255,.4)}
        button:active{transform:translateY(1px)}
        button.secondary{
          background:transparent;
          border:1px solid var(--border2);
          color:var(--fg2);
        }
        button.secondary:hover{border-color:var(--accent2);color:var(--fg);background:rgba(108,99,255,.08)}
        .output,#output{
          flex:1;
          white-space:pre-wrap;
          word-break:break-all;
          font-size:11px;
          color:var(--fg2);
          background:var(--bg2);
          padding:10px 12px;
          overflow-y:auto;
          min-height:60px;
          border-top:1px solid var(--border);
          line-height:1.6;
        }
        .output::-webkit-scrollbar{width:4px}
        .output::-webkit-scrollbar-track{background:transparent}
        .output::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
        .output span.ok{color:var(--success)}
        .output span.warn{color:var(--warn)}
        .output span.err{color:#e05050}
        footer,.panel-footer,.split-footer{
          font-size:9px;
          color:var(--muted);
          padding:4px 12px;
          border-top:1px solid var(--border);
          background:var(--card);
          letter-spacing:.2px;
        }
        """)

    layout_css = {
        "sidebar": textwrap.dedent("""
            .sidebar-nav{
              display:flex;flex-direction:column;gap:3px;padding:8px;
              background:var(--card);border-bottom:1px solid var(--border);
            }
            .nav-btn{
              width:100%;text-align:left;
              background:transparent;
              color:var(--fg2);
              border:none;border-radius:var(--radius);
              padding:6px 10px;
              cursor:pointer;
              font-family:inherit;font-size:11px;font-weight:500;
              transition:background .12s,color .12s;
              display:flex;align-items:center;gap:7px;
            }
            .nav-btn:hover{background:rgba(108,99,255,.12);color:var(--fg)}
            .nav-btn.active{background:rgba(108,99,255,.18);color:var(--accent3);
                            border-left:2px solid var(--accent)}
            """),
        "tabs": textwrap.dedent("""
            .tab-bar{
              display:flex;background:var(--card);
              border-bottom:1px solid var(--border2);
              padding:0 4px;
              gap:2px;
            }
            .tab{
              background:transparent;color:var(--muted);
              border:none;border-bottom:2px solid transparent;
              padding:8px 14px;cursor:pointer;
              font-family:inherit;font-size:11px;font-weight:500;
              letter-spacing:.3px;
              transition:color .12s,border-color .12s;
              margin-bottom:-1px;
            }
            .tab.active{color:var(--accent3);border-bottom-color:var(--accent)}
            .tab:hover:not(.active){color:var(--fg2)}
            .tab-content{display:none;padding:12px}
            .tab-content.active{display:flex;flex-direction:column;gap:8px}
            """),
        "modal": textwrap.dedent("""
            .modal{
              position:fixed;inset:0;
              background:rgba(0,0,0,.72);
              backdrop-filter:blur(4px);
              display:flex;align-items:center;justify-content:center;z-index:100;
            }
            .modal-box{
              background:var(--card2);
              border:1px solid var(--border2);
              border-radius:10px;
              min-width:320px;max-width:90vw;
              box-shadow:0 8px 32px rgba(0,0,0,.6),
                         0 0 0 1px rgba(108,99,255,.15);
            }
            .modal-header{
              display:flex;justify-content:space-between;align-items:center;
              padding:12px 16px;
              border-bottom:1px solid var(--border);
              background:linear-gradient(180deg,rgba(108,99,255,.08) 0%,transparent 100%);
              border-radius:10px 10px 0 0;
            }
            .modal-body{padding:16px;display:flex;flex-direction:column;gap:10px}
            .close-btn{
              background:rgba(255,255,255,.06);color:var(--muted);
              border:1px solid var(--border);border-radius:4px;
              font-size:14px;cursor:pointer;padding:2px 7px;
              transition:background .12s,color .12s;
            }
            .close-btn:hover{background:rgba(224,80,80,.15);color:#e05050;border-color:#e05050}
            .modal-trigger{padding:12px}
            """),
        "split": textwrap.dedent("""
            .split-panel{
              display:grid;
              grid-template-columns:200px 1fr;
              grid-template-rows:1fr auto;
              height:100vh;
            }
            .split-left{
              padding:12px;
              display:flex;flex-direction:column;gap:8px;
              border-right:1px solid var(--border2);
              background:var(--card);
            }
            .split-left h3{
              font-size:11px;font-weight:600;
              color:var(--accent3);
              text-transform:uppercase;letter-spacing:.8px;
              padding-bottom:8px;
              border-bottom:1px solid var(--border);
              margin-bottom:2px;
            }
            .split-right{padding:12px;overflow:auto;background:var(--bg2)}
            .split-footer{grid-column:1/-1}
            """),
    }
    return h + base.strip() + "\n" + layout_css.get(layout, layout_css["sidebar"]).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN.PY — all 10 profiles
# ══════════════════════════════════════════════════════════════════════════════

def gen_main_py(name, pid, desc, author, profile, code_style="PEP8"):
    h = hdr(".py", name, pid, author, desc, code_style)

    # compact style strips blank lines between functions
    def fmt(code):
        if code_style == "compact":
            return re.sub(r'\n{2,}', '\n', code)
        if code_style == "verbose":
            return code.replace("def on", "\n\n# ──────────────────────────\ndef on")
        return code

    bodies = {
        "minimal": fmt(textwrap.dedent(f"""
            def onLoad(api):
                api.editor.showMessage("{name} loaded.", "info")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    api.editor.showMessage("{name} — executed.", "info")
            """)),
        "advanced": fmt(textwrap.dedent(f"""
            from libs.helper import analyze_text

            def onLoad(api):
                api.editor.showMessage("{name} Advanced loaded.", "info")
                api.diagnostics.log("{name} loaded.")

            def onUnload(api):
                api.diagnostics.log("{name} unloaded.")

            def onEditorReady(api):
                api.ui.createPanel("{pid}.panel", {{"title":"{name}","html":"ui/panel.html","css":"ui/panel.css"}})

            def onFileOpen(api, file):
                api.diagnostics.log(f"Open: {{file.getPath()}}")

            def onFileSave(api, file):
                api.diagnostics.log(f"Save: {{file.getPath()}}")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    api.editor.showMessage("{name} — RUN.", "info")
                if commandId == "{pid}.analyze":
                    api.ui.showDialog("Analysis", analyze_text(api.editor.getText()))

            def onSettingsChanged(api, settings):
                api.diagnostics.log("Settings changed.")
            """)),
        "enterprise": fmt(textwrap.dedent(f"""
            from libs.container import DIContainer
            from libs.events import EventBus
            from libs.telemetry import TelemetryCollector

            container = DIContainer()
            bus       = EventBus()
            telemetry = TelemetryCollector("{pid}")

            def onLoad(api):
                container.register("api", api)
                bus.subscribe("{pid}.run", lambda e: api.editor.showMessage("{name} Enterprise ready.", "info"))
                telemetry.start()
                api.diagnostics.log("{name} Enterprise loaded.")

            def onUnload(api):
                telemetry.flush()
                bus.clear()
                api.diagnostics.log("{name} Enterprise unloaded.")

            def onEditorReady(api):
                api.ui.createPanel("{pid}.panel", {{"title":"{name}","html":"ui/panel.html","css":"ui/panel.css"}})

            def onEvent(api, event):
                bus.emit(event.id, event)
                telemetry.record("event", event.id)

            def onError(api, error):
                api.diagnostics.error(f"Error: {{error}}")
                telemetry.record("error", str(error))

            def onTelemetry(api, metrics):
                telemetry.push(metrics)

            def onCommand(api, commandId, args):
                bus.emit(commandId, {{"args": args}})

            def onFileOpen(api, file):  api.diagnostics.log(f"Open: {{file.getPath()}}")
            def onFileSave(api, file):  api.diagnostics.log(f"Save: {{file.getPath()}}")
            def onSettingsChanged(api, s): api.diagnostics.log("Settings updated.")
            """)),
        "ui-heavy": fmt(textwrap.dedent(f"""
            from libs.theme import ThemeEngine
            _theme = ThemeEngine()

            def onLoad(api):
                _theme.init(api)
                api.editor.showMessage("{name} UI-Heavy loaded.", "info")

            def onUnload(api):
                _theme.destroy()

            def onEditorReady(api):
                api.ui.createPanel("{pid}.panel", {{"title":"{name}","html":"ui/panel.html","css":"ui/panel.css","width":320}})

            def onThemeChange(api, theme):
                _theme.apply(theme)

            def onPanelResize(api, size):
                api.diagnostics.log(f"Panel resized: {{size}}")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.open_panel": api.ui.showPanel("{pid}.panel")
                if commandId == "{pid}.toggle_theme": _theme.toggle(api)
            """)),
        "analysis": fmt(textwrap.dedent(f"""
            from libs.analyzer import CodeAnalyzer
            from libs.reporter import ReportBuilder
            _analyzer = CodeAnalyzer()
            _reporter = ReportBuilder()

            def onLoad(api):
                api.editor.showMessage("{name} Analysis engine ready.", "info")

            def onFileOpen(api, file):
                _analyzer.reset()

            def onFileSave(api, file):
                r = _analyzer.quick_scan(api.editor.getText())
                if r.has_warnings:
                    api.editor.showMessage(f"{{r.warning_count}} warning(s) found.", "warn")

            def onAnalysisRequest(api, req):
                api.ui.showDialog("Report", _reporter.build(_analyzer.full_scan(api.editor.getText())))

            def onDiagnostic(api, diag):
                api.diagnostics.log(f"Diagnostic: {{diag}}")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.analyze":
                    api.ui.showDialog("Analysis", str(_analyzer.full_scan(api.editor.getText())))
                if commandId == "{pid}.report":
                    api.ui.showDialog("Report", _reporter.summary())
                if commandId == "{pid}.clear":
                    _analyzer.reset()
                    api.editor.showMessage("Cleared.", "info")
            """)),
        "terminal": fmt(textwrap.dedent(f"""
            import subprocess
            from libs.shell import ShellRunner
            _shell = ShellRunner()

            def onLoad(api):
                api.editor.showMessage("{name} Terminal loaded.", "info")

            def onTerminalInput(api, line):
                _shell.feed(line)

            def onTerminalOutput(api, out):
                api.diagnostics.log(f"Out: {{out[:80]}}")

            def onProcessStart(api, process):
                api.diagnostics.log(f"Process started: {{process.pid}}")

            def onProcessEnd(api, process):
                api.diagnostics.log(f"Process ended: {{process.pid}} exit={{process.returncode}}")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.shell":
                    try:
                        out = subprocess.check_output(args.get("cmd","echo ok"), shell=True, text=True, timeout=10)
                        api.ui.showDialog("Shell", out)
                    except Exception as e:
                        api.editor.showMessage(f"Error: {{e}}", "error")
                if commandId == "{pid}.run_command":
                    api.editor.showMessage("{name} — running.", "info")
            """)),
        "wizard": fmt(textwrap.dedent(f"""
            from libs.wizard_engine import WizardEngine
            _wizard = WizardEngine("{pid}")

            def onLoad(api):
                api.editor.showMessage("{name} Wizard ready.", "info")
                _wizard.define_steps([
                    {{"id":"step1","title":"Welcome","fields":[{{"type":"text","label":"Name","key":"name"}}]}},
                    {{"id":"step2","title":"Config","fields":[{{"type":"choice","label":"Mode","key":"mode","options":["fast","safe","debug"]}}]}},
                    {{"id":"step3","title":"Confirm","type":"confirm"}},
                ])

            def onWizardStep(api, step, data):
                api.diagnostics.log(f"Wizard step: {{step}} data={{data}}")

            def onWizardComplete(api, result):
                api.editor.showMessage(f"Wizard complete: {{result.get('name','?')}}", "info")
                api.diagnostics.log(f"Wizard result: {{result}}")

            def onWizardCancel(api):
                api.editor.showMessage("Wizard cancelled.", "warn")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    _wizard.start(api)
            """)),
        "telemetry": fmt(textwrap.dedent(f"""
            from libs.telemetry import TelemetryCollector
            from libs.metrics import MetricsAggregator
            _tel  = TelemetryCollector("{pid}")
            _agg  = MetricsAggregator()

            def onLoad(api):
                _tel.start()
                api.editor.showMessage("{name} Telemetry active.", "info")

            def onUnload(api):
                _tel.flush()
                api.diagnostics.log("Telemetry flushed.")

            def onTelemetry(api, metrics):
                _tel.push(metrics)
                _agg.ingest(metrics)

            def onMetric(api, key, value):
                _agg.record(key, value)
                api.diagnostics.log(f"Metric {{key}}={{value}}")

            def onEvent(api, event):
                _tel.record("event", event.id)

            def onError(api, error):
                _tel.record("error", str(error))
                api.diagnostics.error(f"Telemetry error: {{error}}")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    report = _agg.summary()
                    api.ui.showDialog("Telemetry Report", report)
            """)),
        "database": fmt(textwrap.dedent(f"""
            from libs.db import DatabaseManager
            _db = DatabaseManager()

            def onLoad(api):
                api.editor.showMessage("{name} Database plugin loaded.", "info")

            def onUnload(api):
                _db.close_all()
                api.diagnostics.log("DB connections closed.")

            def onDbConnect(api, conn_info):
                try:
                    _db.connect(conn_info)
                    api.diagnostics.log(f"DB connected: {{conn_info.get('host','?')}}")
                except Exception as e:
                    api.editor.showMessage(f"DB connect error: {{e}}", "error")

            def onDbQuery(api, query, params=None):
                try:
                    result = _db.execute(query, params)
                    api.diagnostics.log(f"Query OK, rows={{len(result)}}")
                    return result
                except Exception as e:
                    api.editor.showMessage(f"Query error: {{e}}", "error")

            def onDbError(api, error):
                api.diagnostics.error(f"DB error: {{error}}")

            def onDbClose(api):
                _db.close_all()

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    api.ui.showDialog("DB Status", _db.status())
            """)),
        "network": fmt(textwrap.dedent(f"""
            from libs.network import NetworkClient
            _client = NetworkClient()

            def onLoad(api):
                api.editor.showMessage("{name} Network plugin loaded.", "info")

            def onUnload(api):
                _client.close()

            def onRequest(api, request):
                api.diagnostics.log(f"Request: {{request.method}} {{request.url}}")
                return _client.send(request)

            def onResponse(api, response):
                api.diagnostics.log(f"Response: {{response.status}} in {{response.elapsed_ms}}ms")

            def onError(api, error):
                api.diagnostics.error(f"Network error: {{error}}")

            def onTimeout(api, url, timeout_ms):
                api.editor.showMessage(f"Timeout: {{url}} ({{timeout_ms}}ms)", "warn")

            def onCommand(api, commandId, args):
                if commandId == "{pid}.run":
                    status = _client.ping(args.get("url","https://example.com"))
                    api.ui.showDialog("Network Status", str(status))
            """)),
    }
    return h + bodies.get(profile, bodies["minimal"]).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  MANIFEST YAML
# ══════════════════════════════════════════════════════════════════════════════

def gen_manifest_yaml(name, pid, desc, author, license_, profile):
    h = hdr(".yaml", name, pid, author, desc)
    m = AUTHOR_META
    hooks = HOOKS_BY_PROFILE.get(profile, ["onLoad","onCommand"])
    perms  = PERMS_BY_PROFILE.get(profile, ["editor:read-write"])
    ver = "1.0.0" if profile == "minimal" else "2.0.0"
    suffix = {"advanced":" Advanced","enterprise":" Enterprise","ui-heavy":" UI",
              "analysis":" Analysis","terminal":" Terminal","wizard":" Wizard",
              "telemetry":" Telemetry","database":" Database","network":" Network"}.get(profile,"")

    # Build hooks and permissions blocks with correct indentation
    hooks_block = "\n".join(f"  {hk}: true" for hk in hooks)
    perms_block  = "\n".join(f"  - {p}"     for p  in perms)

    # Panels block (only for profiles with UI panels)
    panels_lines: list[str] = []
    if profile in PROFILES_WITH_UI:
        panels_lines = [
            "",
            "panels:",
            f'  - id: "{pid}.panel"',
            f'    title: "{name}"',
            '    position: "right"',
            '    html: "ui/panel.html"',
            '    css: "ui/panel.css"',
        ]

    # Build manifest using explicit string joining (avoids textwrap.dedent + f-string multiline issue)
    lines = [
        f'name: "{name}{suffix}"',
        f'id: "{pid}"',
        f'version: "{ver}"',
        f'description: "{desc}"',
        f'profile: "{profile}"',
        "",
        "author:",
        f'  name: "{author}"',
        f'  company: "{m["company"]}"',
        f'  email: "{m["email"]}"',
        f'  github: "{m["github"]}"',
        f'license: "{license_}"',
        f'copyright: "{m["copy"]}"',
        "",
        "engine:",
        '  min_version: "1.0.0"',
        '  api_version: "1.0.0"',
        "",
        "hooks:",
        hooks_block,
        "",
        "commands:",
        f'  - id: "{pid}.run"',
        f'    title: "Run {name}"',
        '    shortcut: "Ctrl+Alt+R"',
    ] + panels_lines + [
        "",
        "permissions:",
        perms_block,
        "",
        "settings:",
        "  enabled: true",
        '  config_file: "config/default.json"',
    ]
    return h + "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
#  LIBRARY FILES  (profile-specific)
# ══════════════════════════════════════════════════════════════════════════════

def gen_helper_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Helpers",cs) + textwrap.dedent("""
        def analyze_text(text: str) -> str:
            lines = text.split("\\n")
            return (f"Lines: {len(lines)}\\nNon-empty: {sum(1 for l in lines if l.strip())}\\n"
                    f"Words: {len(text.split())}\\nChars: {len(text)}")

        def truncate(text: str, n: int = 200) -> str:
            return text[:n] + "..." if len(text) > n else text

        def sanitize(text: str) -> str:
            return text.strip().replace("\\t", "    ")
        """).strip()

def gen_container_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"DI Container",cs) + textwrap.dedent("""
        class DIContainer:
            def __init__(self): self._s = {}
            def register(self, name, inst): self._s[name] = inst
            def resolve(self, name):
                if name not in self._s: raise KeyError(f"Not registered: {name}")
                return self._s[name]
            def has(self, name): return name in self._s
        """).strip()

def gen_events_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Event Bus",cs) + textwrap.dedent("""
        from collections import defaultdict
        class EventBus:
            def __init__(self): self._h = defaultdict(list)
            def subscribe(self, eid, handler): self._h[eid].append(handler)
            def unsubscribe(self, eid, handler):
                self._h[eid] = [h for h in self._h[eid] if h != handler]
            def emit(self, eid, payload=None):
                for h in list(self._h.get(eid, [])):
                    try: h(payload)
                    except Exception as e: print(f"EventBus [{eid}]: {e}")
            def clear(self): self._h.clear()
        """).strip()

def gen_telemetry_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Telemetry Collector",cs) + textwrap.dedent("""
        import time
        from collections import defaultdict

        class TelemetryCollector:
            def __init__(self, plugin_id: str):
                self._pid = plugin_id
                self._started = None
                self._records = []
                self._counters = defaultdict(int)

            def start(self):
                self._started = time.time()

            def record(self, kind: str, value):
                self._records.append({"kind": kind, "value": value, "ts": time.time()})
                self._counters[kind] += 1

            def push(self, metrics):
                for k, v in (metrics.items() if isinstance(metrics, dict) else []):
                    self.record(k, v)

            def flush(self):
                count = len(self._records)
                self._records.clear()
                return count

            def summary(self) -> str:
                uptime = round(time.time() - self._started, 1) if self._started else 0
                lines = [f"Plugin: {self._pid}", f"Uptime: {uptime}s",
                         f"Records: {sum(self._counters.values())}"]
                for k, v in self._counters.items():
                    lines.append(f"  {k}: {v}")
                return "\\n".join(lines)
        """).strip()

def gen_metrics_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Metrics Aggregator",cs) + textwrap.dedent("""
        from collections import defaultdict

        class MetricsAggregator:
            def __init__(self):
                self._data = defaultdict(list)

            def ingest(self, metrics: dict):
                for k, v in metrics.items():
                    self._data[k].append(v)

            def record(self, key: str, value):
                self._data[key].append(value)

            def summary(self) -> str:
                if not self._data:
                    return "No metrics recorded."
                lines = ["Metrics Summary", "=" * 30]
                for k, vals in self._data.items():
                    avg = sum(vals) / len(vals) if vals else 0
                    lines.append(f"  {k}: count={len(vals)} avg={avg:.2f}")
                return "\\n".join(lines)
        """).strip()

def gen_wizard_engine_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Wizard Engine",cs) + textwrap.dedent("""
        class WizardEngine:
            def __init__(self, plugin_id: str):
                self._pid = plugin_id
                self._steps = []
                self._current = 0
                self._data = {}

            def define_steps(self, steps: list):
                self._steps = steps
                self._current = 0

            def start(self, api):
                self._current = 0
                self._data = {}
                if self._steps:
                    api.diagnostics.log(f"Wizard started: step={self._steps[0]['id']}")

            def next_step(self, api, field_data: dict):
                self._data.update(field_data)
                self._current += 1
                if self._current >= len(self._steps):
                    return self._finish(api)
                step = self._steps[self._current]
                api.diagnostics.log(f"Wizard step: {step['id']}")
                return step

            def _finish(self, api):
                api.diagnostics.log(f"Wizard complete: {self._data}")
                return {"complete": True, "result": self._data}

            def cancel(self, api):
                api.diagnostics.log("Wizard cancelled.")
                self._data = {}
                self._current = 0
        """).strip()

def gen_db_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Database Manager",cs) + textwrap.dedent("""
        class DatabaseManager:
            def __init__(self):
                self._connections = {}
                self._last_result = None

            def connect(self, conn_info: dict):
                key = conn_info.get("host","local") + ":" + str(conn_info.get("port",5432))
                self._connections[key] = {"info": conn_info, "connected": True}
                return key

            def execute(self, query: str, params=None):
                # Stub — replace with real DB driver (sqlite3, psycopg2, etc.)
                self._last_result = [{"query": query, "params": params}]
                return self._last_result

            def close_all(self):
                for k in self._connections:
                    self._connections[k]["connected"] = False

            def status(self) -> str:
                if not self._connections:
                    return "No active connections."
                lines = ["DB Connections:"]
                for k, v in self._connections.items():
                    state = "connected" if v["connected"] else "closed"
                    lines.append(f"  {k}: {state}")
                return "\\n".join(lines)
        """).strip()

def gen_network_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Network Client",cs) + textwrap.dedent("""
        import urllib.request, urllib.error, time

        class NetworkClient:
            def __init__(self):
                self._session_start = time.time()
                self._request_count = 0

            def send(self, request):
                # Stub — wrap with requests or http.client for real use
                self._request_count += 1
                return {"status": 200, "elapsed_ms": 0, "body": ""}

            def ping(self, url: str, timeout: int = 5) -> dict:
                t0 = time.time()
                try:
                    urllib.request.urlopen(url, timeout=timeout)
                    return {"url": url, "reachable": True, "ms": round((time.time()-t0)*1000)}
                except urllib.error.URLError as e:
                    return {"url": url, "reachable": False, "error": str(e)}

            def close(self):
                pass

            def status(self) -> str:
                uptime = round(time.time() - self._session_start, 1)
                return f"Network client | requests: {self._request_count} | uptime: {uptime}s"
        """).strip()

def gen_theme_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Theme Engine",cs) + textwrap.dedent("""
        class ThemeEngine:
            THEMES = {
                "dark":  {"bg":"#1a1a2e","fg":"#e8e6ff","accent":"#534AB7"},
                "light": {"bg":"#f5f4f0","fg":"#1a1a2e","accent":"#534AB7"},
                "neon":  {"bg":"#0d0d1a","fg":"#c9c5ff","accent":"#7F77DD"},
            }
            _cur = "dark"

            def init(self, api): pass
            def destroy(self): pass

            def apply(self, theme):
                name = getattr(theme, "name", theme) if not isinstance(theme, str) else theme
                if name in self.THEMES: self._cur = name

            def toggle(self, api):
                keys = list(self.THEMES.keys())
                self._cur = keys[(keys.index(self._cur) + 1) % len(keys)]
                api.diagnostics.log(f"Theme: {self._cur}")

            @property
            def current(self): return self.THEMES.get(self._cur, {})
        """).strip()

def gen_analyzer_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Code Analyzer",cs) + textwrap.dedent("""
        from dataclasses import dataclass, field
        @dataclass
        class AnalysisResult:
            lines: int = 0; non_empty: int = 0
            words: int = 0; chars: int = 0
            warnings: list = field(default_factory=list)
            @property
            def has_warnings(self): return bool(self.warnings)
            @property
            def warning_count(self): return len(self.warnings)
            def __str__(self):
                return (f"Lines: {self.lines}  Non-empty: {self.non_empty}\\n"
                        f"Words: {self.words}  Chars: {self.chars}\\n"
                        f"Warnings: {self.warning_count}")

        class CodeAnalyzer:
            def reset(self): self._last = None
            def quick_scan(self, text: str) -> AnalysisResult:
                r = AnalysisResult()
                ln = text.split("\\n"); r.lines = len(ln)
                r.non_empty = sum(1 for l in ln if l.strip())
                r.words = len(text.split()); r.chars = len(text)
                if "TODO" in text:  r.warnings.append("TODO found")
                if "FIXME" in text: r.warnings.append("FIXME found")
                if "HACK" in text:  r.warnings.append("HACK found")
                self._last = r; return r
            def full_scan(self, text: str) -> AnalysisResult:
                r = self.quick_scan(text)
                ll = [i+1 for i,l in enumerate(text.split("\\n")) if len(l)>120]
                if ll: r.warnings.append(f"Long lines: {ll[:5]}")
                return r
        """).strip()

def gen_reporter_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Report Builder",cs) + textwrap.dedent("""
        class ReportBuilder:
            def build(self, result) -> str:
                out = ["=" * 40, "  polsoft.ITS™ Analysis Report", "=" * 40, str(result)]
                if result.warnings:
                    out += ["", "Warnings:"] + [f"  • {w}" for w in result.warnings]
                out.append("=" * 40)
                return "\\n".join(out)
            def summary(self) -> str:
                return "No analysis run yet."
        """).strip()

def gen_shell_py(name, pid, author, cs="PEP8"):
    return hdr(".py",name,pid,author,"Shell Runner",cs) + textwrap.dedent("""
        import subprocess
        class ShellRunner:
            def __init__(self): self._buf = []
            def feed(self, line: str): self._buf.append(line)
            def run(self, cmd: str, timeout: int = 10) -> str:
                try: return subprocess.check_output(cmd, shell=True, text=True, timeout=timeout)
                except subprocess.TimeoutExpired: return "ERROR: timeout"
                except Exception as e: return f"ERROR: {e}"
            def flush(self):
                data, self._buf = self._buf[:], []
                return data
        """).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  TESTS  (4 files)
# ══════════════════════════════════════════════════════════════════════════════

def _mock_api_block():
    return textwrap.dedent("""
        import importlib.util, sys
        from unittest.mock import MagicMock
        from pathlib import Path

        def make_api():
            api = MagicMock()
            api.editor.getText.return_value = "line1\\nline2\\nline3"
            api.editor.getPath.return_value = "/project/file.py"
            return api

        def load_plugin():
            p = Path(__file__).parent.parent / "main.py"
            spec = importlib.util.spec_from_file_location("main", p)
            mod  = importlib.util.module_from_spec(spec)
            sys.modules["main"] = mod
            spec.loader.exec_module(mod)
            return mod
        """).strip()

def gen_test_load(name, pid, desc, author):
    h = hdr(".py",name,pid,author,f"Load tests for {name}")
    return h + _mock_api_block() + textwrap.dedent(f"""

        import pytest

        class TestOnLoad:
            def test_shows_message_on_load(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                api.editor.showMessage.assert_called_once()

            def test_message_contains_plugin_name(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                call_args = api.editor.showMessage.call_args[0]
                assert "{name}" in call_args[0]

            def test_load_does_not_raise(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)  # must not raise

            def test_load_info_severity(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                _, severity = api.editor.showMessage.call_args[0]
                assert severity == "info"
        """).strip()

def gen_test_commands(name, pid, desc, author):
    h = hdr(".py",name,pid,author,f"Command tests for {name}")
    return h + _mock_api_block() + textwrap.dedent(f"""

        import pytest

        class TestOnCommand:
            def test_run_command_executes(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                mod.onCommand(api, "{pid}.run", {{}})
                api.editor.showMessage.assert_called()

            def test_unknown_command_no_crash(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                mod.onCommand(api, "unknown.noop", {{}})  # must not raise

            def test_command_with_args(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                mod.onCommand(api, "{pid}.run", {{"key": "value"}})
                api.editor.showMessage.assert_called()

            def test_full_lifecycle_call_count(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                mod.onCommand(api, "{pid}.run", {{}})
                assert api.editor.showMessage.call_count >= 2
        """).strip()

def gen_test_ui(name, pid, desc, author, profile):
    h = hdr(".py",name,pid,author,f"UI tests for {name}")
    has_panel = profile not in ("minimal","wizard","telemetry","database","network")
    return h + _mock_api_block() + textwrap.dedent(f"""

        import pytest

        class TestUI:
            {'def test_panel_created(self):' if has_panel else 'def test_no_panel_minimal(self):'}
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                {"if hasattr(mod, 'onEditorReady'): mod.onEditorReady(api)" if has_panel else "pass"}
                {"api.ui.createPanel.assert_called()" if has_panel else "# minimal profile has no panel"}

            def test_showMessage_called_on_load(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                assert api.editor.showMessage.called

            def test_no_showDialog_on_load(self):
                mod = load_plugin(); api = make_api()
                mod.onLoad(api)
                api.ui.showDialog.assert_not_called()
        """).strip()

def gen_test_config(name, pid, desc, author):
    h = hdr(".py",name,pid,author,f"Config tests for {name}")
    return h + textwrap.dedent(f"""
        import json, pytest
        from pathlib import Path

        CONFIG_PATH = Path(__file__).parent.parent / "config" / "default.json"

        class TestConfig:
            def test_config_file_exists(self):
                assert CONFIG_PATH.exists(), f"config/default.json not found at {{CONFIG_PATH}}"

            def test_config_is_valid_json(self):
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                assert isinstance(data, dict)

            def test_config_has_meta(self):
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                assert "__meta" in data

            def test_config_has_analysis_section(self):
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                assert "analysis" in data

            def test_config_meta_has_plugin_name(self):
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                assert data["__meta"].get("plugin") == "{name}"
        """).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  SELFTEST.PY
# ══════════════════════════════════════════════════════════════════════════════

def gen_selftest(name, pid, desc, author):
    h = hdr(".py",name,pid,author,"Self-test runner")
    return h + textwrap.dedent(f"""
        \"\"\"
        {name} — Self-test runner
        Run: python selftest.py
        \"\"\"
        import sys, json, importlib.util
        from pathlib import Path
        from unittest.mock import MagicMock

        PASS = "✓"; FAIL = "✗"
        results = []

        def check(label, fn):
            try:
                fn()
                results.append((PASS, label))
            except Exception as e:
                results.append((FAIL, f"{{label}} — {{e}}"))

        # ── Load plugin ───────────────────────────────────────────────────────
        def load():
            p = Path(__file__).parent / "main.py"
            spec = importlib.util.spec_from_file_location("main", p)
            mod  = importlib.util.module_from_spec(spec)
            sys.modules["main"] = mod
            spec.loader.exec_module(mod)
            return mod

        def make_api():
            api = MagicMock()
            api.editor.getText.return_value = "line1\\nline2"
            return api

        # ── Tests ─────────────────────────────────────────────────────────────
        check("main.py loadable", lambda: load())

        def _test_onLoad():
            mod = load(); api = make_api()
            mod.onLoad(api)
            assert api.editor.showMessage.called
        check("onLoad calls showMessage", _test_onLoad)

        def _test_onCommand():
            mod = load(); api = make_api()
            mod.onLoad(api)
            mod.onCommand(api, "{pid}.run", {{}})
        check("onCommand does not crash", _test_onCommand)

        def _test_config():
            cfg = Path(__file__).parent / "config" / "default.json"
            assert cfg.exists()
            data = json.loads(cfg.read_text())
            assert "__meta" in data
        check("config/default.json valid", _test_config)

        def _test_manifest():
            mf = Path(__file__).parent / "manifest.yaml"
            assert mf.exists()
            text = mf.read_text()
            for field in ("name","id","version","hooks"):
                assert field in text, f"Missing field: {{field}}"
        check("manifest.yaml valid", _test_manifest)

        # ── Report ────────────────────────────────────────────────────────────
        print("\\n" + "=" * 50)
        print(f"  {name} — Self-test report")
        print("=" * 50)
        passed = failed = 0
        for icon, label in results:
            print(f"  {{icon}} {{label}}")
            if icon == PASS: passed += 1
            else: failed += 1
        print("=" * 50)
        print(f"  Passed: {{passed}}  Failed: {{failed}}")
        print("=" * 50)
        sys.exit(0 if failed == 0 else 1)
        """).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  META-PLUGIN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

def gen_meta_plugin_readme(name, pid, author):
    h = hdr(".txt",name,pid,author,"Meta-plugin system docs")
    return h + textwrap.dedent(f"""
        generator_plugins/ — Meta-Plugin System
        ════════════════════════════════════════

        Each .py file in this folder is a generator plugin that can extend
        the polsoft.ITS™ Plugin Generator without modifying its core.

        Interface:
          def apply(staged: dict, context: dict) -> dict:
              # staged  = {{rel_path: content}} dict of all files to be written
              # context = {{"name","pid","author","profile","icon_style",...}}
              # return modified staged dict
              return staged

        Bundled plugins:
          add_enterprise_features.py  — adds telemetry + DI stubs
          add_ui_themes.py            — injects extra CSS themes
          add_tests.py                — appends extra test cases
          add_telemetry.py            — adds telemetry hooks stub
          add_database_support.py     — adds sqlite3 stub

        Developer: {AUTHOR_META['name']} | {AUTHOR_META['company']}
        {AUTHOR_META['copy']}
        """).strip()

def gen_meta_plugin_file(name, pid, author, plugin_name, docstring, body):
    h = hdr(".py",name,pid,author,f"Generator meta-plugin: {plugin_name}")
    return h + textwrap.dedent(f"""
        \"\"\"
        {docstring}
        Interface: apply(staged, context) -> staged
        \"\"\"

        def apply(staged: dict, context: dict) -> dict:
        {body}
            return staged
        """).strip()

META_PLUGINS = {
    "add_enterprise_features.py": (
        "Adds enterprise feature stubs to any plugin",
        '    # Append enterprise comment to main.py\n'
        '    if "main.py" in staged:\n'
        '        staged["main.py"] += "\\n# [enterprise] DI + telemetry stubs available.\\n"'
    ),
    "add_ui_themes.py": (
        "Injects extra CSS theme variables",
        '    if "ui/panel.css" in staged:\n'
        '        staged["ui/panel.css"] += "\\n/* extra theme */\\n.theme-neon{--accent:#7F77DD;}\\n"'
    ),
    "add_tests.py": (
        "Appends integration test to test_commands",
        '    key = "tests/test_commands.py"\n'
        '    if key in staged:\n'
        '        staged[key] += "\\n# [meta] integration test added by generator_plugins\\n"'
    ),
    "add_telemetry.py": (
        "Adds telemetry stub file",
        '    if "libs/telemetry.py" not in staged:\n'
        '        staged["libs/telemetry_stub.py"] = "# Telemetry stub added by meta-plugin\\n"'
    ),
    "add_database_support.py": (
        "Adds sqlite3 helper stub",
        '    if "libs/db.py" not in staged:\n'
        '        staged["libs/sqlite_stub.py"] = ("import sqlite3\\n"\n'
        '            "# sqlite3 stub added by generator_plugins\\n")'
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
#  OTHER FILES
# ══════════════════════════════════════════════════════════════════════════════

def gen_readme(name, pid, desc, author, profile):
    m = AUTHOR_META
    return hdr(".txt",name,pid,author,desc) + textwrap.dedent(f"""
        Plugin:   {name}
        Profile:  {profile}
        ID:       {pid}
        Desc:     {desc}

        Developer: {author} | {m['company']}
        Email:     {m['email']}
        GitHub:    {m['github']}
        {m['copy']}
        """).strip()

def gen_changelog(name, pid, desc, author, profile):
    d = datetime.now().strftime("%Y-%m-%d")
    return hdr(".md",name,pid,author,desc) + textwrap.dedent(f"""
        # Changelog — {name}

        ## [1.0.0] — {d}

        ### Added
        - Initial release ({profile} profile)
        - Plugin ID: `{pid}`
        - Author metadata in every file
        - Generated by polsoft.ITS™ Plugin Generator v{VERSION}

        ### Future improvements
        - Extended command set
        - UI panel improvements
        - Additional unit tests
        - Auto-update integration
        """).strip()

def gen_requirements(name, pid, author, profile):
    m = AUTHOR_META
    extras = {
        "database":  "# sqlite3 is built-in; for postgres: psycopg2>=2.9.0\n# for mysql: mysql-connector-python>=8.0\n",
        "network":   "# requests>=2.28.0\n# aiohttp>=3.8.0  # for async\n",
        "telemetry": "# prometheus-client>=0.16.0  # optional metrics export\n",
    }
    return (f"# {'─'*58}\n# {name} — requirements.txt\n"
            f"# Developer: {author} | {m['company']}\n"
            f"# {m['copy']}\n# {'─'*58}\n\n"
            f"# No external deps by default.\n"
            f"{extras.get(profile,'')}"
            f"# pyyaml>=6.0\n# rich>=13.0.0\n")

def gen_config_json(name, author, profile):
    m = AUTHOR_META
    extra = {}
    if profile == "database":               extra = {"db":        {"host":"localhost","port":5432,"name":"mydb"}}
    if profile == "network":                extra = {"network":   {"base_url":"https://api.example.com","timeout":10}}
    if profile in ("telemetry","enterprise"): extra = {"telemetry": {"flush_interval":60,"max_records":1000}}
    base = {
        "__meta": {"plugin":name,"author":author,"company":m["company"],"email":m["email"],
                   "github":m["github"],"copyright":m["copy"],"profile":profile},
        "analysis": {"enabled":True,"mode":"basic"},
        "ui":       {"theme":"dark","layout":"sidebar","font":"Consolas"},
        "logging":  {"level":"info","max_lines":1000},
    }
    base.update(extra)
    return json.dumps(base, indent=2, ensure_ascii=False)

def _file_hashes(content: str) -> dict:
    """Compute SHA-256 and MD5 for a file content string (UTF-8 encoded)."""
    raw = content.encode("utf-8")
    return {
        "algorithm": "SHA-256",
        "sha256":    hashlib.sha256(raw).hexdigest(),
        "md5":       hashlib.md5(raw).hexdigest(),
        "size":      len(raw),
    }


def gen_integrity_json(files: dict) -> str:
    """
    Generate integrity.json with SHA-256 + MD5 for every staged file.
    integrity.json itself is NOT included in its own hashes (correct behaviour).
    """
    m = AUTHOR_META
    return json.dumps({
        "generated":  datetime.now().isoformat(),
        "generator":  f"polsoft.ITS™ Plugin Generator v{VERSION}",
        "algorithm":  "SHA-256",
        "author":     m["name"],
        "company":    m["company"],
        "copyright":  m["copy"],
        "files": {
            p: _file_hashes(c)
            for p, c in sorted(files.items())
        }
    }, indent=2, ensure_ascii=False)


def verify_integrity_on_disk(root: Path) -> dict:
    """
    Read integrity.json from a plugin root and verify every file's
    SHA-256 against its actual on-disk content.

    Returns a report dict:
      {ok: bool, checked: int, passed: int, failed: [{path, expected, actual}]}
    """
    integ_path = root / "integrity.json"
    if not integ_path.exists():
        return {"ok": False, "error": "integrity.json not found", "checked": 0,
                "passed": 0, "failed": []}
    try:
        data = json.loads(integ_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"integrity.json parse error: {e}",
                "checked": 0, "passed": 0, "failed": []}

    file_entries = data.get("files", {})
    if not file_entries:
        return {"ok": False, "error": "integrity.json has no 'files' section",
                "checked": 0, "passed": 0, "failed": []}

    passed, failed = 0, []
    for rel_path, entry in file_entries.items():
        expected_sha = entry.get("sha256", "")
        fpath = root / rel_path
        if not fpath.exists():
            failed.append({"path": rel_path, "issue": "file missing on disk"})
            continue
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        if actual_sha == expected_sha:
            passed += 1
        else:
            failed.append({
                "path":     rel_path,
                "expected": expected_sha,
                "actual":   actual_sha,
                "issue":    "SHA-256 mismatch",
            })

    total = passed + len(failed)
    return {
        "ok":      len(failed) == 0,
        "checked": total,
        "passed":  passed,
        "failed":  failed,
        "generated": datetime.now().isoformat(),
    }

def gen_update_json(name, pid, desc, author, profile):
    m = AUTHOR_META
    return json.dumps({
        "__meta": {"generated_by": f"polsoft.ITS™ Plugin Generator v{VERSION}",
                   "date": datetime.now().isoformat()},
        "plugin":      name,
        "id":          pid,
        "version":     "1.0.0",
        "profile":     profile,
        "description": desc,
        "author":      {"name": author, "company": m["company"], "email": m["email"], "github": m["github"]},
        "copyright":   m["copy"],
        "update": {
            "enabled":      False,
            "check_url":    f"https://github.com/seb07uk/{pid}/releases/latest",
            "release_notes": f"https://github.com/seb07uk/{pid}/blob/main/CHANGELOG.md",
            "auto_install": False,
        }
    }, indent=2, ensure_ascii=False)

def gen_plugin_info(name, pid, desc, author, profile, license_, files):
    m = AUTHOR_META
    return json.dumps({
        "__meta": {"generated_by": f"polsoft.ITS™ Plugin Generator v{VERSION}",
                   "date": datetime.now().isoformat()},
        "name": name, "id": pid, "version": "1.0.0",
        "description": desc, "profile": profile, "license": license_,
        "author": {"name": author, "company": m["company"], "email": m["email"], "github": m["github"]},
        "copyright": m["copy"],
        "api": {
            "version": "1.0.0", "min_engine": "1.0.0",
            "hooks": HOOKS_BY_PROFILE.get(profile, ["onLoad","onCommand"]),
            "commands": [{"id": f"{pid}.run", "shortcut": "Ctrl+Alt+R"}],
            "panels": [{"id":f"{pid}.panel","position":"right"}] if profile in PROFILES_WITH_UI else [],
            "permissions": PERMS_BY_PROFILE.get(profile, ["editor:read-write"]),
        },
        "environment": {"python_min": "3.8", "platforms": ["win32","darwin","linux"]},
        "file_integrity": {p: hashlib.sha256(c.encode("utf-8")).hexdigest() for p,c in files.items()},
    }, indent=2, ensure_ascii=False)

def gen_pm_manifest(name, pid, desc, author, profile, license_):
    m = AUTHOR_META
    return hdr(".yaml",name,pid,author,desc) + textwrap.dedent(f"""
        plugin:
          name: "{name}"
          id: "{pid}"
          version: "1.0.0"
          profile: "{profile}"
          description: "{desc}"
        author:
          name: "{author}"
          company: "{m['company']}"
          email: "{m['email']}"
          github: "{m['github']}"
        copyright: "{m['copy']}"
        license: "{license_}"
        compatibility:
          engine_min: "1.0.0"
          api_version: "1.0.0"
          platforms: [win32, darwin, linux]
        paths:
          manifest: manifest.yaml
          entry: main.py
          icons: icons/
          ui: ui/
          config: config/
          libs: libs/
        integrations:
          plugin_manager: true
          diagnostics: true
          auto_update: false
        """).strip()

def gen_diag_structure(name, pid, profile, files):
    m = AUTHOR_META
    return json.dumps({
        "plugin": name, "id": pid, "profile": profile,
        "generated": datetime.now().isoformat(),
        "generator": f"polsoft.ITS™ Plugin Generator v{VERSION}",
        "author": {"name": m["name"], "company": m["company"]},
        "copyright": m["copy"],
        "files": sorted(files.keys()),
        "file_count": len(files),
    }, indent=2, ensure_ascii=False)

def gen_diag_hashes(files):
    return json.dumps({
        "generated": datetime.now().isoformat(),
        "algorithm": "SHA-256",
        "hashes": {p: _file_hashes(c) for p, c in sorted(files.items())}
    }, indent=2, ensure_ascii=False)

def gen_manifest_report(name, pid, profile, manifest_content):
    """Validate manifest and produce JSON report."""
    issues = []
    warnings = []
    required = ["name","id","version","description","author","license","hooks"]
    for f in required:
        if f not in manifest_content:
            issues.append(f"Missing required field: '{f}'")
    if "id:" in manifest_content:
        m = re.search(r'id:\s*"([^"]+)"', manifest_content)
        if m:
            val = m.group(1)
            if " " in val: issues.append(f"ID must not contain spaces: '{val}'")
    if "version:" in manifest_content:
        mv = re.search(r'version:\s*"([^"]+)"', manifest_content)
        if mv:
            v = mv.group(1)
            if not (v.count(".")==2 and all(p.isdigit() for p in v.split("."))):
                issues.append(f"Version must be X.Y.Z: '{v}'")
    if "hooks:" not in manifest_content:
        warnings.append("No hooks section found")
    return json.dumps({
        "generated": datetime.now().isoformat(),
        "plugin": name, "id": pid, "profile": profile,
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "issue_count": len(issues),
        "warning_count": len(warnings),
    }, indent=2, ensure_ascii=False)

def gen_install_ps1(name, pid, author):
    return hdr(".ps1",name,pid,author,"PowerShell installer") + textwrap.dedent(f"""
        $PluginName = "{name}"
        $PluginId   = "{pid}"
        $Target     = "$env:APPDATA\\polsoft.ITS\\ScriptEditor\\plugins\\$PluginName"
        Write-Host "polsoft.ITS Plugin Installer" -ForegroundColor Cyan
        Write-Host "Plugin: $PluginName ($PluginId)"
        if (-Not (Test-Path $Target)) {{ New-Item -ItemType Directory $Target -Force | Out-Null }}
        Copy-Item -Path ".\\*" -Destination $Target -Recurse -Force
        if (Test-Path "$Target\\manifest.yaml") {{
            Write-Host "Manifest OK." -ForegroundColor Green
        }} else {{ Write-Host "WARNING: manifest.yaml missing!" -ForegroundColor Red }}
        Write-Host "Done." -ForegroundColor Green
        """).strip()

def gen_install_bat(name, pid, author):
    return hdr(".bat",name,pid,author,"Batch installer") + textwrap.dedent(f"""
        @echo off
        set PLUGIN={name}
        set TARGET=%APPDATA%\\polsoft.ITS\\ScriptEditor\\plugins\\%PLUGIN%
        echo polsoft.ITS Plugin Installer
        if not exist "%TARGET%" mkdir "%TARGET%"
        xcopy /E /I /Y ".\\*" "%TARGET%\\" > nul
        if exist "%TARGET%\\manifest.yaml" (echo Manifest OK.) else (echo WARNING: manifest.yaml missing!)
        echo Plugin %PLUGIN% installed.
        pause
        """).strip()

# ══════════════════════════════════════════════════════════════════════════════
#  JINJA2 / TEMPLATE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

def _make_j2_context(name: str, pid: str, desc: str, author: str,
                     profile: str, license_: str = "MIT",
                     version: str = "1.0.0", icon_style: str = "dark",
                     code_style: str = "PEP8", ui_layout: str = "sidebar") -> dict:
    """Build the template variable context used by render_j2()."""
    m = AUTHOR_META
    hooks    = HOOKS_BY_PROFILE.get(profile, ["onLoad","onCommand"])
    perms    = PERMS_BY_PROFILE.get(profile, ["editor:read-write"])
    commands = [f"{pid}.run"]
    panels   = [f"{pid}.panel"] if profile in PROFILES_WITH_UI else []
    return {
        "name":        name,
        "plugin_id":   pid,
        "description": desc,
        "author":      author,
        "version":     version,
        "brand":       BRAND,
        "year":        m["year"],
        "license":     license_,
        "profile":     profile,
        "company":     m["company"],
        "email":       m["email"],
        "github":      m["github"],
        "copyright":   m["copy"],
        "ui_style":    icon_style,
        "code_style":  code_style,
        "ui_layout":   ui_layout,
        "hooks":       hooks,
        "commands":    commands,
        "panels":      panels,
        "permissions": perms,
        "generated":   datetime.now().strftime("%Y-%m-%d"),
        "generator":   f"polsoft.ITS™ Plugin Generator v{VERSION}",
    }


def render_j2(template_str: str, context: dict) -> str:
    """
    Render a Jinja2 template string.

    Uses the real Jinja2 engine if available (JINJA2_OK=True), otherwise
    falls back to simple {{ variable }} substitution via str.replace.
    The fallback handles all variables defined in TEMPLATE_VARS.
    Loop/condition constructs require Jinja2.
    """
    if JINJA2_OK:
        try:
            env = jinja2.Environment(
                keep_trailing_newline=True,
                undefined=jinja2.Undefined,   # silently skip unknown vars
            )
            tmpl = env.from_string(template_str)
            return tmpl.render(**context)
        except Exception:
            pass  # fallback to simple substitution on render error

    # ── Simple {{ var }} substitution fallback ────────────────────────────────
    result = template_str
    for key, val in context.items():
        if isinstance(val, list):
            val_str = ", ".join(str(v) for v in val)
        else:
            val_str = str(val)
        result = result.replace("{{ " + key + " }}", val_str)
        result = result.replace("{{" + key + "}}", val_str)
    return result


# ── .j2 template content generators per file type ─────────────────────────────

def _j2_manifest() -> str:
    return textwrap.dedent("""\
        # manifest.yaml.j2 — polsoft.ITS™ Plugin Manifest Template
        # Generated by {{ generator }} | {{ generated }}
        # {{ copyright }}
        name: "{{ name }}"
        id: "{{ plugin_id }}"
        version: "{{ version }}"
        description: "{{ description }}"
        profile: "{{ profile }}"

        author:
          name: "{{ author }}"
          company: "{{ company }}"
          email: "{{ email }}"
          github: "{{ github }}"
        license: "{{ license }}"
        copyright: "{{ copyright }}"

        engine:
          min_version: "1.0.0"
          api_version: "1.0.0"

        hooks:
        {%- for hook in hooks %}
          {{ hook }}: true
        {%- endfor %}

        commands:
          - id: "{{ plugin_id }}.run"
            title: "Run {{ name }}"
            shortcut: "Ctrl+Alt+R"

        permissions:
        {%- for perm in permissions %}
          - {{ perm }}
        {%- endfor %}

        settings:
          enabled: true
          config_file: "config/default.json"
        """)

def _j2_main_py() -> str:
    return textwrap.dedent("""\
        # -*- coding: utf-8 -*-
        # {{ name }} | {{ plugin_id }}
        # {{ description }}
        # Generated: {{ generated }} by {{ generator }}
        # Developer: {{ author }}  |  {{ company }}
        # Email:     {{ email }}
        # GitHub:    {{ github }}
        # {{ copyright }}

        def onLoad(api):
            api.editor.showMessage("{{ name }} loaded.", "info")
            api.diagnostics.log("{{ name }} loaded.")

        def onUnload(api):
            api.diagnostics.log("{{ name }} unloaded.")

        def onCommand(api, commandId, args):
            if commandId == "{{ plugin_id }}.run":
                api.editor.showMessage("{{ name }} — executed.", "info")
        """)

def _j2_readme() -> str:
    return textwrap.dedent("""\
        {{ name }} — polsoft.ITS™ Script Editor Plugin
        ══════════════════════════════════════════════
        Plugin:      {{ name }}
        Profile:     {{ profile }}
        ID:          {{ plugin_id }}
        Description: {{ description }}
        Version:     {{ version }}

        Developer:   {{ author }}
        Company:     {{ company }}
        Email:       {{ email }}
        GitHub:      {{ github }}
        {{ copyright }}
        """)

def _j2_panel_html() -> str:
    return textwrap.dedent("""\
        <!-- {{ name }} | {{ plugin_id }} | UI Panel -->
        <!-- Developer: {{ author }}  |  {{ company }} -->
        <!-- Email:     {{ email }}  |  GitHub: {{ github }} -->
        <!-- Generated: {{ generated }}  |  {{ copyright }} -->
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <link rel="stylesheet" href="panel.css">
          <title>{{ name }}</title>
        </head>
        <body>
          <div class="panel sidebar">
            <div class="panel-header"><h2>{{ name }}</h2></div>
            <nav class="sidebar-nav">
              <button class="nav-btn active"
                      onclick="api.command('{{ plugin_id }}.run')">▶ Run</button>
            </nav>
            <div id="output" class="output"></div>
            <footer class="panel-footer">{{ copyright }}</footer>
          </div>
        </body>
        </html>
        """)

def _j2_panel_css() -> str:
    return textwrap.dedent("""\
        /* {{ name }} — Panel styles */
        /* Developer: {{ author }} | {{ company }} | {{ generated }} */
        :root{--bg:#1a1a2e;--fg:#e8e6ff;--accent:#534AB7;--muted:#9994cc;--card:#0d0d1a}
        *{box-sizing:border-box;margin:0;padding:0}
        body{background:var(--bg);color:var(--fg);font-family:Consolas,monospace;font-size:13px}
        .panel{display:flex;flex-direction:column;height:100vh}
        .panel-header{padding:10px 12px;background:var(--card);border-bottom:1px solid #2a2a4a}
        h2{font-size:14px;color:var(--accent);margin:0}
        button{background:var(--accent);color:#fff;border:none;padding:6px 10px;
               cursor:pointer;border-radius:3px;font-family:inherit;font-size:12px}
        button:hover{opacity:.85}
        .output{flex:1;white-space:pre;font-size:11px;color:var(--muted);
                background:var(--card);padding:8px;overflow:auto;min-height:60px}
        .panel-footer{font-size:9px;color:#3a3a5a;padding:4px 8px;
                      border-top:1px solid #1e1e3a}
        .sidebar-nav{display:flex;flex-direction:column;gap:4px;padding:8px}
        .nav-btn{width:100%;text-align:left;background:transparent;color:var(--muted);
                 border:none;padding:6px 10px;cursor:pointer;border-radius:3px}
        .nav-btn:hover,.nav-btn.active{background:var(--accent);color:#fff}
        """)

def _j2_config_json() -> str:
    return textwrap.dedent("""\
        {
          "__meta": {
            "plugin":    "{{ name }}",
            "author":    "{{ author }}",
            "company":   "{{ company }}",
            "email":     "{{ email }}",
            "github":    "{{ github }}",
            "copyright": "{{ copyright }}",
            "profile":   "{{ profile }}"
          },
          "analysis": {"enabled": true, "mode": "basic"},
          "ui":       {"theme": "dark", "layout": "{{ ui_layout }}", "font": "Consolas"},
          "logging":  {"level": "info", "max_lines": 1000}
        }
        """)

def _j2_helper_py() -> str:
    return textwrap.dedent("""\
        # -*- coding: utf-8 -*-
        # {{ name }} | {{ plugin_id }} — Helper utilities
        # Developer: {{ author }} | {{ company }} | {{ copyright }}

        def analyze_text(text: str) -> str:
            lines = text.split("\\n")
            return (f"Lines: {len(lines)}\\nWords: {len(text.split())}\\n"
                    f"Chars: {len(text)}")

        def truncate(text: str, n: int = 200) -> str:
            return text[:n] + "..." if len(text) > n else text
        """)

def _j2_plugin_svg() -> str:
    return textwrap.dedent("""\
        <!-- {{ name }} | plugin icon | {{ generated }} | {{ copyright }} -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
          <rect width="32" height="32" rx="6" fill="#18181b"/>
          <rect x="1" y="1" width="30" height="30" rx="5" fill="none"
                stroke="#534AB7" stroke-width="0.8"/>
          <text x="16" y="21" text-anchor="middle" font-size="13"
                fill="#e8e6ff" font-family="Consolas,monospace"
                font-weight="500">{{ name|truncate(1,'') }}</text>
        </svg>
        """)


# ── Map: relative file path → generator function ──────────────────────────────
_J2_FILE_GENERATORS: dict[str, callable] = {
    "manifest.yaml.j2":       _j2_manifest,
    "main.py.j2":             _j2_main_py,
    "README.txt.j2":          _j2_readme,
    "ui/panel.html.j2":       _j2_panel_html,
    "ui/panel.css.j2":        _j2_panel_css,
    "config/default.json.j2": _j2_config_json,
    "libs/helper.py.j2":      _j2_helper_py,
    "icons/plugin.svg.j2":    _j2_plugin_svg,
}


def gen_template_json(profile: str) -> str:
    """Generate template.json descriptor for a given profile."""
    m = AUTHOR_META
    has_ui = profile in PROFILES_WITH_UI
    optional = J2_OPTIONAL_FILES.get(profile, [])
    return json.dumps({
        "__meta": {
            "generated_by": f"polsoft.ITS™ Plugin Generator v{VERSION}",
            "date": datetime.now().isoformat(),
            "copyright": m["copy"],
        },
        "type":     profile,
        "hooks":    HOOKS_BY_PROFILE.get(profile, ["onLoad","onCommand"]),
        "commands": ["run"],
        "panels":   ["main"] if has_ui else [],
        "ui":       "dark",
        "requires": {
            "filesystem": profile not in ("minimal","wizard"),
            "editor":     "full-access" if profile != "minimal" else "read-write",
            "network":    profile in ("network","telemetry","enterprise"),
            "terminal":   profile == "terminal",
            "database":   profile == "database",
        },
        "files": {
            "required": J2_REQUIRED_FILES,
            "optional": optional,
        },
        "variables":    TEMPLATE_VARS,
        "permissions":  PERMS_BY_PROFILE.get(profile, ["editor:read-write"]),
    }, indent=2, ensure_ascii=False)


def gen_j2_templates(profile: str, out_dir: Path) -> dict[str, str]:
    """
    Generate all .j2 template files for a given profile into out_dir.
    Returns a dict of {relative_path: content} for every file written.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    staged: dict[str, str] = {}

    # Always generate required files
    for rel in J2_REQUIRED_FILES:
        gen_fn = _J2_FILE_GENERATORS.get(rel)
        content = gen_fn() if gen_fn else f"# {rel} — add content here\n"
        staged[rel] = content

    # Generate optional files for this profile
    for rel in J2_OPTIONAL_FILES.get(profile, []):
        gen_fn = _J2_FILE_GENERATORS.get(rel)
        content = gen_fn() if gen_fn else f"# {rel} — add content here\n"
        staged[rel] = content

    # template.json
    staged["template.json"] = gen_template_json(profile)

    # Write all files to disk
    for rel, content in staged.items():
        fpath = out_dir / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")

    return staged


def validate_template(template_dir: Path) -> dict:
    """
    Validate a template directory (profile subdirectory inside templates/).
    Checks: required .j2 files, Jinja2 variable usage, template.json validity.
    Returns a structured report compatible with diagnostics/template_report.json.
    """
    errors:   list = []
    warnings: list = []
    profile   = template_dir.name

    def err(f: str, msg: str):
        errors.append({"file": f, "message": msg})

    def warn(f: str, msg: str):
        warnings.append({"file": f, "message": msg})

    if not template_dir.is_dir():
        return {"status": "ERROR", "errors": [{"file": str(template_dir),
                "message": "Template directory not found"}],
                "warnings": [], "error_count": 1, "warning_count": 0,
                "profile": profile, "generated": datetime.now().isoformat()}

    # ── 1. Required .j2 files ─────────────────────────────────────────────────
    for req in J2_REQUIRED_FILES:
        if not (template_dir / req).exists():
            err(req, f"Required template file '{req}' not found")

    # ── 2. Optional .j2 files ─────────────────────────────────────────────────
    for opt in J2_OPTIONAL_FILES.get(profile, []):
        if not (template_dir / opt).exists():
            warn(opt, f"Optional template file '{opt}' not found "
                      f"(expected for profile '{profile}')")

    # ── 3. template.json ──────────────────────────────────────────────────────
    tj = template_dir / "template.json"
    if not tj.exists():
        err("template.json", "template.json descriptor not found")
    else:
        try:
            tj_data = json.loads(tj.read_text(encoding="utf-8"))
            for field in ("type","hooks","commands","ui","requires","files"):
                if field not in tj_data:
                    warn("template.json", f"Missing field: '{field}'")
            if "type" in tj_data and tj_data["type"] not in TEMPLATE_TYPES:
                warn("template.json",
                     f"Unknown type '{tj_data['type']}' — "
                     f"expected one of: {', '.join(TEMPLATE_TYPES)}")
            if "hooks" in tj_data and not isinstance(tj_data["hooks"], list):
                err("template.json", "'hooks' must be a list")
        except json.JSONDecodeError as e:
            err("template.json", f"JSON parse error: {e}")

    # ── 4. Jinja2 variable checks in each .j2 file ────────────────────────────
    j2_files = list(template_dir.rglob("*.j2"))
    if not j2_files:
        warn(str(template_dir), "No .j2 files found in template directory")
    else:
        for j2f in j2_files:
            rel = str(j2f.relative_to(template_dir))
            try:
                content = j2f.read_text(encoding="utf-8")
            except Exception as e:
                err(rel, f"Cannot read file: {e}")
                continue

            # Check for {{ variable }} usage
            found_vars = set(re.findall(r"\{\{\s*(\w+)\s*[\|}]", content))
            # Allow known TEMPLATE_VARS + Jinja2 loop iteration vars + filter names
            _allowed = set(TEMPLATE_VARS) | {
                "loop","forloop","block",
                "hook","perm","permission","command","panel","item","entry",
                "key","value","idx","index",
            }
            unknown = found_vars - _allowed
            if unknown:
                warn(rel, f"Unknown template variables: {sorted(unknown)}")

            # Warn if no variables at all — template may be static
            # (suppress for known pure-code library files)
            _lib_suffixes = {".py.j2"}
            _known_static = {"container.py.j2","events.py.j2","shell.py.j2",
                             "wizard_engine.py.j2","db.py.j2","network.py.j2",
                             "analyzer.py.j2","reporter.py.j2","metrics.py.j2",
                             "theme.py.j2","telemetry.py.j2"}
            if not found_vars and Path(rel).name not in _known_static:
                warn(rel, "No template variables ({{ ... }}) found — may be a static file")

            # Check Jinja2 syntax if jinja2 is available
            if JINJA2_OK:
                try:
                    env = jinja2.Environment()
                    env.parse(content)
                except jinja2.TemplateSyntaxError as e:
                    err(rel, f"Jinja2 syntax error at line {e.lineno}: {e.message}")

    # ── 5. manifest.yaml.j2 required fields ──────────────────────────────────
    mj2 = template_dir / "manifest.yaml.j2"
    if mj2.exists():
        mj2_text = mj2.read_text(encoding="utf-8")
        for required_field in ("name:", "id:", "version:", "hooks:"):
            if required_field not in mj2_text:
                warn("manifest.yaml.j2",
                     f"Required YAML field '{required_field}' not present in template")
        if "{{ plugin_id }}" not in mj2_text and "{{ name }}" not in mj2_text:
            warn("manifest.yaml.j2",
                 "Neither {{ plugin_id }} nor {{ name }} found — plugin identity not templated")

    status = "OK" if not errors else "ERROR"
    return {
        "profile":       profile,
        "template_dir":  str(template_dir),
        "status":        status,
        "generated":     datetime.now().isoformat(),
        "generator":     f"polsoft.ITS™ Plugin Generator v{VERSION}",
        "copyright":     AUTHOR_META["copy"],
        "j2_files_found": len(j2_files),
        "errors":        errors,
        "warnings":      warnings,
        "error_count":   len(errors),
        "warning_count": len(warnings),
    }


def generate_from_template(
    template_dir: Path, out_dir: Path,
    name: str, pid: str, desc: str, author: str,
    profile: str, license_: str = "MIT", version: str = "1.0.0",
    icon_style: str = "dark", code_style: str = "PEP8",
    ui_layout: str = "sidebar",
) -> dict[str, str]:
    """
    Render all .j2 files in template_dir into a plugin folder under out_dir.

    Flow (matches Instrukcja_integracji.txt §5):
      1. Load template.json
      2. Build Jinja2 context
      3. Render every .j2 → output file (strip .j2 suffix)
      4. Generate integrity.json + plugin-info.json
      5. Pack into .pits-plugin.zip
      6. Return staged dict

    Raises FileNotFoundError if template_dir does not exist.
    """
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Load template.json for metadata (optional — tolerate absence)
    tj_path = template_dir / "template.json"
    template_meta: dict = {}
    if tj_path.exists():
        try:
            template_meta = json.loads(tj_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    context = _make_j2_context(name, pid, desc, author, profile, license_,
                                version, icon_style, code_style, ui_layout)

    root   = out_dir / name
    staged: dict[str, str] = {}

    # Render every .j2 file found in template_dir
    for j2f in sorted(template_dir.rglob("*.j2")):
        rel_j2  = j2f.relative_to(template_dir)
        rel_out = Path(str(rel_j2)[:-3])  # strip .j2 suffix
        try:
            raw = j2f.read_text(encoding="utf-8")
        except Exception as e:
            continue  # skip unreadable files
        rendered = render_j2(raw, context)
        staged[str(rel_out)] = rendered

    # Copy non-.j2 files verbatim (icons, static assets, etc.)
    for fpath in sorted(template_dir.rglob("*")):
        if fpath.is_file() and fpath.suffix != ".j2" and fpath.name != "template.json":
            rel = str(fpath.relative_to(template_dir))
            if rel not in staged:
                staged[rel] = fpath.read_text(encoding="utf-8", errors="replace")

    # Generate integrity.json from staged content
    staged["integrity.json"] = gen_integrity_json(staged)

    # Generate plugin-info.json
    staged["plugin-info.json"] = gen_plugin_info(
        name, pid, desc, author, profile, license_, staged
    )

    # Write all files to disk
    for rel, content in staged.items():
        fpath = root / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")

    # Pack ZIP
    build_zip(root, name)

    # Save template report alongside plugin
    report = validate_template(template_dir)
    (root / "diagnostics").mkdir(parents=True, exist_ok=True)
    (root / "diagnostics" / "template_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    staged["diagnostics/template_report.json"] = json.dumps(report, indent=2)

    return staged


# ══════════════════════════════════════════════════════════════════════════════
#  CORE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_plugin(
    base_dir, name, pid, desc, author, license_, profile,
    icon_style="dark", code_style="PEP8", ui_layout="sidebar",
    opt_tests=True, opt_selftest=True, opt_changelog=True, opt_reqs=True,
    opt_install=True, opt_diag=True, opt_integrity=True, opt_update=True,
    opt_apimanif=True, opt_pmmanif=True, opt_metaplug=True,
    opt_autovalidate=True,
):
    root   = base_dir / name
    staged = {}

    def stage(rel, content):
        staged[rel] = content

    cs = code_style

    # ── Core ─────────────────────────────────────────────────────────────────
    manifest_content = gen_manifest_yaml(name,pid,desc,author,license_,profile)
    stage("README.txt",          gen_readme(name,pid,desc,author,profile))
    stage("manifest.yaml",       manifest_content)
    stage("main.py",             gen_main_py(name,pid,desc,author,profile,cs))
    stage("config/default.json", gen_config_json(name,author,profile))

    # ── Icons — 5 variants ───────────────────────────────────────────────────
    for variant in ("plugin","panel","toolbar"):
        stage(f"icons/{variant}.svg", gen_svg(name,pid,author,icon_style,variant))
    stage("icons/plugin_dark.svg",     gen_svg(name,pid,author,"dark","plugin"))
    stage("icons/plugin_symbolic.svg", gen_svg(name,pid,author,"symbolic","plugin"))

    # ── Profile-specific UI + libs ────────────────────────────────────────────
    has_ui = profile in PROFILES_WITH_UI
    if has_ui:
        stage("ui/panel.html", gen_panel_html(name,pid,author,desc,ui_layout))
        stage("ui/panel.css",  gen_panel_css(name,pid,author,ui_layout))

    lib_map = {
        "advanced":   [("libs/helper.py",    gen_helper_py(name,pid,author,cs))],
        "enterprise": [("libs/helper.py",    gen_helper_py(name,pid,author,cs)),
                       ("libs/container.py", gen_container_py(name,pid,author,cs)),
                       ("libs/events.py",    gen_events_py(name,pid,author,cs)),
                       ("libs/telemetry.py", gen_telemetry_py(name,pid,author,cs))],
        "ui-heavy":   [("libs/theme.py",     gen_theme_py(name,pid,author,cs))],
        "analysis":   [("libs/analyzer.py",  gen_analyzer_py(name,pid,author,cs)),
                       ("libs/reporter.py",  gen_reporter_py(name,pid,author,cs))],
        "terminal":   [("libs/shell.py",     gen_shell_py(name,pid,author,cs))],
        "wizard":     [("libs/wizard_engine.py", gen_wizard_engine_py(name,pid,author,cs))],
        "telemetry":  [("libs/telemetry.py", gen_telemetry_py(name,pid,author,cs)),
                       ("libs/metrics.py",   gen_metrics_py(name,pid,author,cs))],
        "database":   [("libs/db.py",        gen_db_py(name,pid,author,cs))],
        "network":    [("libs/network.py",   gen_network_py(name,pid,author,cs))],
    }
    for rel, content in lib_map.get(profile, []):
        stage(rel, content)

    # ── Profile-specific extra directories ───────────────────────────────────
    if profile == "enterprise":
        m = AUTHOR_META
        stage("telemetry/.gitkeep",
              f"# {name} — telemetry/ directory\n# {m['copy']}\n"
              "# Place telemetry export configs or adapters here.\n")
        stage("diagnostics/.gitkeep",
              f"# {name} — diagnostics/ directory\n# {m['copy']}\n"
              "# Runtime diagnostics logs and reports are written here.\n"
              "# This directory is created at runtime if absent.\n")

    # ── Optional ──────────────────────────────────────────────────────────────
    if opt_changelog:
        stage("CHANGELOG.md", gen_changelog(name,pid,desc,author,profile))

    if opt_reqs:
        stage("requirements.txt", gen_requirements(name,pid,author,profile))

    if opt_tests:
        stage("tests/__init__.py",    f"# {name} tests\n# {AUTHOR_META['copy']}\n")
        stage("tests/test_load.py",     gen_test_load(name,pid,desc,author))
        stage("tests/test_commands.py", gen_test_commands(name,pid,desc,author))
        stage("tests/test_ui.py",       gen_test_ui(name,pid,desc,author,profile))
        stage("tests/test_config.py",   gen_test_config(name,pid,desc,author))

    if opt_selftest:
        stage("selftest.py", gen_selftest(name,pid,desc,author))

    if opt_install:
        stage("install.ps1", gen_install_ps1(name,pid,author))
        stage("install.bat", gen_install_bat(name,pid,author))

    if opt_pmmanif:
        stage(".plugin-manifest.yaml", gen_pm_manifest(name,pid,desc,author,profile,license_))

    if opt_update:
        stage("update.json", gen_update_json(name,pid,desc,author,profile))

    if opt_apimanif:
        stage("plugin-info.json", gen_plugin_info(name,pid,desc,author,profile,license_,staged))

    if opt_integrity:
        stage("integrity.json", gen_integrity_json(staged))

    if opt_metaplug:
        stage("generator_plugins/README.txt", gen_meta_plugin_readme(name,pid,author))
        for fname, (doc, body) in META_PLUGINS.items():
            stage(f"generator_plugins/{fname}",
                  gen_meta_plugin_file(name,pid,author,fname,doc,body))

    if opt_diag:
        stage("diagnostics/plugin_structure.json", gen_diag_structure(name,pid,profile,staged))
        stage("diagnostics/file_hashes.json",      gen_diag_hashes(staged))
        stage("diagnostics/manifest_report.json",  gen_manifest_report(name,pid,profile,manifest_content))

    # ── Write to disk ─────────────────────────────────────────────────────────
    for rel, content in staged.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # ── Post-generation validation ────────────────────────────────────────────
    if opt_autovalidate:
        report = validate_plugin(root)
        report_path = root / "diagnostics" / "plugin_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        staged["diagnostics/plugin_report.json"] = json.dumps(report, indent=2)

    return staged

# ══════════════════════════════════════════════════════════════════════════════
#  VALIDATOR
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_FIELDS = ["name","id","version","description","author","license","hooks"]

def validate_manifest(path: Path) -> tuple[list, list]:
    """Returns (issues, warnings) lists."""
    issues, warnings = [], []
    if not path.exists():
        return ([f"File not found: {path}"], [])
    text = path.read_text(encoding="utf-8")
    if YAML_OK:
        try: data = yaml.safe_load(text)
        except Exception as e: return ([f"YAML parse error: {e}"], [])
        if not isinstance(data, dict): return (["Root must be a mapping"], [])
        for f in REQUIRED_FIELDS:
            if f not in data: issues.append(f"Missing required field: '{f}'")
        if "id" in data and " " in str(data["id"]):
            issues.append("ID must not contain spaces")
        if "version" in data:
            v = str(data["version"])
            if not (v.count(".")==2 and all(p.isdigit() for p in v.split("."))):
                issues.append(f"Version must be X.Y.Z: '{v}'")
        if "author" in data and isinstance(data["author"],dict):
            if "name" not in data["author"]: issues.append("author.name missing")
            if "email" not in data["author"]: warnings.append("author.email missing (recommended)")
        if "hooks" in data and isinstance(data["hooks"],dict):
            if not any(data["hooks"].values()): issues.append("At least one hook must be enabled")
        if "engine" not in data: warnings.append("engine.min_version not specified")
        if "permissions" not in data: warnings.append("permissions not specified")
    else:
        for f in REQUIRED_FIELDS:
            if f not in text: issues.append(f"Missing field: '{f}'")
    return (issues, warnings)


# ══════════════════════════════════════════════════════════════════════════════
#  FULL PLUGIN VALIDATOR  (validates generated plugin directory)
# ══════════════════════════════════════════════════════════════════════════════

def validate_plugin(root: Path) -> dict:
    """
    Full plugin validator — checks structure, UI, config, icons, hooks, and
    metadata of a generated plugin folder. Returns a structured report dict
    compatible with diagnostics/plugin_report.json format.
    """
    errors: list   = []
    warnings: list = []
    plugin_name    = root.name
    profile        = "minimal"

    def err(file: str, msg: str, line: int | None = None):
        e: dict = {"file": file, "message": msg}
        if line is not None:
            e["line"] = line
        errors.append(e)

    def warn(file: str, msg: str):
        warnings.append({"file": file, "message": msg})

    # ── 1. manifest.yaml ──────────────────────────────────────────────────────
    mf = root / "manifest.yaml"
    if not mf.exists():
        err("manifest.yaml", "File not found — plugin cannot be loaded without a manifest")
    else:
        m_issues, m_warns = validate_manifest(mf)
        for iss in m_issues: err("manifest.yaml", iss)
        for w   in m_warns:  warn("manifest.yaml", w)

        mf_text = mf.read_text(encoding="utf-8", errors="replace")

        # Detect profile from manifest
        pm = re.search(r'profile:\s*"([^"]+)"', mf_text)
        if pm and pm.group(1) in REQUIRED_STRUCTURE:
            profile = pm.group(1)
        elif pm:
            warn("manifest.yaml", f"Unknown profile value: '{pm.group(1)}'")

        # Check plugin ID format
        im = re.search(r'id:\s*"([^"]+)"', mf_text)
        if im:
            pid_val = im.group(1)
            if not re.match(r'^com\.[a-z0-9_]+\.[a-z0-9_]+', pid_val):
                warn("manifest.yaml",
                     f"ID should follow 'com.vendor.name' format, got: '{pid_val}'")

        # Verify expected hooks for profile are declared
        for hook in HOOKS_BY_PROFILE.get(profile, []):
            if f"  {hook}:" not in mf_text:
                warn("manifest.yaml", f"Expected hook '{hook}' not declared for profile '{profile}'")

        # Commands section
        if "commands:" not in mf_text:
            warn("manifest.yaml", "No 'commands:' section found")
        else:
            if "title:" not in mf_text:
                warn("manifest.yaml", "Command entry appears to be missing a 'title:' field")

        # Panels for UI profiles
        if profile in PROFILES_WITH_UI and "panels:" not in mf_text:
            warn("manifest.yaml", f"Profile '{profile}' typically declares 'panels:' — none found")

    # ── 2. main.py ────────────────────────────────────────────────────────────
    main_py = root / "main.py"
    if not main_py.exists():
        err("main.py", "Entry point main.py not found")
    else:
        src = main_py.read_text(encoding="utf-8", errors="replace")

        if "def onLoad" not in src:
            err("main.py", "Required hook 'def onLoad(api)' not found")
        if "def onCommand" not in src:
            err("main.py", "Required hook 'def onCommand(api, commandId, args)' not found")

        for hook in HOOKS_BY_PROFILE.get(profile, []):
            if f"def {hook}" not in src:
                warn("main.py", f"Expected hook 'def {hook}' not implemented for profile '{profile}'")

        if AUTHOR_META["company"] not in src:
            warn("main.py", "Author company metadata not found in file header")

    # ── 3. Folder structure by profile ───────────────────────────────────────
    required_paths = REQUIRED_STRUCTURE.get(profile, REQUIRED_STRUCTURE["minimal"])
    for path_str in required_paths:
        p = root / path_str.rstrip("/")
        if path_str.endswith("/"):
            if not p.is_dir():
                warn("structure", f"Expected directory '{path_str}' not found "
                                  f"(required for profile '{profile}')")
        else:
            if not p.exists():
                err("structure", f"Required file '{path_str}' not found "
                                 f"(required for profile '{profile}')")

    # ── 4. UI files ───────────────────────────────────────────────────────────
    if profile in PROFILES_WITH_UI:
        html_f = root / "ui" / "panel.html"
        css_f  = root / "ui" / "panel.css"

        if not html_f.exists():
            err("ui/panel.html", "UI panel HTML file not found")
        else:
            html = html_f.read_text(encoding="utf-8", errors="replace")
            for tag in ("<div", "<button"):
                if tag not in html:
                    warn("ui/panel.html", f"Expected HTML element '{tag}' not found")
            if "<script" not in html and profile in ("advanced", "enterprise", "ui-heavy"):
                warn("ui/panel.html",
                     "No <script> element found — may be required for interactive panels")

        if not css_f.exists():
            err("ui/panel.css", "UI panel CSS file not found")
        else:
            css = css_f.read_text(encoding="utf-8", errors="replace")
            for sel in (".panel", "#output", "button"):
                if sel not in css:
                    warn("ui/panel.css", f"Expected CSS selector '{sel}' not found")

    # ── 5. config/default.json ────────────────────────────────────────────────
    cfg = root / "config" / "default.json"
    if not cfg.exists():
        warn("config/default.json", "Config file not found — settings will not be available")
    else:
        try:
            cfg_data = json.loads(cfg.read_text(encoding="utf-8"))
            if "__meta" not in cfg_data:
                warn("config/default.json", "Missing '__meta' section")
            else:
                meta = cfg_data["__meta"]
                if "plugin" not in meta:
                    warn("config/default.json", "__meta missing 'plugin' field")
                if "author" not in meta:
                    warn("config/default.json", "__meta missing 'author' field")
            if profile == "analysis" and "analysis" not in cfg_data:
                warn("config/default.json",
                     "Profile 'analysis' typically contains an 'analysis' config section")
            if profile in ("enterprise", "telemetry") and "telemetry" not in cfg_data:
                warn("config/default.json",
                     f"Profile '{profile}' typically contains a 'telemetry' config section")
            if profile == "database" and "db" not in cfg_data:
                warn("config/default.json",
                     "Profile 'database' typically contains a 'db' config section")
            if profile == "network" and "network" not in cfg_data:
                warn("config/default.json",
                     "Profile 'network' typically contains a 'network' config section")
        except json.JSONDecodeError as e:
            err("config/default.json", f"JSON parse error: {e}")

    # ── 6. SVG icons ─────────────────────────────────────────────────────────
    for icon_name in ("plugin.svg", "panel.svg"):
        icon_f = root / "icons" / icon_name
        if not icon_f.exists():
            warn(f"icons/{icon_name}", "Icon file not found")
        else:
            svg_text = icon_f.read_text(encoding="utf-8", errors="replace")
            if "<svg" not in svg_text:
                err(f"icons/{icon_name}", "Invalid SVG: <svg> opening tag missing")
            elif "</svg>" not in svg_text:
                err(f"icons/{icon_name}", "Invalid SVG: </svg> closing tag missing")

    for icon_name in ("toolbar.svg", "plugin_dark.svg", "plugin_symbolic.svg"):
        if not (root / "icons" / icon_name).exists():
            warn(f"icons/{icon_name}", "Optional icon variant not found")

    # ── 7. Optional recommended files ────────────────────────────────────────
    for fname, label in [
        ("README.txt",       "Plugin README"),
        ("plugin-info.json", "API manifest (plugin-info.json)"),
        ("integrity.json",   "Integrity hash file"),
        ("update.json",      "Auto-update descriptor"),
    ]:
        if not (root / fname).exists():
            warn(fname, f"{label} not found (recommended)")

    # ── 8. plugin-info.json validity ─────────────────────────────────────────
    pi = root / "plugin-info.json"
    if pi.exists():
        try:
            pi_data = json.loads(pi.read_text(encoding="utf-8"))
            for field in ("name", "id", "version", "api"):
                if field not in pi_data:
                    warn("plugin-info.json", f"Missing field: '{field}'")
            if "api" in pi_data:
                api_section = pi_data["api"]
                if "hooks" not in api_section:
                    warn("plugin-info.json", "api section missing 'hooks' list")
                if "permissions" not in api_section:
                    warn("plugin-info.json", "api section missing 'permissions' list")
        except json.JSONDecodeError as e:
            err("plugin-info.json", f"JSON parse error: {e}")

    # ── 9. integrity.json validity ────────────────────────────────────────────
    integ = root / "integrity.json"
    if integ.exists():
        try:
            integ_data = json.loads(integ.read_text(encoding="utf-8"))
            if "files" not in integ_data:
                warn("integrity.json", "Missing 'files' section")
            if "generator" not in integ_data:
                warn("integrity.json", "Missing 'generator' field")
        except json.JSONDecodeError as e:
            err("integrity.json", f"JSON parse error: {e}")

    # ── 10. Profile-specific library files ───────────────────────────────────
    lib_checks = {
        "advanced":   ["libs/helper.py"],
        "enterprise": ["libs/helper.py","libs/container.py","libs/events.py","libs/telemetry.py"],
        "ui-heavy":   ["libs/theme.py"],
        "analysis":   ["libs/analyzer.py","libs/reporter.py"],
        "terminal":   ["libs/shell.py"],
        "wizard":     ["libs/wizard_engine.py"],
        "telemetry":  ["libs/telemetry.py","libs/metrics.py"],
        "database":   ["libs/db.py"],
        "network":    ["libs/network.py"],
    }
    for lib_path in lib_checks.get(profile, []):
        if not (root / lib_path).exists():
            warn(lib_path, f"Expected library file for profile '{profile}' not found")

    # ── Build report ──────────────────────────────────────────────────────────
    status = "OK" if not errors else "ERROR"
    return {
        "plugin":        plugin_name,
        "profile":       profile,
        "status":        status,
        "generated":     datetime.now().isoformat(),
        "generator":     f"polsoft.ITS™ Plugin Generator v{VERSION}",
        "copyright":     AUTHOR_META["copy"],
        "errors":        errors,
        "warnings":      warnings,
        "error_count":   len(errors),
        "warning_count": len(warnings),
    }

# ══════════════════════════════════════════════════════════════════════════════
#  ZIP BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_zip(plugin_root: Path, name: str) -> Path:
    zp = plugin_root.parent / f"{name}.pits-plugin.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(plugin_root.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(plugin_root.parent))
    return zp

# ══════════════════════════════════════════════════════════════════════════════
#  GUI
# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk if TK_OK else object):  # type: ignore[misc]
    """Main GUI application window."""
    def __init__(self):
        super().__init__()
        self._lang      = "en"
        self._staged    = {}
        self._out_root  = None
        self._wiz_step  = 0
        self._wiz_data  = {}

        self._opts = {k: tk.BooleanVar(value=True) for k in (
            "tests","selftest","changelog","reqs","install",
            "diag","integrity","update","apimanif","pmmanif","metaplug",
            "autovalidate",
        )}

        self.title(LANG["en"]["title"])
        self.resizable(True, True)
        self.configure(bg="#0d0d18")
        self._build_ui()
        self._apply_lang()
        # size window to fit content after all widgets are built
        self.update_idletasks()
        w = max(self.winfo_reqwidth(),  820)
        h = max(self.winfo_reqheight(), 580)
        self.geometry(f"{w}x{h}")
        self.minsize(820, 580)

    # ── Translation helpers ───────────────────────────────────────────────────

    def _t(self, k): return LANG[self._lang].get(k, k)

    def _toggle_lang(self):
        self._lang = "pl" if self._lang == "en" else "en"
        self._apply_lang()

    def _apply_lang(self):
        L = LANG[self._lang]
        self.title(L["title"])
        self._lbl_title.config(text=L["title"])
        self._lbl_sub.config(text=L["subtitle"])
        self._btn_lang.config(text=L["lang_btn"])
        for i, key in enumerate(["tab_gen","tab_wizard","tab_tmpl",
                                  "tab_opts","tab_valid","tab_about"]):
            self._nb.tab(i, text=L[key])
        for attr, key in [
            ("_lf_name","plugin_name"), ("_lf_id","plugin_id"),
            ("_lf_author","author"),    ("_lf_license","license"),
            ("_lf_desc","description"), ("_lf_profile","profile"),
            ("_lf_icon","icon_style"),  ("_lf_cs","code_style"),
            ("_lf_layout","ui_layout"), ("_lf_out","out_dir"),
        ]:
            getattr(self, attr).config(text=L[key])
        self._btn_browse.config(text=L["browse"])
        self._btn_generate.config(text=L["generate"])
        self._btn_zip.config(text=L["build_zip"])
        self._btn_opendir.config(text=L["open_dir"])
        self._btn_copy.config(text=L["copy_btn"])
        self._lbl_files.config(text=L["files_label"])
        self._lbl_prev.config(text=L["preview"])
        self._lbl_opts_h.config(text=L["opts_extras"])
        for k, lbl in self._opt_labels.items():
            lbl.config(text=L.get(f"opt_{k}", k))
        # Templates tab
        self._lf_tmpl_dir.config(text=L["tmpl_dir_lbl"])
        self._btn_tmpl_dir.config(text=L["tmpl_dir_btn"])
        self._lf_tmpl_profile.config(text=L["tmpl_profile_lbl"])
        self._btn_tmpl_gen.config(text=L["tmpl_gen_btn"])
        self._btn_tmpl_valid.config(text=L["tmpl_valid_btn"])
        self._btn_tmpl_test.config(text=L["tmpl_test_btn"])
        self._lf_tmpl_out.config(text=L["tmpl_out_lbl"])
        # Validator tab
        self._lf_vpath.config(text=L["valid_path"])
        self._btn_vbrowse.config(text=L["valid_browse"])
        self._btn_vrun.config(text=L["validate"])
        self._lf_vfolder.config(text=L["valid_folder_lbl"])
        self._btn_vfolder_browse.config(text=L["valid_folder_btn"])
        self._btn_vplugin.config(text=L["validate_plugin"])
        self._btn_vintegrity.config(text=L["integrity_verify"])
        # About tab
        self._update_about_lang(self._lang)
        self._update_wizard_ui()

    # ── Style ─────────────────────────────────────────────────────────────────

    def _mk_style(self):
        s = ttk.Style(self); s.theme_use("clam")
        BG   = "#0d0d18"
        BG2  = "#111120"
        TAB  = "#161626"
        TABS = "#6C63FF"
        FG   = "#e8e6ff"
        MUT  = "#6a6890"
        s.configure("TNotebook",       background=BG,   borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab",   font=("Consolas",9,"bold"), padding=(14,6),
                    background=TAB, foreground=MUT, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", TABS),  ("active", "#1e1e32")],
              foreground=[("selected", FG),     ("active", "#b8b5d8")])
        s.configure("TFrame",       background=BG)
        s.configure("TCheckbutton", background=BG2, font=("Consolas",9),
                    foreground="#b8b5d8")

    def _ent(self, parent, val=""):
        e = tk.Entry(parent, font=("Consolas",10), relief="flat",
            bg="#181828", fg="#e8e6ff", insertbackground="#6C63FF",
            highlightthickness=1, highlightcolor="#6C63FF",
            highlightbackground="#1e1e32")
        e.insert(0, val); return e

    def _flbl(self, parent, attr, pady=(7,1)):
        lbl = tk.Label(parent, text="", font=("Consolas",8,"bold"),
                       fg="#6a6890", bg="#0d0d18", anchor="w")
        lbl.pack(fill="x", pady=pady); setattr(self, attr, lbl); return lbl

    # ── Main UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._mk_style()

        # Top bar
        bar = tk.Frame(self, bg="#0a0a14", height=52)
        bar.pack(fill="x"); bar.pack_propagate(False)
        # accent stripe at very top
        stripe = tk.Frame(self, bg="#6C63FF", height=2)
        stripe.place(x=0, y=0, relwidth=1)
        tk.Label(bar, text="◈", font=("Consolas",20), fg="#6C63FF", bg="#0a0a14").pack(side="left",padx=(14,6),pady=8)
        self._lbl_title = tk.Label(bar, text="", font=("Consolas",12,"bold"), fg="#e8e6ff", bg="#0a0a14")
        self._lbl_title.pack(side="left")
        self._lbl_sub = tk.Label(bar, text="", font=("Consolas",8), fg="#6a6890", bg="#0a0a14")
        self._lbl_sub.pack(side="left", padx=(8,0))
        self._btn_lang = tk.Button(bar, text="PL", font=("Consolas",9,"bold"),
            fg="#e8e6ff", bg="#6C63FF", relief="flat", padx=10, cursor="hand2",
            activebackground="#8B85FF", activeforeground="white",
            command=self._toggle_lang)
        self._btn_lang.pack(side="right", padx=12, pady=12)

        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=0, pady=0)
        tabs = [ttk.Frame(self._nb) for _ in range(6)]
        for t in tabs:
            t.columnconfigure(0, weight=1)
            t.rowconfigure(0, weight=1)
            self._nb.add(t, text="")
        (self._tab_gen, self._tab_wiz, self._tab_tmpl,
         self._tab_opts, self._tab_valid, self._tab_about) = tabs

        self._build_gen()
        self._build_wizard()
        self._build_tmpl()
        self._build_opts()
        self._build_valid()
        self._build_about()

    # ── Generator tab ─────────────────────────────────────────────────────────

    def _build_gen(self):
        tab = self._tab_gen
        tab.columnconfigure(0, weight=2, minsize=260)
        tab.columnconfigure(1, weight=3)
        tab.rowconfigure(0, weight=1)

        L = tk.Frame(tab, bg="#0d0d18", padx=13, pady=10)
        L.grid(row=0, column=0, sticky="nsew")
        L.columnconfigure(0, weight=1)

        tk.Frame(tab, bg="#1e1e32", width=1).grid(row=0, column=0, sticky="nse")

        R = tk.Frame(tab, bg="#111120", padx=11, pady=10)
        R.grid(row=0, column=1, sticky="nsew")
        R.columnconfigure(0, weight=1)
        R.rowconfigure(3, weight=1)

        # Left form
        self._flbl(L, "_lf_name")
        self._e_name = self._ent(L,"MyPlugin"); self._e_name.pack(fill="x",ipady=3)

        self._flbl(L, "_lf_id")
        self._e_id = self._ent(L,"com.polsoft.myplugin"); self._e_id.pack(fill="x",ipady=3)

        self._flbl(L, "_lf_author")
        self._e_author = self._ent(L,"Sebastian Januchowski"); self._e_author.pack(fill="x",ipady=3)

        self._flbl(L, "_lf_license")
        self._e_license = self._ent(L,"MIT"); self._e_license.pack(fill="x",ipady=3)

        self._flbl(L, "_lf_desc")
        self._e_desc = tk.Text(L, font=("Consolas",10), height=2, relief="flat",
            bg="#181828", fg="#e8e6ff", insertbackground="#6C63FF",
            highlightthickness=1, highlightcolor="#6C63FF", highlightbackground="#1e1e32")
        self._e_desc.insert("1.0","Plugin dla polsoft.ITS™ Script Editor.")
        self._e_desc.pack(fill="x")

        # Profile (2×5 grid)
        self._flbl(L, "_lf_profile")
        self._pvar = tk.StringVar(value="minimal")
        pf = tk.Frame(L, bg="#0d0d18"); pf.pack(fill="x")
        for i,(k,v) in enumerate(PROFILES.items()):
            tk.Radiobutton(pf, text=v["en"], variable=self._pvar, value=k,
                font=("Consolas",8), bg="#0d0d18", fg="#b8b5d8",
                activebackground="#0d0d18", selectcolor="#6C63FF"
            ).grid(row=i//5, column=i%5, sticky="w", padx=1, pady=1)

        # Icon style
        self._flbl(L, "_lf_icon")
        self._ivar = tk.StringVar(value="dark")
        ic = tk.Frame(L, bg="#0d0d18"); ic.pack(fill="x")
        for i,s in enumerate(ICON_STYLES):
            tk.Radiobutton(ic, text=s, variable=self._ivar, value=s,
                font=("Consolas",8), bg="#0d0d18", fg="#b8b5d8",
                activebackground="#0d0d18", selectcolor="#6C63FF"
            ).grid(row=0, column=i, sticky="w", padx=1)

        # Code style
        self._flbl(L, "_lf_cs")
        self._csvar = tk.StringVar(value="PEP8")
        csf = tk.Frame(L, bg="#0d0d18"); csf.pack(fill="x")
        for i,s in enumerate(CODE_STYLES):
            tk.Radiobutton(csf, text=s, variable=self._csvar, value=s,
                font=("Consolas",8), bg="#0d0d18", fg="#b8b5d8",
                activebackground="#0d0d18", selectcolor="#6C63FF"
            ).grid(row=0, column=i, sticky="w", padx=1)

        # UI Layout
        self._flbl(L, "_lf_layout")
        self._lvar = tk.StringVar(value="sidebar")
        lf = tk.Frame(L, bg="#0d0d18"); lf.pack(fill="x")
        for i,s in enumerate(UI_LAYOUTS):
            tk.Radiobutton(lf, text=s, variable=self._lvar, value=s,
                font=("Consolas",8), bg="#0d0d18", fg="#b8b5d8",
                activebackground="#0d0d18", selectcolor="#6C63FF"
            ).grid(row=0, column=i, sticky="w", padx=1)

        # Output dir
        self._flbl(L, "_lf_out")
        df = tk.Frame(L, bg="#0d0d18"); df.pack(fill="x")
        self._e_out = self._ent(df, str(Path.home()/"Desktop"))
        self._e_out.pack(side="left", fill="x", expand=True, ipady=3)
        self._btn_browse = tk.Button(df, text="Browse...", font=("Consolas",8), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2", command=self._browse, padx=6, pady=3)
        self._btn_browse.pack(side="left", padx=(5,0))

        # Action buttons
        self._btn_generate = tk.Button(L, text="", font=("Consolas",11,"bold"),
            relief="flat", bg="#6C63FF", fg="white", activebackground="#8B85FF",
            cursor="hand2", pady=8, command=self._generate)
        self._btn_generate.pack(fill="x", pady=(10,3))

        self._btn_zip = tk.Button(L, text="", font=("Consolas",9),
            relief="flat", bg="#181828", fg="#e8e6ff",
            cursor="hand2", pady=5, command=self._do_zip, state="disabled")
        self._btn_zip.pack(fill="x", pady=(0,3))

        self._status = tk.StringVar(value="")
        tk.Label(L, textvariable=self._status, font=("Consolas",8),
            fg="#1D9E75", bg="#0d0d18", anchor="w", wraplength=215).pack(fill="x")

        # Right panel
        self._lbl_files = tk.Label(R, text="", font=("Consolas",9,"bold"),
            fg="#8B85FF", bg="#111120", anchor="w")
        self._lbl_files.grid(row=0, column=0, sticky="ew", pady=(0,3))

        self._file_lb = tk.Listbox(R, font=("Consolas",9), relief="flat",
            bg="#181828", fg="#e8e6ff", selectbackground="#6C63FF", selectforeground="white",
            height=8, highlightthickness=1, highlightcolor="#6C63FF",
            highlightbackground="#1e1e32", activestyle="none")
        self._file_lb.grid(row=1, column=0, sticky="ew")
        self._file_lb.bind("<<ListboxSelect>>", self._on_sel)

        self._lbl_prev = tk.Label(R, text="", font=("Consolas",9,"bold"),
            fg="#8B85FF", bg="#111120", anchor="w")
        self._lbl_prev.grid(row=2, column=0, sticky="ew", pady=(7,2))

        pf2 = tk.Frame(R, bg="#111120")
        pf2.grid(row=3, column=0, sticky="nsew")
        pf2.columnconfigure(0, weight=1); pf2.rowconfigure(0, weight=1)

        self._prev = tk.Text(pf2, font=("Consolas",9), relief="flat",
            bg="#0a0a14", fg="#c9c5ff", wrap="none", highlightthickness=0, state="disabled")
        sy = ttk.Scrollbar(pf2, orient="vertical", command=self._prev.yview)
        sx = ttk.Scrollbar(pf2, orient="horizontal", command=self._prev.xview)
        self._prev.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        self._prev.grid(row=0, column=0, sticky="nsew")

        bf = tk.Frame(R, bg="#111120")
        bf.grid(row=4, column=0, sticky="ew", pady=(5,0))
        self._btn_copy = tk.Button(bf, text="", font=("Consolas",9), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2", command=self._copy, padx=8, pady=3)
        self._btn_copy.pack(side="left")
        self._btn_opendir = tk.Button(bf, text="", font=("Consolas",9), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2", command=self._opendir,
            padx=8, pady=3, state="disabled")
        self._btn_opendir.pack(side="left", padx=(7,0))

    # ── Wizard tab ────────────────────────────────────────────────────────────

    def _build_wizard(self):
        tab = self._tab_wiz
        tab.columnconfigure(0, weight=1); tab.rowconfigure(1, weight=1)

        # Step indicator bar
        self._wiz_bar = tk.Frame(tab, bg="#0a0a14", height=34)
        self._wiz_bar.grid(row=0, column=0, sticky="ew")
        self._wiz_bar.grid_propagate(False)
        self._wiz_step_labels = []
        for i in range(4):
            lbl = tk.Label(self._wiz_bar, text=f"● {i+1}", font=("Consolas",9),
                           fg="#2e2e50", bg="#0a0a14", padx=8)
            lbl.pack(side="left", pady=8)
            self._wiz_step_labels.append(lbl)

        # Content frame
        self._wiz_content = tk.Frame(tab, bg="#0d0d18", padx=24, pady=16)
        self._wiz_content.grid(row=1, column=0, sticky="nsew")
        self._wiz_content.columnconfigure(0, weight=1)

        # Nav bar
        nav = tk.Frame(tab, bg="#0a0a14", height=40)
        nav.grid(row=2, column=0, sticky="ew"); nav.grid_propagate(False)
        tk.Frame(tab, bg="#1e1e32", height=1).grid(row=2, column=0, sticky="new")
        self._wiz_btn_back = tk.Button(nav, text="← Back", font=("Consolas",9,"bold"),
            relief="flat", bg="#1e1e32", fg="#b8b5d8", padx=10,
            cursor="hand2", command=self._wiz_back)
        self._wiz_btn_back.pack(side="left", padx=12, pady=6)
        self._wiz_btn_next = tk.Button(nav, text="Next →", font=("Consolas",9,"bold"),
            relief="flat", bg="#6C63FF", fg="white", padx=10,
            cursor="hand2", command=self._wiz_next)
        self._wiz_btn_next.pack(side="right", padx=12, pady=6)

        self._wiz_step   = 0
        self._wiz_data   = {}
        self._wiz_fields = {}
        self._render_wiz_step()

    def _update_wizard_ui(self):
        L = LANG[self._lang]
        step_keys = ["wiz_step1","wiz_step2","wiz_step3","wiz_step4"]
        for i, lbl in enumerate(self._wiz_step_labels):
            lbl.config(text=f"● {L.get(step_keys[i], f'Step {i+1}')}")
        self._wiz_btn_back.config(text=L["wiz_back"])
        self._wiz_btn_next.config(text=L["wiz_finish"] if self._wiz_step == 3 else L["wiz_next"])
        self._render_wiz_step()

    def _render_wiz_step(self):
        for w in self._wiz_content.winfo_children():
            w.destroy()
        self._wiz_fields = {}
        # Highlight active step
        for i, lbl in enumerate(self._wiz_step_labels):
            lbl.config(fg="#e8e6ff" if i == self._wiz_step else "#3a3a5a")

        step = self._wiz_step
        L = LANG[self._lang]
        f = self._wiz_content

        def add_field(label, key, default=""):
            tk.Label(f, text=label, font=("Consolas",8,"bold"),
                     fg="#6a6890", bg="#0d0d18", anchor="w").pack(fill="x", pady=(8,1))
            e = self._ent(f, self._wiz_data.get(key, default))
            e.pack(fill="x", ipady=3)
            self._wiz_fields[key] = e

        def add_radio(label, key, options, default=None):
            tk.Label(f, text=label, font=("Consolas",8,"bold"),
                     fg="#6a6890", bg="#0d0d18", anchor="w").pack(fill="x", pady=(8,1))
            var = tk.StringVar(value=self._wiz_data.get(key, default or options[0]))
            rf = tk.Frame(f, bg="#0d0d18"); rf.pack(fill="x")
            for i, opt in enumerate(options):
                tk.Radiobutton(rf, text=opt, variable=var, value=opt,
                    font=("Consolas",9), bg="#0d0d18", fg="#b8b5d8",
                    activebackground="#0d0d18", selectcolor="#6C63FF"
                ).grid(row=i//4, column=i%4, sticky="w", padx=2, pady=1)
            self._wiz_fields[key] = var

        if step == 0:
            tk.Label(f, text=L["wiz_step1"], font=("Consolas",11,"bold"),
                     fg="#8B85FF", bg="#0d0d18").pack(anchor="w", pady=(0,8))
            add_field(L["plugin_name"], "name",    "MyPlugin")
            add_field(L["plugin_id"],   "id",      "com.polsoft.myplugin")
            add_field(L["author"],      "author",  "Sebastian Januchowski")
            add_field(L["license"],     "license", "MIT")
            add_field(L["description"], "desc",    "Plugin dla polsoft.ITS™ Script Editor.")

        elif step == 1:
            tk.Label(f, text=L["wiz_step2"], font=("Consolas",11,"bold"),
                     fg="#8B85FF", bg="#0d0d18").pack(anchor="w", pady=(0,8))
            add_radio(L["profile"],    "profile",    list(PROFILES.keys()),    "minimal")
            add_radio(L["icon_style"], "icon_style", ICON_STYLES,              "dark")
            add_radio(L["code_style"], "code_style", CODE_STYLES,              "PEP8")
            add_radio(L["ui_layout"],  "ui_layout",  UI_LAYOUTS,               "sidebar")

        elif step == 2:
            tk.Label(f, text=L["wiz_step3"], font=("Consolas",11,"bold"),
                     fg="#8B85FF", bg="#0d0d18").pack(anchor="w", pady=(0,8))
            profile = self._wiz_data.get("profile","minimal")
            hooks   = HOOKS_BY_PROFILE.get(profile, ["onLoad","onCommand"])
            tk.Label(f, text="Active hooks:", font=("Consolas",8,"bold"),
                     fg="#6a6890", bg="#0d0d18", anchor="w").pack(fill="x", pady=(8,2))
            hf = tk.Frame(f, bg="#0d0d18"); hf.pack(fill="x")
            for i, hk in enumerate(hooks):
                tk.Label(hf, text=f"✓ {hk}", font=("Consolas",9),
                         fg="#1D9E75", bg="#0d0d18").grid(row=i//2, column=i%2, sticky="w", padx=4, pady=1)
            perms = PERMS_BY_PROFILE.get(profile, [])
            tk.Label(f, text="Permissions:", font=("Consolas",8,"bold"),
                     fg="#6a6890", bg="#0d0d18", anchor="w").pack(fill="x", pady=(10,2))
            for p in perms:
                tk.Label(f, text=f"  • {p}", font=("Consolas",9),
                         fg="#9994cc", bg="#0d0d18", anchor="w").pack(fill="x")
            add_field(L["out_dir"], "out_dir", str(Path.home()/"Desktop"))

        elif step == 3:
            tk.Label(f, text=L["wiz_step4"], font=("Consolas",11,"bold"),
                     fg="#8B85FF", bg="#0d0d18").pack(anchor="w", pady=(0,10))
            summary = [
                ("Plugin", self._wiz_data.get("name","?")),
                ("ID",     self._wiz_data.get("id","?")),
                ("Author", self._wiz_data.get("author","?")),
                ("Profile",self._wiz_data.get("profile","minimal")),
                ("Icon",   self._wiz_data.get("icon_style","dark")),
                ("Code",   self._wiz_data.get("code_style","PEP8")),
                ("Layout", self._wiz_data.get("ui_layout","sidebar")),
                ("Output", self._wiz_data.get("out_dir","?")),
            ]
            for label, val in summary:
                row = tk.Frame(f, bg="#0d0d18"); row.pack(fill="x", pady=1)
                tk.Label(row, text=f"{label}:", font=("Consolas",9,"bold"),
                         fg="#6a6890", bg="#0d0d18", width=9, anchor="e").pack(side="left")
                tk.Label(row, text=val, font=("Consolas",9),
                         fg="#b8b5d8", bg="#0d0d18", anchor="w").pack(side="left", padx=(6,0))

        self._wiz_btn_next.config(
            text=L["wiz_finish"] if step == 3 else L["wiz_next"]
        )
        self._wiz_btn_back.config(state="disabled" if step == 0 else "normal")

    def _wiz_collect(self):
        for key, widget in self._wiz_fields.items():
            if isinstance(widget, tk.StringVar):
                self._wiz_data[key] = widget.get()
            elif hasattr(widget, "get"):
                val = widget.get().strip() if isinstance(widget.get(), str) else widget.get("1.0","end").strip()
                if val: self._wiz_data[key] = val

    def _wiz_next(self):
        self._wiz_collect()
        if self._wiz_step < 3:
            self._wiz_step += 1
            self._render_wiz_step()
        else:
            self._generate_from_wizard()

    def _wiz_back(self):
        if self._wiz_step > 0:
            self._wiz_step -= 1
            self._render_wiz_step()

    def _generate_from_wizard(self):
        d = self._wiz_data
        out = Path(d.get("out_dir", str(Path.home()/"Desktop")))
        opts = {k: v.get() for k,v in self._opts.items()}
        try:
            files = generate_plugin(
                out,
                d.get("name","MyPlugin"), d.get("id","com.polsoft.myplugin"),
                d.get("desc","Plugin."),  d.get("author","Sebastian Januchowski"),
                d.get("license","MIT"),   d.get("profile","minimal"),
                d.get("icon_style","dark"), d.get("code_style","PEP8"),
                d.get("ui_layout","sidebar"),
                **{f"opt_{k}": v for k,v in opts.items()}
            )
            self._staged   = files
            self._out_root = out / d.get("name","MyPlugin")
            self._populate_file_list()

            val_key = "diagnostics/plugin_report.json"
            if val_key in files:
                try:
                    rpt = json.loads(files[val_key])
                    val_hint = (f"  ✓ Validated: {rpt['error_count']} errors, "
                                f"{rpt['warning_count']} warnings"
                                if rpt["status"] == "OK"
                                else f"  ✗ Validation: {rpt['error_count']} error(s)")
                except Exception:
                    val_hint = ""
            else:
                val_hint = ""

            self._status.set(f"✓ {self._t('success_msg')}  → {self._out_root}{val_hint}")
            self._btn_opendir.config(state="normal")
            self._btn_zip.config(state="normal")

            if opts.get("autovalidate") and self._out_root:
                self._e_vfolder.delete(0,"end")
                self._e_vfolder.insert(0, str(self._out_root))
                self._nb.select(4)  # switch to Validator tab
            else:
                self._nb.select(0)  # switch to Generator tab to see files
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))

    # ── Templates tab ─────────────────────────────────────────────────────────

    def _build_tmpl(self):
        f = tk.Frame(self._tab_tmpl, bg="#0d0d18", padx=24, pady=18)
        f.grid(row=0, column=0, sticky="nsew")
        self._tab_tmpl.columnconfigure(0, weight=1)
        self._tab_tmpl.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1); f.rowconfigure(7, weight=1)

        # Templates dir
        self._lf_tmpl_dir = tk.Label(f, text="", font=("Consolas",8,"bold"),
            fg="#6a6890", bg="#0d0d18", anchor="w")
        self._lf_tmpl_dir.grid(row=0, column=0, sticky="ew")
        tr = tk.Frame(f, bg="#0d0d18"); tr.grid(row=1, column=0, sticky="ew", pady=(2,4))
        tr.columnconfigure(0, weight=1)
        self._e_tmpl_dir = self._ent(tr, str(Path.cwd() / "templates"))
        self._e_tmpl_dir.grid(row=0, column=0, sticky="ew", ipady=3)
        self._btn_tmpl_dir = tk.Button(tr, text="", font=("Consolas",8), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2",
            command=self._tmpl_dir_browse, padx=6, pady=3)
        self._btn_tmpl_dir.grid(row=0, column=1, padx=(5,0))

        # Template profile selector
        self._lf_tmpl_profile = tk.Label(f, text="", font=("Consolas",8,"bold"),
            fg="#6a6890", bg="#0d0d18", anchor="w")
        self._lf_tmpl_profile.grid(row=2, column=0, sticky="ew", pady=(6,0))
        self._tmpl_pvar = tk.StringVar(value="minimal")
        tpf = tk.Frame(f, bg="#0d0d18"); tpf.grid(row=3, column=0, sticky="ew", pady=(2,6))
        for i, (k, v) in enumerate(PROFILES.items()):
            tk.Radiobutton(tpf, text=v["en"], variable=self._tmpl_pvar, value=k,
                font=("Consolas",8), bg="#0d0d18", fg="#b8b5d8",
                activebackground="#0d0d18", selectcolor="#6C63FF"
            ).grid(row=i//5, column=i%5, sticky="w", padx=1, pady=1)

        # Action buttons row
        btn_row = tk.Frame(f, bg="#0d0d18")
        btn_row.grid(row=4, column=0, sticky="ew", pady=(0,6))
        btn_row.columnconfigure((0,1,2), weight=1)
        self._btn_tmpl_gen = tk.Button(btn_row, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#6C63FF", fg="white", cursor="hand2",
            pady=5, command=self._tmpl_generate)
        self._btn_tmpl_gen.grid(row=0, column=0, sticky="ew", padx=(0,3))
        self._btn_tmpl_valid = tk.Button(btn_row, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#1e1e32", fg="#b8b5d8", cursor="hand2",
            pady=5, command=self._tmpl_validate)
        self._btn_tmpl_valid.grid(row=0, column=1, sticky="ew", padx=3)
        self._btn_tmpl_test = tk.Button(btn_row, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#0e3d1a", fg="#1D9E75", cursor="hand2",
            pady=5, command=self._tmpl_test)
        self._btn_tmpl_test.grid(row=0, column=2, sticky="ew", padx=(3,0))

        # Test output dir
        self._lf_tmpl_out = tk.Label(f, text="", font=("Consolas",8,"bold"),
            fg="#6a6890", bg="#0d0d18", anchor="w")
        self._lf_tmpl_out.grid(row=5, column=0, sticky="ew")
        tor = tk.Frame(f, bg="#0d0d18"); tor.grid(row=6, column=0, sticky="ew", pady=(2,4))
        tor.columnconfigure(0, weight=1)
        self._e_tmpl_out = self._ent(tor, str(Path.home() / "Desktop"))
        self._e_tmpl_out.grid(row=0, column=0, sticky="ew", ipady=3)
        tk.Button(tor, text="...", font=("Consolas",8), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2", padx=6, pady=3,
            command=lambda: self._pick_dir(self._e_tmpl_out)
        ).grid(row=0, column=1, padx=(5,0))

        # Output area
        self._t_out = tk.Text(f, font=("Consolas",9), relief="flat",
            bg="#0a0a14", fg="#c9c5ff", highlightthickness=0, state="disabled")
        self._t_out.grid(row=7, column=0, sticky="nsew")

    # ── Options tab ───────────────────────────────────────────────────────────

    def _build_opts(self):
        f = tk.Frame(self._tab_opts, bg="#0d0d18", padx=24, pady=18)
        f.grid(row=0, column=0, sticky="nsew")
        self._tab_opts.columnconfigure(0, weight=1)
        self._tab_opts.rowconfigure(0, weight=1)
        self._lbl_opts_h = tk.Label(f, text="", font=("Consolas",10,"bold"),
            fg="#8B85FF", bg="#0d0d18", anchor="w")
        self._lbl_opts_h.pack(fill="x", pady=(0,12))
        self._opt_labels = {}
        for k in ("tests","selftest","changelog","reqs","install",
                  "diag","integrity","update","apimanif","pmmanif","metaplug",
                  "autovalidate"):
            row = tk.Frame(f, bg="#0d0d18"); row.pack(fill="x", pady=2)
            # separator before autovalidate
            if k == "autovalidate":
                tk.Frame(f, bg="#2a2a42", height=1).pack(fill="x", pady=(6,2))
                row = tk.Frame(f, bg="#0d0d18"); row.pack(fill="x", pady=2)
            ttk.Checkbutton(row, variable=self._opts[k]).pack(side="left")
            lbl = tk.Label(row, text="", font=("Consolas",9),
                           fg="#b8b5d8", bg="#0d0d18", anchor="w")
            lbl.pack(side="left", padx=(5,0))
            self._opt_labels[k] = lbl

    # ── Validator tab ─────────────────────────────────────────────────────────

    def _build_valid(self):
        f = tk.Frame(self._tab_valid, bg="#0d0d18", padx=24, pady=18)
        f.grid(row=0, column=0, sticky="nsew")
        self._tab_valid.columnconfigure(0, weight=1)
        self._tab_valid.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1); f.rowconfigure(5, weight=1)

        # ── Section 1: manifest.yaml validator ────────────────────────────────
        self._lf_vpath = tk.Label(f, text="", font=("Consolas",8,"bold"),
            fg="#6a6890", bg="#0d0d18", anchor="w")
        self._lf_vpath.grid(row=0, column=0, sticky="ew")

        vr = tk.Frame(f, bg="#0d0d18"); vr.grid(row=1, column=0, sticky="ew", pady=(2,4))
        vr.columnconfigure(0, weight=1)
        self._e_vpath = self._ent(vr,"")
        self._e_vpath.grid(row=0, column=0, sticky="ew", ipady=3)
        self._btn_vbrowse = tk.Button(vr, text="", font=("Consolas",8), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2", command=self._vbrowse, padx=6, pady=3)
        self._btn_vbrowse.grid(row=0, column=1, padx=(5,0))

        self._btn_vrun = tk.Button(f, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#6C63FF", fg="white", cursor="hand2",
            pady=5, command=self._vrun)
        self._btn_vrun.grid(row=2, column=0, sticky="ew", pady=(0,8))

        # Separator
        sep = tk.Frame(f, bg="#2a2a42", height=1)
        sep.grid(row=3, column=0, sticky="ew", pady=(0,8))

        # ── Section 2: full plugin folder validator ────────────────────────────
        self._lf_vfolder = tk.Label(f, text="", font=("Consolas",8,"bold"),
            fg="#6a6890", bg="#0d0d18", anchor="w")
        self._lf_vfolder.grid(row=3, column=0, sticky="ew", pady=(6,0))

        vfr = tk.Frame(f, bg="#0d0d18"); vfr.grid(row=4, column=0, sticky="ew", pady=(2,4))
        vfr.columnconfigure(0, weight=1)
        self._e_vfolder = self._ent(vfr, "")
        self._e_vfolder.grid(row=0, column=0, sticky="ew", ipady=3)
        self._btn_vfolder_browse = tk.Button(
            vfr, text="", font=("Consolas",8), relief="flat",
            bg="#151525", fg="#b8b5d8", cursor="hand2",
            command=self._vfolder_browse, padx=6, pady=3)
        self._btn_vfolder_browse.grid(row=0, column=1, padx=(5,0))

        self._btn_vplugin = tk.Button(f, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#1e1e32", fg="#b8b5d8", cursor="hand2",
            pady=5, command=self._vplugin_run)
        self._btn_vplugin.grid(row=5, column=0, sticky="ew", pady=(0,4))

        # SHA-256 integrity verify
        self._btn_vintegrity = tk.Button(f, text="", font=("Consolas",9,"bold"),
            relief="flat", bg="#1e1e32", fg="#b8b5d8", cursor="hand2",
            pady=5, command=self._vinteg_run)
        self._btn_vintegrity.grid(row=6, column=0, sticky="ew", pady=(0,8))

        # ── Shared output ──────────────────────────────────────────────────────
        self._v_out = tk.Text(f, font=("Consolas",9), relief="flat",
            bg="#0a0a14", fg="#c9c5ff", highlightthickness=0, state="disabled")
        self._v_out.grid(row=7, column=0, sticky="nsew")
        f.rowconfigure(7, weight=1)

    # ── About tab ─────────────────────────────────────────────────────────────

    def _build_about(self):
        f = tk.Frame(self._tab_about, bg="#0d0d18")
        f.grid(row=0, column=0, sticky="nsew")
        self._tab_about.columnconfigure(0, weight=1)
        self._tab_about.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)

        # Full-size inner frame that holds the centred content via place
        inner = tk.Frame(f, bg="#0d0d18")
        inner.grid(row=0, column=0, sticky="nsew")
        inner.columnconfigure(0, weight=1)
        inner.rowconfigure(0, weight=1)

        # Content wrapper — centred inside inner
        content = tk.Frame(inner, bg="#0d0d18")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Logo glyph
        tk.Label(content, text="◈", font=("Consolas", 38), fg="#6C63FF",
                 bg="#0d0d18").pack(pady=(0, 4))

        # App title
        tk.Label(content,
                 text=f"polsoft.ITS\u2122 Plugin Generator",
                 font=("Consolas", 15, "bold"), fg="#e8e6ff",
                 bg="#0d0d18").pack()

        # Version badge
        tk.Label(content, text=f"v{VERSION}",
                 font=("Consolas", 10), fg="#6C63FF",
                 bg="#0d0d18").pack(pady=(2, 18))

        # Top separator
        tk.Frame(content, bg="#1e1e32", height=1, width=340).pack(pady=(0, 18))

        # Author info rows — (label key, value) pairs
        rows_pl = [
            ("Programista", AUTHOR_META["name"]),
            ("Firma",       AUTHOR_META["company"]),
            ("Kontakt",     AUTHOR_META["email"]),
            ("GitHub",      AUTHOR_META["github"]),
        ]
        rows_en = [
            ("Developer",   AUTHOR_META["name"]),
            ("Company",     AUTHOR_META["company"]),
            ("Contact",     AUTHOR_META["email"]),
            ("GitHub",      AUTHOR_META["github"]),
        ]
        info_grid = tk.Frame(content, bg="#0d0d18")
        info_grid.pack(padx=20)
        info_grid.columnconfigure(1, weight=1)
        self._about_key_labels = []
        self._about_val_labels = []
        for i, (k, v) in enumerate(rows_en):
            kl = tk.Label(info_grid, text=k + ":", font=("Consolas", 9, "bold"),
                          fg="#6a6890", bg="#0d0d18", anchor="e", width=11)
            kl.grid(row=i, column=0, sticky="e", padx=(0, 14), pady=4)
            vl = tk.Label(info_grid, text=v, font=("Consolas", 9),
                          fg="#b8b5d8", bg="#0d0d18", anchor="w")
            vl.grid(row=i, column=1, sticky="w", pady=4)
            self._about_key_labels.append((kl, rows_pl[i][0], rows_en[i][0]))
            self._about_val_labels.append(vl)

        # Bottom separator + copyright
        tk.Frame(content, bg="#1e1e32", height=1, width=340).pack(pady=(18, 14))
        self._about_copy = tk.Label(content,
            text=AUTHOR_META["copy"],
            font=("Consolas", 8), fg="#3a3a5a", bg="#0d0d18")
        self._about_copy.pack()
        self._about_rights = tk.Label(content, text="",
            font=("Consolas", 8), fg="#3a3a5a", bg="#0d0d18")
        self._about_rights.pack(pady=(2, 0))

    def _update_about_lang(self, lang):
        """Refresh about tab text for current language."""
        if not hasattr(self, "_about_key_labels"):
            return
        rows_pl = ["Programista", "Firma", "Kontakt", "GitHub"]
        rows_en = ["Developer",   "Company", "Contact", "GitHub"]
        keys    = rows_pl if lang == "pl" else rows_en
        for (kl, pl_k, en_k), key in zip(self._about_key_labels, keys):
            kl.config(text=key + ":")
        rights = "Wszelkie prawa zastrzeżone." if lang == "pl" else "All rights reserved."
        self._about_rights.config(text=rights)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self._e_out.get())
        if d: self._e_out.delete(0,"end"); self._e_out.insert(0,d)

    def _vbrowse(self):
        p = filedialog.askopenfilename(filetypes=[("YAML","*.yaml"),("All","*.*")])
        if p: self._e_vpath.delete(0,"end"); self._e_vpath.insert(0,p)

    def _vfolder_browse(self):
        d = filedialog.askdirectory()
        if d: self._e_vfolder.delete(0,"end"); self._e_vfolder.insert(0,d)

    def _v_write(self, text: str):
        """Write text to the shared validator output widget."""
        self._v_out.config(state="normal")
        self._v_out.delete("1.0","end")
        self._v_out.insert("end", text)
        if not YAML_OK:
            self._v_out.insert("end",
                "\n[Tip: pip install pyyaml — for full YAML validation]\n")
        self._v_out.config(state="disabled")

    def _t_write(self, text: str):
        """Write text to the Templates tab output widget."""
        self._t_out.config(state="normal")
        self._t_out.delete("1.0","end")
        self._t_out.insert("end", text)
        if not JINJA2_OK:
            self._t_out.insert("end",
                "\n[Tip: pip install jinja2 — full Jinja2 template rendering]\n")
        self._t_out.config(state="disabled")

    def _pick_dir(self, entry_widget):
        """Browse for a directory and fill the given Entry widget."""
        d = filedialog.askdirectory()
        if d:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d)

    def _tmpl_dir_browse(self):
        d = filedialog.askdirectory()
        if d:
            self._e_tmpl_dir.delete(0,"end")
            self._e_tmpl_dir.insert(0, d)

    def _tmpl_generate(self):
        """Generate .j2 template files for the chosen profile."""
        profile = self._tmpl_pvar.get()
        base    = Path(self._e_tmpl_dir.get().strip() or "templates")
        out_dir = base / profile
        try:
            staged = gen_j2_templates(profile, out_dir)
            lines = [f"✓ Generated {len(staged)} template files\n",
                     f"  Profile: {profile}\n",
                     f"  Directory: {out_dir}\n\n"]
            for rel in sorted(staged.keys()):
                lines.append(f"  {rel}\n")
            self._t_write("".join(lines))
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))

    def _tmpl_validate(self):
        """Validate the template directory for the chosen profile."""
        profile  = self._tmpl_pvar.get()
        base     = Path(self._e_tmpl_dir.get().strip() or "templates")
        tmpl_dir = base / profile
        try:
            report = validate_template(tmpl_dir)
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))
            return

        # Save report
        try:
            (tmpl_dir / "diagnostics").mkdir(parents=True, exist_ok=True)
            (tmpl_dir / "diagnostics" / "template_report.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass

        icon = "✓" if report["status"] == "OK" else "✗"
        lines = [f"{icon} Template: {profile}  |  Status: {report['status']}\n",
                 f"  .j2 files found: {report.get('j2_files_found',0)}\n",
                 f"  Errors: {report['error_count']}   Warnings: {report['warning_count']}\n\n"]
        if report["errors"]:
            lines.append(f"✗ Errors ({report['error_count']}):\n")
            for e in report["errors"]:
                lines.append(f"  • [{e['file']}] {e['message']}\n")
        if report["warnings"]:
            lines.append(f"\n⚠ Warnings ({report['warning_count']}):\n")
            for w in report["warnings"]:
                lines.append(f"  ○ [{w['file']}] {w['message']}\n")
        if not report["errors"] and not report["warnings"]:
            lines.append("  No issues found.\n")
        lines.append(f"\n  Report → diagnostics/template_report.json\n")
        self._t_write("".join(lines))

    def _tmpl_test(self):
        """Generate a test plugin from the chosen template profile."""
        profile  = self._tmpl_pvar.get()
        base     = Path(self._e_tmpl_dir.get().strip() or "templates")
        tmpl_dir = base / profile
        out_dir  = Path(self._e_tmpl_out.get().strip() or str(Path.home()/"Desktop"))

        if not tmpl_dir.is_dir():
            # Auto-generate templates first if they don't exist
            try:
                gen_j2_templates(profile, tmpl_dir)
            except Exception as e:
                messagebox.showerror(self._t("err_title"), f"Cannot create templates: {e}")
                return

        test_name = f"Test_{profile.replace('-','_').title()}"
        try:
            staged = generate_from_template(
                tmpl_dir, out_dir,
                name=test_name,
                pid=f"com.polsoft.test.{profile}",
                desc=f"Test plugin for profile {profile}",
                author=AUTHOR_META["name"],
                profile=profile,
            )
            lines = [f"✓ Test plugin generated from template\n",
                     f"  Profile:  {profile}\n",
                     f"  Template: {tmpl_dir}\n",
                     f"  Output:   {out_dir / test_name}\n",
                     f"  Files:    {len(staged)}\n\n"]
            for rel in sorted(staged.keys()):
                lines.append(f"  {rel}\n")
            self._t_write("".join(lines))
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))

    def _vinteg_run(self):
        """Verify SHA-256 integrity of a plugin folder on disk."""
        folder_str = self._e_vfolder.get().strip()
        if not folder_str:
            messagebox.showerror(self._t("err_title"),
                "Please select a plugin folder first." if self._lang == "en"
                else "Wybierz folder pluginu.")
            return
        root = Path(folder_str)
        if not root.is_dir():
            messagebox.showerror(self._t("err_title"), f"Directory not found:\n{root}")
            return
        try:
            result = verify_integrity_on_disk(root)
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))
            return

        if "error" in result:
            self._v_write(f"✗ SHA-256 Verify failed: {result['error']}\n")
            return

        icon = "✓" if result["ok"] else "✗"
        lines = [f"{icon} SHA-256 Integrity: {'PASS' if result['ok'] else 'FAIL'}\n",
                 f"  Checked: {result['checked']}  Passed: {result['passed']}  "
                 f"Failed: {len(result['failed'])}\n\n"]
        if result["failed"]:
            lines.append("✗ Mismatches:\n")
            for item in result["failed"]:
                lines.append(f"  • {item['path']}\n")
                if "issue" in item:
                    lines.append(f"    Issue:    {item['issue']}\n")
                if "expected" in item:
                    lines.append(f"    Expected: {item['expected'][:32]}…\n")
                    lines.append(f"    Actual:   {item['actual'][:32]}…\n")
        else:
            lines.append("  All files match their SHA-256 hashes.\n")
        self._v_write("".join(lines))

    def _collect_form(self):
        return {
            "name":    self._e_name.get().strip()    or "MyPlugin",
            "pid":     self._e_id.get().strip()      or "com.polsoft.myplugin",
            "author":  self._e_author.get().strip()  or "Sebastian Januchowski",
            "license": self._e_license.get().strip() or "MIT",
            "desc":    self._e_desc.get("1.0","end").strip() or "Plugin.",
            "profile": self._pvar.get(),
            "icon":    self._ivar.get(),
            "cs":      self._csvar.get(),
            "layout":  self._lvar.get(),
            "out":     Path(self._e_out.get().strip() or str(Path.home()/"Desktop")),
        }

    def _populate_file_list(self):
        self._file_lb.delete(0,"end")
        for fn in sorted(self._staged.keys()):
            self._file_lb.insert("end", fn)
        if self._out_root:
            mp = self._out_root / "manifest.yaml"
            self._e_vpath.delete(0,"end")
            self._e_vpath.insert(0, str(mp))
            self._e_vfolder.delete(0,"end")
            self._e_vfolder.insert(0, str(self._out_root))

    def _generate(self):
        c    = self._collect_form()
        opts = {k: v.get() for k,v in self._opts.items()}
        try:
            files = generate_plugin(
                c["out"], c["name"], c["pid"], c["desc"], c["author"],
                c["license"], c["profile"], c["icon"], c["cs"], c["layout"],
                **{f"opt_{k}": v for k,v in opts.items()}
            )
            self._staged   = files
            self._out_root = c["out"] / c["name"]
            self._populate_file_list()

            # Show validation summary in status bar if report was generated
            val_key = "diagnostics/plugin_report.json"
            if val_key in files:
                try:
                    rpt = json.loads(files[val_key])
                    val_hint = (f"  ✓ Validated: {rpt['error_count']} errors, "
                                f"{rpt['warning_count']} warnings"
                                if rpt["status"] == "OK"
                                else f"  ✗ Validation: {rpt['error_count']} error(s) — "
                                     f"see diagnostics/plugin_report.json")
                except Exception:
                    val_hint = ""
            else:
                val_hint = ""

            self._status.set(
                f"✓ {self._t('success_msg')}  → {self._out_root}{val_hint}"
            )
            self._btn_opendir.config(state="normal")
            self._btn_zip.config(state="normal")

            # Auto-switch to Validator tab and pre-fill folder path
            if opts.get("autovalidate"):
                self._e_vfolder.delete(0,"end")
                self._e_vfolder.insert(0, str(self._out_root))
                self._nb.select(4)  # Validator tab
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))

    def _do_zip(self):
        if not self._out_root or not self._out_root.exists():
            messagebox.showerror(self._t("err_title"), "Generate plugin first.")
            return
        try:
            zp = build_zip(self._out_root, self._out_root.name)
            self._status.set(f"✓ {self._t('zip_success')}  → {zp.name}")
        except Exception as e:
            messagebox.showerror(self._t("err_title"), str(e))

    def _on_sel(self, _e):
        sel = self._file_lb.curselection()
        if not sel: return
        key = self._file_lb.get(sel[0])
        self._prev.config(state="normal")
        self._prev.delete("1.0","end")
        self._prev.insert("end", self._staged.get(key,""))
        self._prev.config(state="disabled")

    def _copy(self):
        content = self._prev.get("1.0","end")
        self.clipboard_clear(); self.clipboard_append(content)
        prev = self._btn_copy["text"]
        self._btn_copy.config(text=self._t("copied"))
        self.after(1800, lambda: self._btn_copy.config(text=prev))

    def _opendir(self):
        if self._out_root and self._out_root.exists():
            import subprocess
            if sys.platform == "win32":   os.startfile(self._out_root)
            elif sys.platform == "darwin": subprocess.Popen(["open", str(self._out_root)])
            else:                          subprocess.Popen(["xdg-open", str(self._out_root)])

    def _vrun(self):
        path = Path(self._e_vpath.get().strip())
        issues, warnings = validate_manifest(path)
        out = []
        if not issues and not warnings:
            out.append(f"✓ Valid: {path.name}\n\n  No issues found.\n")
        else:
            if issues:
                out.append(f"✗ Issues ({len(issues)}):\n")
                for iss in issues:
                    out.append(f"  • {iss}\n")
            if warnings:
                out.append(f"\n⚠ Warnings ({len(warnings)}):\n")
                for w in warnings:
                    out.append(f"  ○ {w}\n")
        self._v_write("".join(out))

    def _vplugin_run(self):
        folder_str = self._e_vfolder.get().strip()
        if not folder_str:
            messagebox.showerror(self._t("err_title"),
                "Please select a plugin folder first." if self._lang=="en"
                else "Wybierz folder pluginu.")
            return
        root = Path(folder_str)
        if not root.is_dir():
            messagebox.showerror(self._t("err_title"),
                f"Directory not found:\n{root}")
            return
        try:
            report = validate_plugin(root)
        except Exception as exc:
            messagebox.showerror(self._t("err_title"), str(exc))
            return

        # Save report next to plugin folder
        try:
            diag_dir = root / "diagnostics"
            diag_dir.mkdir(parents=True, exist_ok=True)
            (diag_dir / "plugin_report.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception:
            pass  # non-fatal — just show in GUI

        lines = []
        status_icon = "✓" if report["status"] == "OK" else "✗"
        lines.append(f"{status_icon} Plugin: {report['plugin']}  "
                     f"| Profile: {report['profile']}  "
                     f"| Status: {report['status']}\n")
        lines.append(f"  Errors: {report['error_count']}   "
                     f"Warnings: {report['warning_count']}\n\n")

        if report["errors"]:
            lines.append(f"✗ Errors ({report['error_count']}):\n")
            for e in report["errors"]:
                file_tag = f"[{e['file']}] " if e.get("file") else ""
                line_tag = f" (line {e['line']})" if e.get("line") else ""
                lines.append(f"  • {file_tag}{e['message']}{line_tag}\n")

        if report["warnings"]:
            lines.append(f"\n⚠ Warnings ({report['warning_count']}):\n")
            for w in report["warnings"]:
                file_tag = f"[{w['file']}] " if w.get("file") else ""
                lines.append(f"  ○ {file_tag}{w['message']}\n")

        if not report["errors"] and not report["warnings"]:
            lines.append("  No issues or warnings found.\n")

        lines.append(f"\n  Report saved → diagnostics/plugin_report.json\n")
        self._v_write("".join(lines))

# ══════════════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════════════

def _cli_banner():
    sep = "─" * 58
    print(f"\n  polsoft.ITS™ Plugin Generator v{VERSION}")
    print(f"  {AUTHOR_META['company']}  |  {AUTHOR_META['email']}")
    print(f"  {sep}\n")


def main_cli(argv=None):
    """Command-line interface for the plugin generator."""
    parser = argparse.ArgumentParser(
        prog="plugin_generator",
        description=f"polsoft.ITS™ Plugin Generator v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(f"""\
            Examples:
              %(prog)s --gui
              %(prog)s --list-profiles
              %(prog)s --list-templates ./templates
              %(prog)s --generate MyPlugin --profile advanced --out ~/Desktop
              %(prog)s --test-template analysis --templates-dir ./templates --out /tmp
              %(prog)s --validate ./MyPlugin/manifest.yaml
              %(prog)s --validate-plugin ./MyPlugin
              %(prog)s --verify-integrity ./MyPlugin
            """),
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--gui",               action="store_true",
                      help="Launch the GUI (default when no arguments given)")
    mode.add_argument("--list-profiles",     action="store_true",
                      help="List all available profiles")
    mode.add_argument("--list-templates",    metavar="DIR", nargs="?", const="templates",
                      help="List templates found in DIR (default: ./templates)")
    mode.add_argument("--generate",          metavar="NAME",
                      help="Generate a plugin with the given name")
    mode.add_argument("--test-template",     metavar="PROFILE",
                      help="Generate a test plugin from a template profile")
    mode.add_argument("--validate",          metavar="MANIFEST",
                      help="Validate a manifest.yaml file")
    mode.add_argument("--validate-plugin",   metavar="DIR",
                      help="Validate a full plugin directory")
    mode.add_argument("--verify-integrity",  metavar="DIR",
                      help="Verify SHA-256 integrity.json hashes on disk")

    # Common options
    parser.add_argument("--profile",        default="minimal",
                        choices=list(PROFILES.keys()),
                        help="Plugin profile (default: minimal)")
    parser.add_argument("--pid",            default=None,
                        help="Plugin ID (default: com.polsoft.<name>)")
    parser.add_argument("--author",         default=AUTHOR_META["name"])
    parser.add_argument("--license",        default="MIT")
    parser.add_argument("--desc",           default="Plugin for polsoft.ITS™ Script Editor.")
    parser.add_argument("--icon-style",     default="dark", choices=ICON_STYLES)
    parser.add_argument("--code-style",     default="PEP8", choices=CODE_STYLES)
    parser.add_argument("--ui-layout",      default="sidebar", choices=UI_LAYOUTS)
    parser.add_argument("--out",            default=None,
                        help="Output directory (default: current directory)")
    parser.add_argument("--templates-dir",  default="templates",
                        help="Templates base directory (default: ./templates)")
    parser.add_argument("--no-validate",    action="store_true",
                        help="Skip auto-validation after generation")
    parser.add_argument("--json",           action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args(argv)
    _cli_banner()

    # ── --list-profiles ───────────────────────────────────────────────────────
    if args.list_profiles:
        print("Available profiles:\n")
        for k, v in PROFILES.items():
            hooks = ", ".join(HOOKS_BY_PROFILE.get(k, []))
            print(f"  {k:<12}  hooks: {hooks}")
        print()
        return 0

    # ── --list-templates ──────────────────────────────────────────────────────
    if args.list_templates is not None:
        tdir = Path(args.list_templates)
        print(f"Templates in: {tdir}\n")
        if not tdir.is_dir():
            print(f"  (directory does not exist yet — use --test-template to create)\n")
            return 0
        found = 0
        for profile in TEMPLATE_TYPES:
            pd = tdir / profile
            if pd.is_dir():
                j2_count = len(list(pd.rglob("*.j2")))
                has_tj   = (pd / "template.json").exists()
                print(f"  {profile:<12}  .j2 files: {j2_count:<3}  template.json: {'✓' if has_tj else '✗'}")
                found += 1
        if found == 0:
            print("  No template directories found.")
        print()
        return 0

    # ── --validate ────────────────────────────────────────────────────────────
    if args.validate:
        path = Path(args.validate)
        issues, warnings = validate_manifest(path)
        if args.json:
            print(json.dumps({"path": str(path), "issues": issues,
                              "warnings": warnings, "ok": not issues}, indent=2))
        else:
            if not issues and not warnings:
                print(f"✓ Valid: {path.name}  — no issues\n")
            else:
                if issues:
                    print(f"✗ Errors ({len(issues)}):")
                    for i in issues: print(f"  • {i}")
                if warnings:
                    print(f"\n⚠ Warnings ({len(warnings)}):")
                    for w in warnings: print(f"  ○ {w}")
                print()
        return 1 if issues else 0

    # ── --validate-plugin ─────────────────────────────────────────────────────
    if args.validate_plugin:
        root = Path(args.validate_plugin)
        report = validate_plugin(root)
        # Save report
        rp = root / "diagnostics" / "plugin_report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            icon = "✓" if report["status"] == "OK" else "✗"
            print(f"{icon} Plugin: {report['plugin']}  Profile: {report['profile']}  "
                  f"Status: {report['status']}")
            print(f"  Errors: {report['error_count']}   Warnings: {report['warning_count']}")
            if report["errors"]:
                print(f"\n  Errors:")
                for e in report["errors"]:
                    print(f"    • [{e['file']}] {e['message']}")
            if report["warnings"]:
                print(f"\n  Warnings:")
                for w in report["warnings"]:
                    print(f"    ○ [{w['file']}] {w['message']}")
            print(f"\n  Report saved → {rp}\n")
        return 1 if report["errors"] else 0

    # ── --verify-integrity ────────────────────────────────────────────────────
    if args.verify_integrity:
        root   = Path(args.verify_integrity)
        result = verify_integrity_on_disk(root)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"✗ Error: {result['error']}\n")
                return 1
            icon = "✓" if result["ok"] else "✗"
            print(f"{icon} SHA-256 Integrity: {'PASS' if result['ok'] else 'FAIL'}")
            print(f"  Checked: {result['checked']}  Passed: {result['passed']}  "
                  f"Failed: {len(result['failed'])}")
            if result["failed"]:
                print("\n  Mismatches:")
                for item in result["failed"]:
                    flag = item.get("issue","mismatch")
                    print(f"    • {item['path']}  [{flag}]")
            else:
                print("  All files match their SHA-256 hashes.")
            print()
        return 0 if result.get("ok") else 1

    # ── --test-template ───────────────────────────────────────────────────────
    if args.test_template:
        profile  = args.test_template
        tdir     = Path(args.templates_dir)
        tmpl_dir = tdir / profile
        out_dir  = Path(args.out) if args.out else Path.cwd()

        print(f"Testing template: {profile}")
        print(f"  Template dir: {tmpl_dir}")

        # Auto-generate templates if missing
        if not tmpl_dir.is_dir():
            print(f"  Template dir not found — generating .j2 files...")
            gen_j2_templates(profile, tmpl_dir)
            print(f"  Generated template files in {tmpl_dir}")

        # Validate first
        report = validate_template(tmpl_dir)
        icon   = "✓" if report["status"] == "OK" else "✗"
        print(f"\n  {icon} Template validation: {report['status']}")
        print(f"     Errors: {report['error_count']}   Warnings: {report['warning_count']}")
        for e in report["errors"]:
            print(f"     ✗ [{e['file']}] {e['message']}")
        for w in report["warnings"]:
            print(f"     ○ [{w['file']}] {w['message']}")

        # Generate test plugin
        test_name = f"Test_{profile.replace('-','_').title()}"
        print(f"\n  Generating test plugin '{test_name}' → {out_dir}...")
        try:
            staged = generate_from_template(
                tmpl_dir, out_dir,
                name=test_name,
                pid=f"com.polsoft.test.{profile}",
                desc=f"Test plugin — profile {profile}",
                author=AUTHOR_META["name"],
                profile=profile,
            )
            print(f"  ✓ Generated {len(staged)} files")
            print(f"  ✓ ZIP: {out_dir / test_name}.pits-plugin.zip")
            # Verify integrity
            vr = verify_integrity_on_disk(out_dir / test_name)
            iv = "✓" if vr.get("ok") else "✗"
            print(f"  {iv} SHA-256 verify: checked={vr['checked']} "
                  f"passed={vr['passed']} failed={len(vr['failed'])}")
        except Exception as e:
            print(f"  ✗ Generation failed: {e}")
            return 1
        print()
        return 0

    # ── --generate ────────────────────────────────────────────────────────────
    if args.generate:
        name    = args.generate
        pid     = args.pid or f"com.polsoft.{name.lower().replace(' ','_')}"
        out_dir = Path(args.out) if args.out else Path.cwd()
        print(f"Generating plugin: {name}")
        print(f"  Profile:  {args.profile}")
        print(f"  ID:       {pid}")
        print(f"  Output:   {out_dir}")
        try:
            staged = generate_plugin(
                out_dir, name, pid, args.desc, args.author, args.license,
                args.profile, args.icon_style, args.code_style, args.ui_layout,
                opt_autovalidate=not args.no_validate,
            )
            print(f"  ✓ Generated {len(staged)} files → {out_dir / name}")
            if not args.no_validate:
                rpt_raw = staged.get("diagnostics/plugin_report.json", "{}")
                try:
                    rpt = json.loads(rpt_raw)
                    icon = "✓" if rpt["status"] == "OK" else "✗"
                    print(f"  {icon} Validation: {rpt['status']}  "
                          f"errors={rpt['error_count']}  warnings={rpt['warning_count']}")
                except Exception:
                    pass
            # Verify SHA-256
            vr = verify_integrity_on_disk(out_dir / name)
            iv = "✓" if vr.get("ok") else "✗"
            print(f"  {iv} SHA-256 verify: checked={vr['checked']} "
                  f"passed={vr['passed']} failed={len(vr['failed'])}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return 1
        print()
        return 0

    # ── --gui fallback ─────────────────────────────────────────────────────────
    _launch_gui()
    return 0


def _launch_gui():
    if not TK_OK:
        print("✗ tkinter is not available in this environment.")
        print("  On Linux: sudo apt install python3-tk")
        print("  On Windows/macOS: reinstall Python with the 'tcl/tk' option checked.")
        print("  Alternatively, use CLI mode: --generate, --validate, etc.")
        sys.exit(1)
    app = App()
    app.mainloop()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # No arguments → launch GUI directly (backward compatible)
    if len(sys.argv) == 1:
        _launch_gui()
    else:
        sys.exit(main_cli())