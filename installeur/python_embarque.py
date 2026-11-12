"""Prépare le Python livré dans le Setup.exe (dossier « python\\ » de l'app) : Python 3.14.8 « embeddable » de
python.org + UnityPy / Pillow + tkinter (fenêtre « Parcourir »). Fait une fois, gardé dans installeur\\python\\
(UI PICKER seulement) ; fabriquer.py l'appelle s'il manque. Figé : changé seulement ici, par nous, dans une release.
Usage : python_embarque.py [--refaire]
"""
import glob
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

VERSION = "3.14.8"
MODULES = ["UnityPy==1.25.4", "Pillow"]
ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, "python")
URL = f"https://www.python.org/ftp/python/{VERSION}/python-{VERSION}-embed-amd64.zip"

# le Python embarqué n'ajoute pas le dossier du script lancé à sys.path (fichier ._pth) : les scripts du skin
# importent leurs voisins (backup, chemins…) -> remis ici, comme un Python normal
SITECUSTOMIZE = '''import os, sys
if sys.argv and sys.argv[0] and sys.argv[0] not in ("-c", "-m") and os.path.isfile(sys.argv[0]):
    sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
'''


FMOD_VIDE = '''"""Remplace fmod_toolkit (bibliothèque audio FMOD, propriétaire) : le skin ne lit jamais de son.
Replaces fmod_toolkit (proprietary FMOD audio library): the skin never reads audio. MIT, AlexJeuVideal and Kinito."""


def raw_to_wav(*args, **kwargs):
    raise RuntimeError("audio non pris en charge / audio not supported")
'''


def preparer():
    base = sys.base_prefix   # Python 3.14 de ce PC (même version) : tkinter et son Tcl/Tk en viennent
    if f"{sys.version_info[0]}.{sys.version_info[1]}" != VERSION.rsplit(".", 1)[0]:
        sys.exit(f"lancer avec un Python {VERSION.rsplit('.', 1)[0]} (le .venv d'UI PICKER)")
    shutil.rmtree(DOSSIER, ignore_errors=True)
    os.makedirs(DOSSIER)
    zp = os.path.join(DOSSIER, "embed.zip")
    print("téléchargement", URL)
    urllib.request.urlretrieve(URL, zp)
    with zipfile.ZipFile(zp) as z:
        z.extractall(DOSSIER)
    os.remove(zp)
    pth = glob.glob(os.path.join(DOSSIER, "python3*._pth"))[0]
    with open(pth, encoding="utf-8") as f:
        lignes = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    with open(pth, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes + [r"Lib\site-packages", "import site"]) + "\n")
    with open(os.path.join(DOSSIER, "sitecustomize.py"), "w", encoding="utf-8") as f:
        f.write(SITECUSTOMIZE)
    sp = os.path.join(DOSSIER, "Lib", "site-packages")
    subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-input",
                    "--prefer-binary", "--target", sp, *MODULES], check=True)
    # v1.88 (SignPath : aucun composant propriétaire dans le Setup signé) : fmod_toolkit embarque fmod.dll (FMOD,
    # propriétaire), seulement pour l'audio des bundles, que le skin ne lit jamais -> remplacé par un module vide
    for d in os.listdir(sp):
        if d.lower().startswith(("fmod_toolkit", "pyfmodex")):
            shutil.rmtree(os.path.join(sp, d))
    os.makedirs(os.path.join(sp, "fmod_toolkit"))
    with open(os.path.join(sp, "fmod_toolkit", "__init__.py"), "w", encoding="utf-8") as f:
        f.write(FMOD_VIDE)
    shutil.copytree(os.path.join(base, "Lib", "tkinter"), os.path.join(sp, "tkinter"),
                    ignore=shutil.ignore_patterns("__pycache__", "test*"))
    for motif in ("_tkinter.pyd", "tcl*.dll", "tk*.dll", "zlib*.dll"):
        for p in glob.glob(os.path.join(base, "DLLs", motif)):
            if not os.path.exists(os.path.join(DOSSIER, os.path.basename(p))):
                shutil.copy2(p, DOSSIER)
    tcl = os.path.join(base, "tcl")   # Tcl 9 : bibliothèque dans la DLL (zipfs), dossier tcl seulement en Tcl 8
    if os.path.isdir(tcl):
        shutil.copytree(tcl, os.path.join(DOSSIER, "tcl"), ignore=shutil.ignore_patterns("*demos*", "*tzdata*"))
    for d, sous, _ in os.walk(DOSSIER):
        for s in [s for s in sous if s == "__pycache__"]:
            shutil.rmtree(os.path.join(d, s))
    print("prêt :", DOSSIER)


if __name__ == "__main__":
    if "--refaire" in sys.argv or not os.path.exists(os.path.join(DOSSIER, "python.exe")):
        preparer()
    else:
        print("déjà prêt :", DOSSIER)
