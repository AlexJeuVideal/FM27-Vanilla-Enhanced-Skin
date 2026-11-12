#!/bin/bash
# Lanceur Mac de l'app du skin (FM27 natif, Steam) : double-clic dans le Finder. Au premier lancement, prepare son
# propre Python (dossier python/, rien a installer) ; ouvre l'app, qui fait tout le reste. Laisse cette fenetre
# ouverte pendant que tu utilises l'app : la fermer arrete l'app.
# Mac launcher (native FM27, Steam): double-click in Finder. First time, it sets up its own Python (python/ folder,
# nothing to install); opens the app, which does everything else. Keep this window open while you use the app.
cd "$(dirname "$0")" || exit 1
# zip telecharge : macOS met tout le dossier en quarantaine ; le moteur rapide (.so) serait alors refuse au chargement
xattr -dr com.apple.quarantine . >/dev/null 2>&1
mkdir -p backups

# --- Python embarque (v1.87) : Python 3.14.8 autonome (python-build-standalone), fige comme celui du Setup Windows ---
PYE="python/bin/python3"
TAG="20261020"
case "$(uname -m)" in
  arm64)  ARCH="aarch64"; SHA="54eafeb1703dd5d150d45d07bbccb650fab4d2ee75e6928862597a8676cf9105" ;;
  x86_64) ARCH="x86_64";  SHA="66155f929a4b1ef9f756698ba36b00418cb439907673b5b3145c6565151ecddd" ;;
  *)      ARCH="" ;;
esac
if [ -n "$ARCH" ] && ! "$PYE" -c "import UnityPy, PIL" >/dev/null 2>&1; then
  echo "Premiere ouverture : preparation de Python (une seule fois, 1 a 2 minutes, internet requis)..."
  echo "First start: setting up Python (only once, 1 to 2 minutes, internet needed)..."
  if [ ! -x "$PYE" ]; then
    rm -rf python python_tmp.tar.gz
    URL="https://github.com/astral-sh/python-build-standalone/releases/download/$TAG/cpython-3.14.8%2B$TAG-$ARCH-apple-darwin-install_only.tar.gz"
    if curl -fL --retry 2 --progress-bar -o python_tmp.tar.gz "$URL" \
       && [ "$(shasum -a 256 python_tmp.tar.gz | cut -d' ' -f1)" = "$SHA" ] \
       && tar -xzf python_tmp.tar.gz; then
      :
    else
      echo "Telechargement de Python rate / Python download failed"
      rm -rf python
    fi
    rm -f python_tmp.tar.gz
  fi
  if [ -x "$PYE" ]; then
    # outils du skin ; s'ils ratent ici, l'etape « Outils » de l'app les reinstalle
    "$PYE" -m pip install --disable-pip-version-check --no-input -q "UnityPy==1.25.4" Pillow \
      || echo "Outils pas installes : l'app les reinstallera / Tools not installed: the app will retry"
  fi
fi

PY=""
if [ -x "$PYE" ]; then
  PY="$PYE"
elif [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  # secours (pas d'internet au premier lancement) : un Python deja installe, 3.14 au plus
  for v in python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 \
           /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 \
           /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
           /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
           /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 /usr/bin/python3; do
    if command -v "$v" >/dev/null 2>&1 && "$v" -c "import sys" >/dev/null 2>&1; then PY="$v"; break; fi
  done
fi
if [ -z "$PY" ]; then
  MSG="Python n'a pas pu etre prepare : verifie ta connexion internet et relance ce fichier.

Python could not be set up: check your internet connection and run this file again."
  osascript -e "display dialog \"$MSG\" with title \"FM27 Vanilla Enhanced Skin\" buttons {\"OK\"} default button 1" >/dev/null 2>&1 || echo "$MSG"
  exit 1
fi
echo "FM27 Vanilla Enhanced Skin : l'app s'ouvre (laisse cette fenetre ouverte) / the app is opening (keep this window open)"
exec "$PY" outils/app/serveur.py
