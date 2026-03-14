# polsoft.ITS™ Generator Pluginów

> **Narzędzie deweloperskie dla [polsoft.ITS™ Script Editor](https://github.com/seb07uk)** — twórz, waliduj i wdrażaj pluginy w kilka sekund.

[![Wersja](https://img.shields.io/badge/wersja-4.3.0-6C63FF?style=flat-square)](https://github.com/seb07uk)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platforma](https://img.shields.io/badge/platforma-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/seb07uk)
[![Licencja](https://img.shields.io/badge/licencja-MIT-green?style=flat-square)](LICENSE)

---

## Opis

**polsoft.ITS™ Generator Pluginów** to przenośne, jednoplikowe narzędzie deweloperskie do generowania kompletnych pakietów pluginów dla polsoft.ITS™ Script Editor. Obsługuje 10 wbudowanych profili pluginów, pełny system szablonów Jinja2, weryfikację integralności SHA-256 oraz dwujęzyczny (PL/EN) interfejs graficzny z głębokim ciemnym motywem — wszystko z jednego pliku Python bez obowiązkowych zależności.

Można go uruchomić z interfejsem graficznym lub sterować wyłącznie z wiersza poleceń, integrować z CI lub osadzić jako bibliotekę.

![Zrzut ekranu GUI](docs/screenshot.png)

---

## Funkcje

| Funkcja | Szczegóły |
|---|---|
| **10 profili pluginów** | `minimal` · `advanced` · `enterprise` · `ui-heavy` · `analysis` · `terminal` · `wizard` · `telemetry` · `database` · `network` |
| **System szablonów Jinja2** | Generuj szkielety `.j2` per profil, renderuj je do pełnych pluginów, waliduj szablony |
| **Integralność SHA-256** | Każdy wygenerowany plik jest hashowany; `verify-integrity` wykrywa modyfikacje po generacji |
| **Pełny walidator** | 10-obszarowy walidator pluginu: manifest · hooki · struktura · UI · config · ikony · libs · metadane |
| **6-zakładkowe GUI** | Generator · Wizard · Szablony · Opcje · Walidator · O programie |
| **CLI z 8 poleceniami** | W pełni skryptowalne — bez potrzeby wyświetlania |
| **Dwujęzyczność** | Interfejs Polski / Angielski z przełącznikiem |
| **Jeden plik, zero obowiązkowych zależności** | Działa z Python 3.8+ bez instalacji |

---

## Pierwsze kroki

### Wymagania

| Wymaganie | Wersja | Uwagi |
|---|---|---|
| Python | 3.8+ | Wymagany |
| tkinter | wbudowany | Wymagany tylko dla GUI |
| PyYAML | 6.0+ | Opcjonalny — pełna walidacja YAML manifestu |
| Jinja2 | 3.0+ | Opcjonalny — pełne renderowanie szablonów `.j2` |

Instalacja zależności opcjonalnych:

```bash
pip install pyyaml jinja2
```

### Instalacja

Instalacja nie jest wymagana. Pobierz plik i uruchom:

```bash
# Pobierz
curl -O https://raw.githubusercontent.com/seb07uk/polsoft-plugin-generator/main/plugin_generator_5.py

# Uruchom GUI
python plugin_generator_5.py

# Lub użyj CLI
python plugin_generator_5.py --help
```

---

## Użycie

### Tryb GUI

Kliknij dwukrotnie `plugin_generator_5.py` lub uruchom:

```bash
python plugin_generator_5.py
python plugin_generator_5.py --gui
```

GUI otwiera się z sześcioma zakładkami:

- **Generator** — wpisz nazwę pluginu, ID, profil, style i kliknij **✦ Generuj plugin**
- **Wizard** — interaktywny kreator czterokrokowy
- **Szablony** — generuj szkielety `.j2`, waliduj i testuj szablony
- **Opcje** — włącz/wyłącz opcjonalne pliki wyjściowe (testy, changelog, integralność, meta-pluginy…)
- **Walidator** — waliduj `manifest.yaml` lub cały folder pluginu; weryfikuj hashe SHA-256
- **O programie** — wersja i dane autora

### Tryb CLI

```bash
python plugin_generator_5.py --list-profiles
python plugin_generator_5.py --list-templates ./templates
python plugin_generator_5.py --generate MojPlugin --profile advanced --out ~/Pulpit
python plugin_generator_5.py --test-template analysis --templates-dir ./templates --out /tmp
python plugin_generator_5.py --validate ./MojPlugin/manifest.yaml
python plugin_generator_5.py --validate-plugin ./MojPlugin
python plugin_generator_5.py --verify-integrity ./MojPlugin
```

#### Wszystkie opcje CLI

```
uzycie: plugin_generator_5.py [--gui] [--list-profiles] [--list-templates [KATALOG]]
                               [--generate NAZWA] [--test-template PROFIL]
                               [--validate MANIFEST] [--validate-plugin KATALOG]
                               [--verify-integrity KATALOG]
                               [--profile PROFIL] [--pid PID] [--author AUTOR]
                               [--license LICENCJA] [--desc OPIS]
                               [--icon-style {neon,pixel,symbolic,gradient,dark}]
                               [--code-style {PEP8,compact,verbose,enterprise}]
                               [--ui-layout {sidebar,tabs,modal,split}]
                               [--out KATALOG] [--templates-dir KATALOG]
                               [--no-validate] [--json]
```

---

## Profile pluginów

| Profil | Opis | Kluczowe hooki |
|---|---|---|
| `minimal` | Jeden plik, bez zależnosci | `onLoad` · `onCommand` |
| `advanced` | Panel UI + biblioteka pomocnicza | +`onEditorReady` · `onFileOpen` · `onFileSave` |
| `enterprise` | Kontener DI, szyna zdarzen, telemetria | +`onEvent` · `onError` · `onTelemetry` |
| `ui-heavy` | Silnik motywow, dynamiczny panel | +`onThemeChange` · `onPanelResize` |
| `analysis` | Analizator kodu + generator raportow | +`onAnalysisRequest` · `onDiagnostic` |
| `terminal` | Runner powloki, cykl zycia procesu | +`onTerminalInput` · `onProcessStart` |
| `wizard` | Wielokrokowy interfejs przewodnika | +`onWizardStep` · `onWizardComplete` |
| `telemetry` | Agregacja metryk + push | +`onTelemetry` · `onMetric` |
| `database` | Menedzer polaczen, runner zapytan | +`onDbConnect` · `onDbQuery` |
| `network` | Klient HTTP, hooki zadan/odpowiedzi | +`onRequest` · `onResponse` · `onTimeout` |

---

## Struktura wygenerowanego pluginu

```
MojPlugin/
├── manifest.yaml              # Manifest pluginu (nazwa, id, wersja, hooki, uprawnienia)
├── main.py                    # Punkt wejscia — implementacje hookow
├── README.txt                 # Dokumentacja pluginu
├── CHANGELOG.md
├── requirements.txt
├── integrity.json             # SHA-256 + MD5 dla kazdego pliku
├── plugin-info.json           # Manifest API
├── update.json                # Deskryptor auto-aktualizacji
├── .plugin-manifest.yaml      # Integracja z Plugin Manager
├── install.ps1 / install.bat  # Skrypty instalacyjne Windows
│
├── config/
│   └── default.json
│
├── icons/
│   ├── plugin.svg             # 5 wariantow ikon
│   ├── panel.svg
│   ├── toolbar.svg
│   ├── plugin_dark.svg
│   └── plugin_symbolic.svg
│
├── ui/                        # (profile advanced+)
│   ├── panel.html
│   └── panel.css
│
├── libs/                      # Biblioteki specyficzne dla profilu
│   └── helper.py / analyzer.py / telemetry.py / ...
│
├── tests/                     # Zestaw testow pytest (4 pliki)
│   ├── test_load.py
│   ├── test_commands.py
│   ├── test_ui.py
│   └── test_config.py
│
├── selftest.py                # Samodzielny runner testow
│
├── diagnostics/
│   ├── plugin_structure.json
│   ├── file_hashes.json
│   ├── manifest_report.json
│   └── plugin_report.json     # Pelny raport walidacji
│
└── generator_plugins/         # System meta-pluginow
    ├── README.txt
    ├── add_enterprise_features.py
    ├── add_ui_themes.py
    ├── add_tests.py
    ├── add_telemetry.py
    └── add_database_support.py
```

---

## System szablonow

Generator zawiera w pelni kompatybilny system szablonow Jinja2.

### Utworz szablony dla profilu

```bash
python plugin_generator_5.py --test-template advanced --templates-dir ./templates --out /tmp
```

To polecenie:
1. Generuje pliki szkieletowe `.j2` w `templates/advanced/`
2. Generuje deskryptor `template.json`
3. Waliduje szablon (bledy + ostrzezenia)
4. Renderuje testowy plugin i weryfikuje jego integralnosc SHA-256

### Zmienne szablonu

Kazdy plik `.j2` moze uzywac:

```
{{ name }}        {{ plugin_id }}    {{ description }}   {{ author }}
{{ version }}     {{ profile }}      {{ company }}        {{ email }}
{{ github }}      {{ copyright }}    {{ license }}        {{ brand }}
{{ hooks }}       {{ commands }}     {{ panels }}         {{ permissions }}
{{ ui_layout }}   {{ icon_style }}   {{ code_style }}     {{ generated }}
{{ generator }}
```

### Dodaj wlasny szablon

```
templates/
└── moj_profil/
    ├── manifest.yaml.j2
    ├── main.py.j2
    ├── README.txt.j2
    ├── template.json          <- wymagany deskryptor
    └── ...                    <- dodatkowe pliki .j2
```

**Format `template.json`:**

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

## Weryfikacja integralnosci

Kazdy wygenerowany plugin zawiera `integrity.json` z hashami SHA-256 + MD5 dla wszystkich plikow.

```json
{
  "algorithm": "SHA-256",
  "generator": "polsoft.ITS™ Plugin Generator v4.3.0",
  "files": {
    "manifest.yaml": {
      "algorithm": "SHA-256",
      "sha256": "a3f1...",
      "md5":    "c2b9...",
      "size":   1264
    }
  }
}
```

Weryfikuj w dowolnym momencie:

```bash
python plugin_generator_5.py --verify-integrity ./MojPlugin
```

```
✓ SHA-256 Integralnosc: OK
  Sprawdzono: 30  Zgodnych: 30  Niezgodnych: 0
  Wszystkie pliki zgodne z hashami SHA-256.
```

Jezeli plik zostal zmodyfikowany:

```
✗ SHA-256 Integralnosc: BLAD
  Sprawdzono: 30  Zgodnych: 29  Niezgodnych: 1

  Niezgodnosci:
    • main.py  [niezgodnosc SHA-256]
      Oczekiwano: a3f1c8d2...
      Znaleziono: 77b3e91f...
```

---

## Walidacja

### Waliduj manifest

```bash
python plugin_generator_5.py --validate ./MojPlugin/manifest.yaml
```

### Waliduj caly katalog pluginu

```bash
python plugin_generator_5.py --validate-plugin ./MojPlugin
```

Walidator sprawdza **10 obszarow**:

1. `manifest.yaml` — wymagane pola, format ID, wersja, hooki, panele
2. `main.py` — wymagane hooki, hooki specyficzne dla profilu, metadane autora
3. Struktura folderow — wymagane sciezki per profil
4. Pliki UI — elementy `panel.html`, selektory `panel.css`
5. `config/default.json` — poprawnosc JSON, `__meta`, sekcje specyficzne dla profilu
6. Ikony — 5 wariantow SVG, poprawnosc `<svg>`
7. `plugin-info.json` — sekcja API, hooki, uprawnienia
8. `integrity.json` — struktura i pole generatora
9. Pliki bibliotek — zawartosc `libs/` specyficzna dla profilu
10. Opcjonalne pliki zalecane — README, update.json, CHANGELOG

Raporty sa zapisywane do `diagnostics/plugin_report.json`.

---

## Opcje

| Opcja | Domyslnie | Opis |
|---|---|---|
| Testy Pytest (4 pliki) | ✓ | `test_load` · `test_commands` · `test_ui` · `test_config` |
| `selftest.py` | ✓ | Samodzielny runner testow (bez pytest) |
| `CHANGELOG.md` | ✓ | Szkielet historii zmian |
| `requirements.txt` | ✓ | Lista zaleznosci dla profilu |
| Skrypty instalacyjne | ✓ | Instalatory `.ps1` + `.bat` Windows |
| Diagnostics | ✓ | `plugin_structure.json` · `file_hashes.json` · `manifest_report.json` |
| `integrity.json` | ✓ | Hashe SHA-256 + MD5 dla wszystkich plikow |
| `update.json` | ✓ | Szkielet mechanizmu auto-aktualizacji |
| `plugin-info.json` | ✓ | Pelny manifest API |
| `.plugin-manifest.yaml` | ✓ | Integracja z Plugin Manager |
| `generator_plugins/` | ✓ | System rozszerzania przez meta-pluginy |
| **Auto-walidacja po generacji** | ✓ | Uruchamia pelny walidator i zapisuje raport automatycznie |

---

## System meta-pluginow

Katalog `generator_plugins/` pozwala rozszerzac generator bez modyfikowania jego kodu. Kazdy plik eksponuje jedna funkcje:

```python
def apply(staged: dict, context: dict) -> dict:
    # staged  = {sciezka_relatywna: zawartosc}  — wszystkie pliki do zapisu
    # context = {name, pid, profile, author, ...}
    staged["libs/moj_addon.py"] = "# wstrzykniete przez meta-plugin\n"
    return staged
```

Wbudowane meta-pluginy:

| Plik | Dzialanie |
|---|---|
| `add_enterprise_features.py` | Dodaje komentarze DI + stub telemetrii |
| `add_ui_themes.py` | Wstrzykuje dodatkowe zmienne CSS motywu |
| `add_tests.py` | Dodaje stuby testow integracyjnych |
| `add_telemetry.py` | Dodaje `libs/telemetry_stub.py` jezeli brak |
| `add_database_support.py` | Dodaje `libs/sqlite_stub.py` jezeli brak |

---

## Style kodu

| Styl | Opis |
|---|---|
| `PEP8` | Standardowe formatowanie Python (domyslny) |
| `compact` | Usuniete puste linie miedzy funkcjami |
| `verbose` | Komentarze separatora przed kazdym hookiem |
| `enterprise` | Pelne docstringi, type hints, strukturowane logowanie |

---

## Style ikon (SVG)

| Styl | Tlo | Wyglad |
|---|---|---|
| `dark` | `#111116` | Podwojne ramki, subtelne linie siatki, jasny tekst (domyslny) |
| `neon` | `#07071a` | Radialny gradient, dwa koncentryczne pierscienie, markery krzyzowe, centralny punkt |
| `pixel` | `#0d0e18` | 8 dekoracji narożnych i krawędziowych, ostre kwadratowe rogi |
| `symbolic` | `#fafaf8` | Jasny motyw, podwojna ramka (przerywana + ciagla), wewnetrzne linie siatki |
| `gradient` | `#3C3489` | Wypelnienie linearGradient, kulista poswata, polprzezroczysta linia podzialu |

---

## Layouty panelu UI

| Layout | Opis |
|---|---|
| `sidebar` | Pionowa nawigacja z lewostronnym wskaznikiem aktywnego elementu, obszar wyjsciowy wypelnia pozostale miejsce |
| `tabs` | Poziomy pasek zakladek (Run / Analyze / Config), podkreslennie aktywnej zakladki |
| `modal` | Plywajace okno dialogowe z nakladka `backdrop-filter: blur`, animowany przycisk zamkniecia |
| `split` | Dwukolumnowa siatka: kontrolki po lewej (ciemna karta), przewijalne wyjscie po prawej |

Wszystkie layouty uzywaja czcionki **JetBrains Mono** (Google Fonts) z Consolas jako fallback, tekstury tla z siatka 24 px oraz wspolnego ciemnego systemu kolorow (`#0b0b14` baza, `#6C63FF` akcent).

---

## Standardy pluginow polsoft.ITS™

Kazdy wygenerowany plugin spelnia pelny standard polsoft.ITS™:

- ✅ `manifest.yaml` z `name`, `id`, `version`, `hooks`, `permissions`, `panels`
- ✅ `icons/` z minimum 2 wariantami SVG (generowanych jest 5)
- ✅ `README.txt` z opisem
- ✅ Metadane autora w naglowku kazdego pliku (`name`, `company`, `email`, `github`, `copyright`)
- ✅ Branding i copyright polsoft.ITS™ we wszystkich typach generowanych plikow (`.py`, `.yaml`, `.md`, `.css`, `.html`, `.txt`, `.ps1`, `.bat`)
- ✅ Poprawna struktura folderow per profil
- ✅ Zestaw testow pytest (advanced+)
- ✅ `integrity.json` z SHA-256
- ✅ Manifest API `plugin-info.json`

---

## Historia zmian

### v4.3.0

- **Ciemny motyw GUI** — pelna migracja z jasnego (`#f5f4f0`) na gleboki ciemny (`#0d0d18`) we wszystkich 6 zakladkach; wszystkie czcionki zmienione z Courier na Consolas
- **Automatyczne dopasowanie okna** — `update_idletasks()` + `geometry()` po zbudowaniu UI; `minsize(820, 580)` zapobiega obcinaniu zawartosci
- **Integracja widgetow z oknem** — wszystkie ramki zakladek uzywaja `grid(sticky="nsew")` z `columnconfigure/rowconfigure weight=1`; notebook wypelnia okno w calosci
- **Redesign zakladki "O programie"** — zastapiono przewijalne `tk.Text` siatka wysrodkowanych etykiet; cala zawartosc widoczna bez przewijania; etykiety kluczy z obsluga jezyka (PL/EN)
- **Redesign ikon SVG** — przeprojektowane wszystkie 5 stylow: `neon` z radialnym gradientem + markerami krzyzowymi; `pixel` z 8 dekoracjami; `symbolic` z podwojna ramka + siatka; `gradient` z `linearGradient`; `dark` z wewnetrznymi liniami siatki
- **Panel CSS v2** — czcionka JetBrains Mono, tekstura tla z siatka 24 px, glassmorphism modalu (`backdrop-filter: blur`), wlasny scrollbar 4 px, `transition` + `transform` przyciskow, lewy wskaznik aktywnego elementu sidebar
- **Kompletnosc metadanych autora** — `hdr()` wstrzykuje teraz `email` + `github` do naglowkow `.md`, `.css`, `.txt`, `.ps1/.bat/.sh`; `LANG["about_body"]` przerobiony na stale `AUTHOR_META`

### v4.2.0

- **System szablonow Jinja2** — `gen_j2_templates`, `validate_template`, `generate_from_template`, `render_j2` (z fallbackiem)
- **`verify_integrity_on_disk()`** — wykrywanie manipulacji SHA-256 w dowolnym folderze pluginu
- **Ulepszenia SHA-256** — pole `algorithm` we wszystkich wpisach hash, jawne kodowanie UTF-8, helper `_file_hashes()`
- **CLI** — 8 polecen, wyjscie `--json`, flaga `--no-validate`
- **Zakladka Szablony w GUI** — generuj, waliduj i testuj szablony z poziomu GUI
- **Przycisk weryfikacji integralnosci** w zakladce Walidator
- **Leniwy import tkinter** — CLI dziala bez wyswietlacza i bez zainstalowanego tkinter
- Poprawka: kompatybilnosc klasy `App` z Windows (`TypeError: __bases__ assignment`)
- Poprawka: blad wciec YAML w `manifest.yaml`

### v4.1.0

- `validate_plugin()` — pelny walidator pluginu (10 obszarow)
- `diagnostics/plugin_report.json` — ustrukturyzowany raport bledow/ostrzezen
- `REQUIRED_STRUCTURE`, `PROFILES_WITH_UI` — wyeliminowano magiczne ciagi znakow
- Auto-walidacja po generacji (`opt_autovalidate`)
- Zakladka Walidator: sekcja manifestu + sekcja pelnego folderu pluginu
- Przycisk weryfikacji SHA-256

### v4.0.0

- 10 profili pluginow (dodano wizard, telemetry, database, network)
- 4 pliki testow per plugin (test_load, test_commands, test_ui, test_config)
- Samodzielny runner `selftest.py`
- `integrity.json` SHA-256 + MD5
- Sprawdzanie `update.json` auto-aktualizacji
- Style kodu: PEP8 / compact / verbose / enterprise
- Layouty UI: sidebar / tabs / modal / split
- System meta-pluginow (`generator_plugins/`)
- Tryb Wizard w GUI
- 5 wariantow ikon SVG
- Dwujezyczny interfejs PL/EN

---

## Informacje o projekcie

| | |
|---|---|
| **Programista** | Sebastian Januchowski |
| **Firma** | polsoft.ITS™ Group |
| **Email** | polsoft.its@fastservice.com |
| **GitHub** | [github.com/seb07uk](https://github.com/seb07uk) |
| **Licencja** | MIT |
| **Copyright** | 2026© Sebastian Januchowski & polsoft.ITS™ |

---

## Wklad w projekt

1. Sforkuj repozytorium
2. Utworz galaz funkcji (`git checkout -b feature/moja-funkcja`)
3. Zatwierdz zmiany (`git commit -m 'Dodaj moja funkcje'`)
4. Wypchnij galaz (`git push origin feature/moja-funkcja`)
5. Otworz Pull Request

Upewnij sie, ze wszystkie istniejace profile przechodza walidacje (`errors=0, warnings=0`) przed zgloszeniem.

---

## Licencja

Ten projekt jest objety licencja **MIT** — szczegoly w pliku [LICENSE](LICENSE).

```
2026© Sebastian Januchowski & polsoft.ITS™. Wszelkie prawa zastrzezone.
```

---

*Wygenerowano za pomoca polsoft.ITS™ Generator Pluginow v4.3.0*
