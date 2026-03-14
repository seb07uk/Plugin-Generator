@echo off
REM ──────────────────────────────────────────────────────────────────────────
REM  polsoft.ITS™ Plugin Generator — skrypt kompilacji Windows
REM  Wersja:      4.2.0
REM  Programista: Sebastian Januchowski
REM  Firma:       polsoft.ITS™ Group
REM  Email:       polsoft.its@fastservice.com
REM  GitHub:      https://github.com/seb07uk
REM  2026© Sebastian Januchowski & polsoft.ITS™. All rights reserved.
REM ──────────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion

set APP_NAME=PluginGenerator
set APP_VERSION=4.2.0
set SPEC_FILE=plugin_generator.spec
set DIST_DIR=dist
set BUILD_DIR=build

echo.
echo  ◈  polsoft.ITS™ Plugin Generator — Kompilacja v%APP_VERSION%
echo  ─────────────────────────────────────────────────────────────
echo.

REM ── Sprawdź Python ────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [BLAD] Python nie jest zainstalowany lub nie jest w PATH.
    echo         Pobierz: https://www.python.org/downloads/
    pause & exit /b 1
)
echo  [OK]   Python znaleziony.

REM ── Sprawdź pip ───────────────────────────────────────────────────────────
pip --version >nul 2>&1
if errorlevel 1 (
    echo  [BLAD] pip nie jest dostepny.
    pause & exit /b 1
)

REM ── Zainstaluj / zaktualizuj PyInstaller ─────────────────────────────────
echo  [INFO] Sprawdzanie PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Instalowanie PyInstaller...
    pip install pyinstaller --quiet
    if errorlevel 1 (
        echo  [BLAD] Instalacja PyInstaller nie powiodla sie.
        pause & exit /b 1
    )
) else (
    echo  [OK]   PyInstaller dostepny.
)

REM ── Opcjonalne zależności (pyyaml, jinja2) ────────────────────────────────
echo  [INFO] Instalowanie opcjonalnych zaleznosci...
pip install pyyaml jinja2 --quiet
echo  [OK]   Zaleznosci zainstalowane.

REM ── Sprawdź pliki źródłowe ────────────────────────────────────────────────
if not exist "plugin_generator.py" (
    echo  [BLAD] Nie znaleziono plugin_generator.py w biezacym katalogu.
    echo         Uruchom skrypt z katalogu zawierajacego pliki zrodlowe.
    pause & exit /b 1
)
echo  [OK]   plugin_generator.py znaleziony.

if not exist "ico.ico" (
    echo  [OSTRZEZENIE] Nie znaleziono ico.ico — EXE bedzie bez ikony.
) else (
    echo  [OK]   ico.ico znaleziony.
)

if not exist "%SPEC_FILE%" (
    echo  [BLAD] Nie znaleziono %SPEC_FILE%.
    pause & exit /b 1
)
echo  [OK]   %SPEC_FILE% znaleziony.

REM ── Czyszczenie poprzedniej kompilacji ───────────────────────────────────
if exist "%DIST_DIR%\%APP_NAME%.exe" (
    echo  [INFO] Usuwanie poprzedniej kompilacji...
    del /f /q "%DIST_DIR%\%APP_NAME%.exe" >nul 2>&1
)
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" >nul 2>&1
)

REM ── Kompilacja ────────────────────────────────────────────────────────────
echo.
echo  [INFO] Kompilacja PyInstaller — proszę czekac...
echo.

pyinstaller "%SPEC_FILE%" --distpath "%DIST_DIR%" --workpath "%BUILD_DIR%" --noconfirm --clean

if errorlevel 1 (
    echo.
    echo  [BLAD] Kompilacja nie powiodla sie!
    echo         Sprawdz komunikaty powyzej.
    pause & exit /b 1
)

REM ── Weryfikacja wyniku ────────────────────────────────────────────────────
if not exist "%DIST_DIR%\%APP_NAME%.exe" (
    echo  [BLAD] Plik %APP_NAME%.exe nie zostal wygenerowany.
    pause & exit /b 1
)

REM ── Informacje o pliku wynikowym ─────────────────────────────────────────
echo.
echo  ─────────────────────────────────────────────────────────────
echo  [OK]   Kompilacja zakonczona pomyslnie!
echo.
for %%F in ("%DIST_DIR%\%APP_NAME%.exe") do (
    echo  Plik:    %%~fF
    echo  Rozmiar: %%~zF bajtow
)
echo.
echo  polsoft.ITS™ Plugin Generator v%APP_VERSION%
echo  2026 Sebastian Januchowski - polsoft.its@fastservice.com
echo  ─────────────────────────────────────────────────────────────
echo.

REM ── Opcjonalne: otwórz folder dist ───────────────────────────────────────
set /p OPEN_FOLDER="Otworzyc folder dist? [T/N]: "
if /i "!OPEN_FOLDER!"=="T" (
    explorer "%DIST_DIR%"
)

endlocal
pause
