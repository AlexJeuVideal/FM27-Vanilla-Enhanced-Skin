#!/bin/sh
# Lanceur Linux de l'app du skin (FM27 lance par Proton / Steam) : ouvre l'app en arriere-plan. L'app fait tout le
# reste (langue, outils Python dans .venv, dossier du jeu, installation). Copie a la racine du dossier de partage.
# Linux launcher (FM27 run through Proton / Steam): opens the app in the background; the app does everything else.
cd "$(dirname "$0")" || exit 1
# v2.17 : l'app est un programme (Rust), plus besoin de Python
if [ -f "outils/app/fm27-serveur-linux" ]; then
  chmod 755 "outils/app/fm27-serveur-linux" 2>/dev/null
  mkdir -p backups
  nohup "outils/app/fm27-serveur-linux" >>backups/app.log 2>&1 &
  exit 0
fi
PY=""
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  # 3.14 au plus : UnityPy / lz4 / brotli sans roue pour 3.15 (2026-11-12)
  for v in python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v "$v" >/dev/null 2>&1; then PY="$v"; break; fi
  done
fi
if [ -z "$PY" ]; then
  MSG="Python 3 est introuvable : installe python3 et python3-venv avec le gestionnaire de paquets de ta distribution, puis relance ce fichier. Il faut Python 3.8 à 3.14 : pas 3.15, trop récent pour le skin (dans ce cas, installe python3.14 et python3.14-venv).

Python 3 was not found: install python3 and python3-venv with your distribution's package manager, then run this file again. Python 3.8 to 3.14 is needed: not 3.15, too new for the skin (if so, install python3.14 and python3.14-venv)."
  if command -v zenity >/dev/null 2>&1; then
    zenity --error --title="FM27 Vanilla Enhanced Skin" --text="$MSG"
  elif command -v kdialog >/dev/null 2>&1; then
    kdialog --title "FM27 Vanilla Enhanced Skin" --error "$MSG"
  else
    echo "$MSG"
  fi
  exit 1
fi
mkdir -p backups
nohup "$PY" outils/app/serveur.py >>backups/app.log 2>&1 &
