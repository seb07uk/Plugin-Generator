# polsoft.ITS™ Plugin Generator
### Wersja 4.3.0 — aplikacja desktopowa (portable .exe)

> Narzędzie deweloperskie dla **polsoft.ITS™ Script Editor** — twórz, waliduj i pakuj pluginy w kilka sekund.

**Programista:** Sebastian Januchowski | **Firma:** polsoft.ITS™ Group
**Kontakt:** polsoft.its@fastservice.com | **GitHub:** github.com/seb07uk
**Licencja:** MIT | **Copyright:** 2026© Sebastian Januchowski & polsoft.ITS™

---

## Uruchomienie

Plik `PluginGenerator.exe` jest **w pełni przenośny** — nie wymaga instalacji ani Pythona.

1. Skopiuj `PluginGenerator.exe` w dowolne miejsce na dysku
2. Uruchom dwuklikiem
3. GUI otwiera się automatycznie

> Przy pierwszym uruchomieniu Windows może wyświetlić ostrzeżenie SmartScreen — kliknij **„Więcej informacji" → „Uruchom mimo to"**.

---

## Interfejs — 6 zakładek

### ✦ Generator
Główny panel tworzenia pluginu. Wypełnij pola i kliknij **✦ Generuj plugin**:

| Pole | Opis |
|------|------|
| Nazwa pluginu | Wyświetlana nazwa, np. `MójPlugin` |
| ID pluginu | Unikalny identyfikator, np. `com.firma.mojplugin` |
| Autor | Imię i nazwisko autora |
| Licencja | Np. `MIT`, `GPL-3.0`, `Proprietary` |
| Opis | Krótki opis działania pluginu |
| Profil | Typ pluginu — patrz sekcja Profile poniżej |
| Styl ikon SVG | Wygląd ikon: `dark` / `neon` / `pixel` / `symbolic` / `gradient` |
| Styl kodu | Formatowanie kodu: `PEP8` / `compact` / `verbose` / `enterprise` |
| Layout panelu UI | Układ panelu: `sidebar` / `tabs` / `modal` / `split` |
| Katalog wyjściowy | Folder, w którym zostanie zapisany plugin |

Po generacji lista plików pojawia się po prawej stronie — kliknięcie pliku pokazuje jego podgląd.
Przycisk **📦 Buduj ZIP** pakuje cały plugin do pliku `.pits-plugin.zip`.

---

### 🧙 Wizard
Interaktywny kreator 4-krokowy — prowadzi przez cały proces tworzenia pluginu bez znajomości szczegółów technicznych:

1. **Krok 1** — Podstawowe dane (nazwa, ID, autor, licencja, opis)
2. **Krok 2** — Profil i styl (profil, ikony, kod, layout)
3. **Krok 3** — Podgląd hooków i uprawnień dla wybranego profilu
4. **Krok 4** — Potwierdzenie i generacja

---

### 📄 Szablony
System szablonów Jinja2 — zaawansowane tworzenie pluginów na bazie własnych szablonów `.j2`:

- **Generuj pliki .j2** — tworzy szkielet szablonu dla wybranego profilu
- **Waliduj szablon** — sprawdza poprawność plików `.j2` i `template.json`
- **Testuj szablon** — generuje plugin testowy z szablonu i weryfikuje wynik

---

### ⚙ Opcje
Kontrola dodatkowych plików generowanych razem z pluginem:

| Opcja | Domyślnie | Co generuje |
|-------|-----------|-------------|
| Testy pytest | ✓ | 4 pliki testów (`test_load`, `test_commands`, `test_ui`, `test_config`) |
| selftest.py | ✓ | Samodzielny tester bez potrzeby instalacji pytest |
| CHANGELOG.md | ✓ | Szablon historii wersji |
| requirements.txt | ✓ | Lista zależności dostosowana do profilu |
| Skrypty instalacyjne | ✓ | `install.ps1` + `install.bat` dla Windows |
| Diagnostics/ | ✓ | Raporty struktury i hashy plików |
| integrity.json | ✓ | Sumy SHA-256 + MD5 dla wszystkich plików |
| update.json | ✓ | Deskryptor auto-aktualizacji |
| plugin-info.json | ✓ | Pełny manifest API |
| .plugin-manifest.yaml | ✓ | Integracja z Plugin Managerem |
| generator_plugins/ | ✓ | System meta-pluginów |
| **Auto-walidacja** | ✓ | Automatyczna walidacja po każdej generacji |

