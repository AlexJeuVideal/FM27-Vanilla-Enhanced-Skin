# Code signing policy / Politique de signature

Free code signing provided by [SignPath.io](https://signpath.io), certificate by
[SignPath Foundation](https://signpath.org).

## What is signed / Ce qui est signé

The Windows installer (`… Setup.exe`) of each release. It is built from this repository by GitHub Actions
(`.github/workflows/release.yml`) and signed only after a team member approves the signing request.
L'installeur Windows (`… Setup.exe`) de chaque version, construit depuis ce dépôt par GitHub Actions et signé seulement
après approbation de la demande par un membre de l'équipe.

## Team roles / Rôles

- Committers and reviewers / Auteurs et relecteurs : [AlexJeuVideal](https://github.com/AlexJeuVideal)
- Approvers / Approbateurs : [AlexJeuVideal](https://github.com/AlexJeuVideal)

## Privacy policy / Vie privée

This program will not transfer any information to other networked systems unless specifically requested by the user
or the person installing or operating it, except: an update check on GitHub at startup (no personal data sent), and,
on first setup, downloading its Python tools from python.org, PyPI and GitHub.
Ce programme ne transmet aucune information à d'autres systèmes, sauf à la demande de l'utilisateur, et à part : la
recherche de mise à jour sur GitHub au démarrage (aucune donnée personnelle), et, à la première installation, le
téléchargement de ses outils Python (python.org, PyPI, GitHub).
