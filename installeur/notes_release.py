"""Texte de la Release GitHub tiré de « NOTES DE MISE A JOUR.md » : la section de la version (français puis anglais)
+ la ligne « Code signing policy » (exigée par SignPath sur les pages de téléchargement).
Usage : notes_release.py "<NOTES DE MISE A JOUR.md>" v1.XX "<sortie.md>"
"""
import re
import sys

POLITIQUE = ("Code signing policy: free code signing provided by SignPath.io, certificate by SignPath Foundation — "
             "https://github.com/AlexJeuVideal/FM27-Vanilla-Enhanced-Skin/blob/main/CODE_SIGNING_POLICY.md")


def section(texte, langue, version):
    """corps de « ### v1.XX … » sous « ## <langue> », jusqu'au titre suivant"""
    bloc = texte.split(f"## {langue}", 1)[1]
    bloc = re.split(r"^## ", bloc, maxsplit=1, flags=re.M)[0]
    m = re.search(rf"^### {re.escape(version)}\b[^\n]*\n(.*?)(?=^### |\Z)", bloc, re.M | re.S)
    if not m:
        sys.exit(f"pas de section {version} en {langue} dans les NOTES")
    return m.group(1).strip()


def main(argv):
    notes, version, sortie = argv
    texte = open(notes, encoding="utf-8").read()
    corps = (f"FRANÇAIS\n\n{section(texte, 'Français', version)}\n\n"
             f"ENGLISH\n\n{section(texte, 'English', version)}\n\n---\n\n{POLITIQUE}\n")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(corps)
    print(corps)


if __name__ == "__main__":
    main(sys.argv[1:])