---

### ✔ Walidator
Narzędzie weryfikacji poprawności pluginów:

**Walidacja manifestu** — sprawdza pojedynczy plik `manifest.yaml` pod kątem wymaganych pól, formatu wersji i ID.

**Walidacja całego pluginu** — pełna weryfikacja 10 obszarów:
1. `manifest.yaml` — wymagane pola, format ID, hooki, panele
2. `main.py` — wymagane hooki, metadane autora
3. Struktura folderów — zgodność z profilem
4. Pliki UI — `panel.html`, `panel.css`
5. `config/default.json` — poprawność JSON, sekcje
6. Ikony SVG — 5 wariantów, poprawność `<svg>`
7. `plugin-info.json` — sekcja API, hooki, uprawnienia
8. `integrity.json` — struktura i pole generatora
9. Pliki bibliotek — zgodność z profilem
10. Pliki opcjonalne — README, update.json, CHANGELOG

**Weryfikacja SHA-256** — porównuje sumy kontrolne z `integrity.json` z faktyczną zawartością plików na dysku. Wykrywa każdą modyfikację po wygenerowaniu.

---

### ℹ O programie
Informacje o wersji i autorze.

---

## Profile pluginów

Profil określa strukturę, hooki i biblioteki generowanego pluginu:

| Profil | Zastosowanie |
|--------|-------------|
| `minimal` | Najprostszy plugin — jeden plik, brak zależności |
| `advanced` | Panel UI + biblioteka pomocnicza |
| `enterprise` | Kontener DI, szyna zdarzeń, telemetria |
| `ui-heavy` | Silnik motywów, dynamiczny panel |
| `analysis` | Analizator kodu + generator raportów |
| `terminal` | Runner poleceń shell, cykl życia procesów |
| `wizard` | Wieloetapowy kreator UI |
| `telemetry` | Agregacja metryk i telemetria |
| `database` | Menedżer połączeń, query runner |
| `network` | Klient HTTP, hooki żądań/odpowiedzi |

---

## Struktura generowanego pluginu

Po kliknięciu **✦ Generuj** w wybranym folderze powstaje:

```
NazwaPluginu/
├── manifest.yaml          ← manifest pluginu
├── main.py                ← punkt wejścia, implementacje hooków
├── README.txt
├── CHANGELOG.md
├── requirements.txt
├── integrity.json         ← SHA-256 + MD5 wszystkich plików
├── plugin-info.json       ← manifest API
├── update.json
├── install.ps1 / .bat     ← instalatory Windows
├── config/
│   └── default.json
├── icons/                 ← 5 wariantów SVG
├── ui/                    ← panel HTML + CSS (profile z UI)
├── libs/                  ← biblioteki specyficzne dla profilu
├── tests/                 ← 4 pliki testów pytest
├── selftest.py
├── diagnostics/           ← raporty walidacji
└── generator_plugins/     ← system meta-pluginów
```

Gotowy plugin można spakować przyciskiem **📦 Buduj ZIP** do pliku `.pits-plugin.zip`.

---

## Przełącznik języka

Przycisk **PL / EN** w prawym górnym rogu przełącza interfejs między językiem polskim a angielskim.

---

## Wymagania systemowe

| | |
|-|--|
| **System** | Windows 10 / 11 (64-bit) |
| **Pamięć RAM** | min. 256 MB |
| **Miejsce na dysku** | ~50 MB (plik EXE) |
| **Instalacja** | nie wymagana |
| **Zależności** | brak — wszystko wbudowane w EXE |

---

*2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.*
