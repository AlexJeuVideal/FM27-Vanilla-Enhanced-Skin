@echo off
rem Lanceur de l'app du skin (dossier de partage) : ouvre l'app, sans fenetre noire. L'app fait tout le reste
rem (langue, outils Python, dossier du jeu, installation). Ce fichier est copie a la racine du dossier de partage.
cd /d "%~dp0"
rem v2.17 : l'app est un programme (Rust), plus besoin de Python
if exist "outils\app\fm27-serveur.exe" goto rust
rem python\ : Python 3.14 livre par le Setup (rien a installer) ; sinon .venv / Python du PC (installations d'avant)
if exist "python\pythonw.exe" goto embarque
if exist ".venv\Scripts\pythonw.exe" goto venv
where pyw >nul 2>nul
if not errorlevel 1 goto pyw
where pythonw >nul 2>nul
if not errorlevel 1 goto pythonw
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Python 3 est introuvable. Installe Python 3.14 (la page s''ouvre : Windows installer 64-bit ; pas 3.15, trop recent pour le skin), coche Add python.exe to PATH, puis relance ce fichier.' + [char]10 + [char]10 + 'Python 3 was not found. Install Python 3.14 (the page opens: Windows installer 64-bit; not 3.15, too new for the skin), tick Add python.exe to PATH, then run this file again.', 'FM27 Vanilla Enhanced Skin') | Out-Null"
rem 3.14 et pas la derniere : UnityPy / lz4 / brotli sans roue Windows pour 3.15 (2026-11-12)
start "" https://www.python.org/downloads/release/python-3148/
exit /b
:rust
start "" "outils\app\fm27-serveur.exe"
exit /b
:embarque
start "" "python\pythonw.exe" outils\app\serveur.py
exit /b
:venv
start "" ".venv\Scripts\pythonw.exe" outils\app\serveur.py
exit /b
:pyw
start "" pyw -3 outils\app\serveur.py
exit /b
:pythonw
start "" pythonw outils\app\serveur.py
exit /b
