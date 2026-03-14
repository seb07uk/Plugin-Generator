━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  polsoft.ITS™ Generator Pluginow  v4.3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Programista:  Sebastian Januchowski
  Firma:        polsoft.ITS™ Group
  Email:        polsoft.its@fastservice.com
  GitHub:       https://github.com/seb07uk
  2026© Sebastian Januchowski & polsoft.ITS™. Wszelkie prawa zastrzezone.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPIS
────
  Przenosne, jednoplikowe narzedzie deweloperskie do generowania
  kompletnych pakietow pluginow dla polsoft.ITS™ Script Editor.
  Nie wymaga instalacji. Dziala z Python 3.8+ bez konfiguracji.

SZYBKI START
────────────
  Tryb GUI:
    python plugin_generator_5.py

  CLI — wygeneruj plugin:
    python plugin_generator_5.py --generate MojPlugin --profile advanced --out ./output

  CLI — lista profili:
    python plugin_generator_5.py --list-profiles

  CLI — waliduj plugin:
    python plugin_generator_5.py --validate-plugin ./MojPlugin

  CLI — weryfikuj integralnosc SHA-256:
    python plugin_generator_5.py --verify-integrity ./MojPlugin

ZALEZNOSCI OPCJONALNE
─────────────────────
  pip install pyyaml jinja2
  (bez nich narzedzie dziala — ograniczona walidacja YAML i renderowanie szablonow)

PROFILE  (10 lacznie)
─────────────────────
  minimal    advanced    enterprise    ui-heavy    analysis
  terminal   wizard      telemetry     database    network

CO JEST GENEROWANE
──────────────────
  manifest.yaml  main.py  README.txt  CHANGELOG.md  requirements.txt
  integrity.json  plugin-info.json  update.json  .plugin-manifest.yaml
  install.ps1 / install.bat  config/  icons/ (5 wariantow SVG)
  ui/ (profile advanced+)  libs/  tests/ (4 pliki pytest)
  selftest.py  diagnostics/  generator_plugins/

ZAKLADKI GUI
────────────
  Generator · Wizard · Szablony · Opcje · Walidator · O programie

POLECENIA CLI
─────────────
  --gui                           Uruchom GUI
  --list-profiles                 Lista dostepnych profili
  --list-templates [KATALOG]      Lista dostepnych szablonow
  --generate NAZWA --profile P    Generuj plugin
  --test-template PROFIL [KATALOG] Testuj szablon
  --validate MANIFEST             Waliduj manifest.yaml
  --validate-plugin KATALOG       Pelna walidacja pluginu (10 obszarow)
  --verify-integrity KATALOG      Weryfikacja integralnosci SHA-256
  --json                          Wyjscie w formacie JSON
  --no-validate                   Pomin walidacje po generacji

HISTORIA ZMIAN
──────────────
  v4.3.0  Ciemny motyw GUI · czcionka Consolas · auto-rozmiar okna ·
          redesign zakladki O programie (bez przewijania) ·
          redesign ikon SVG · Panel CSS v2 (JetBrains Mono, glassmorphism) ·
          kompletne metadane autora we wszystkich generowanych plikach

  v4.2.0  System szablonow Jinja2 · verify_integrity_on_disk() ·
          CLI 8 polecen · zakladka Szablony w GUI

  v4.1.0  validate_plugin() walidator 10-obszarowy · auto-walidacja

  v4.0.0  10 profili · system meta-pluginow · Wizard GUI · 5 ikon SVG ·
          dwujezyczny interfejs PL/EN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  2026© Sebastian Januchowski & polsoft.ITS™. Wszelkie prawa zastrzezone.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
