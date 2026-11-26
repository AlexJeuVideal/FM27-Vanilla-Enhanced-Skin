"""Prépare « Partage\\Release vX.XX\\ » : le zip du dossier de partage (pour la Release GitHub, mise à jour auto) +
« <nom> vX.XX Setup.exe » (installeur). UI PICKER seulement, jamais livré.

Zip : le dossier de partage lui-même à la racine (sans __pycache__ / app.log / Journal - Log.txt). Setup : le même contenu en ressource
payload.zip + le logo, Setup.cs compilé par le csc de Windows (.NET Framework 4, rien à installer), icône =
outils\\app\\icone.ico. Les deux sont refaits à chaque fois (dossier Release vidé avant).
Usage : fabriquer.py "<dossier de partage>" [dossier de sortie (défaut : <Partage>\\Release vX.XX)]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
CSC = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), r"Microsoft.NET\Framework64\v4.0.30319\csc.exe")
IGNORES = ("__pycache__", "app.log", "Journal - Log.txt")   # journal : celui d'un essai, jamais livré (v1.53)
# v1.87 : chaque fichier du zip / du Setup porte la date de fabrication, jamais celle du disque (un
# fichier pas retouché depuis longtemps montrerait sa vieille date une fois dézippé / installé)
MAINTENANT = time.localtime()[:6]
APPS = ("fm27-serveur.exe", "fm27-serveur-linux", "fm27-serveur-mac")


def ajouter(z, p, nom):
    zi = zipfile.ZipInfo.from_file(p, nom)
    zi.date_time, zi.compress_type = MAINTENANT, zipfile.ZIP_DEFLATED
    # lanceurs et app Rust Linux / Mac : exécutables une fois dézippés (rwxr-xr-x)
    if nom.endswith((".sh", ".command") + APPS[1:]):
        zi.create_system, zi.external_attr = 3, (0o100755 << 16)
    with open(p, "rb") as f:
        z.writestr(zi, f.read())


def main(argv):
    if not argv:
        sys.exit(__doc__)
    partage = os.path.abspath(argv[0]).rstrip("\\/")
    with open(os.path.join(partage, "outils", "commun", "version.txt"), encoding="utf-8") as f:
        nom = re.sub(r"\s+by\s.*$", "", f.read().strip())   # « … v1.16 by AlexJeuVideal x Kinito » -> « … v1.16 »
    version = re.search(r"v\d+\.\d+", nom).group(0)
    sortie = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(os.path.dirname(partage), "Release " + version)
    if os.path.isdir(sortie) and os.listdir(sortie):
        if not os.path.basename(sortie).startswith("Release "):
            sys.exit(f"dossier de sortie pas vide : {sortie}")
        shutil.rmtree(sortie)   # « Release vX.XX » : refait en entier
    os.makedirs(sortie, exist_ok=True)
    exe = os.path.join(sortie, nom + " Setup.exe")
    # v2.17 : les trois apps Rust (compilées : maj_partage ici, release.yml sur GitHub)
    manque = [n for n in APPS if not os.path.isfile(os.path.join(partage, "outils", "app", n))]
    if manque:
        sys.exit("app Rust absente de outils\\app : " + ", ".join(manque))
    fichiers = []
    for d, sous, fs in os.walk(partage):
        sous[:] = [s for s in sous if s not in IGNORES]
        fichiers += [os.path.join(d, fi) for fi in fs if fi not in IGNORES]
    n = len(fichiers)
    # zip de la Release : le dossier de partage à la racine du zip (mise_a_jour.py le retrouve) ; v1.70 : nom complet
    # + « - Linux » (demande du joueur : qu'on s'y retrouve à côté du zip Mac ; la mise à jour auto le prend aussi)
    with open(os.path.join(partage, "outils", "commun", "version.txt"), encoding="utf-8") as f:
        complet = f.read().strip()
    zrelease = os.path.join(sortie, complet + " - Linux.zip")
    with zipfile.ZipFile(zrelease, "w", zipfile.ZIP_DEFLATED) as z:
        for p in fichiers:
            ajouter(z, p, os.path.relpath(p, os.path.dirname(partage)).replace(os.sep, "/"))
    # v1.87 : app unique Windows / Linux / Mac -> zip Mac = le même contenu (nom repéré par le joueur et par la MAJ
    # auto sur Mac ; Windows / Linux l'ignorent)
    shutil.copy2(zrelease, os.path.join(sortie, complet + " - Mac.zip"))
    with tempfile.TemporaryDirectory() as tmp:
        payload = os.path.join(tmp, "payload.zip")   # Setup : contenu du dossier à la racine
        # v2.17 : app Rust, plus de Python embarqué dans le Setup (python_embarque.py n'est plus utilisé)
        with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as z:
            for p in fichiers:
                ajouter(z, p, os.path.relpath(p, partage).replace(os.sep, "/"))
        # Setup unique (v1.68) : dépôt + token lus dans mise_a_jour.py (jamais recopiés à la main) -> ressource maj.txt
        with open(os.path.join(partage, "outils", "commun", "mise_a_jour.py"), encoding="utf-8") as f:
            src = f.read()
        reglages = [re.search(rf'^{k} = "([^"]*)"', src, re.M) for k in ("DEPOT", "TOKEN")]
        if not all(reglages):
            sys.exit("DEPOT / TOKEN introuvables dans mise_a_jour.py")
        maj = os.path.join(tmp, "maj.txt")
        with open(maj, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(m.group(1) for m in reglages) + "\n")
        # v1.88 (SignPath) : nom du produit et version dans les propriétés du .exe, à chaque build
        num = version.lstrip("v")
        info = os.path.join(tmp, "AssemblyInfo.cs")
        with open(info, "w", encoding="utf-8") as f:
            f.write("using System.Reflection;\n"
                    '[assembly: AssemblyTitle("FM27 Vanilla Enhanced Skin Setup")]\n'
                    '[assembly: AssemblyProduct("FM27 Vanilla Enhanced Skin")]\n'
                    '[assembly: AssemblyCompany("AlexJeuVideal x Kinito")]\n'
                    '[assembly: AssemblyCopyright("MIT License - AlexJeuVideal and Kinito")]\n'
                    f'[assembly: AssemblyVersion("{num}.0.0")]\n'
                    f'[assembly: AssemblyFileVersion("{num}.0.0")]\n'
                    f'[assembly: AssemblyInformationalVersion("{num}")]\n')
        cmd = [CSC, "/nologo", "/target:winexe", "/optimize+", f"/out:{exe}", info,
               "/win32icon:" + os.path.join(partage, "outils", "app", "icone.ico"),
               f"/resource:{payload},payload.zip", f"/resource:{maj},maj.txt",
               "/resource:" + os.path.join(partage, "outils", "app", "logo.png") + ",logo.png",
               "/r:System.Windows.Forms.dll", "/r:System.Drawing.dll", "/r:System.IO.Compression.dll",
               "/r:System.IO.Compression.FileSystem.dll", "/r:Microsoft.CSharp.dll", "/r:System.Core.dll",
               "/r:System.Management.dll", "/r:System.Web.Extensions.dll",
               os.path.join(ICI, "Setup.cs")]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="cp850", errors="replace")
        print(r.stdout, r.stderr)
        if r.returncode:
            sys.exit("échec de la compilation")
    print(f"{sortie} : {n} fichiers")
    for p in (zrelease, exe):
        print(f"  {os.path.basename(p)} ({os.path.getsize(p) / 1e6:.2f} Mo)")


if __name__ == "__main__":
    main(sys.argv[1:])
