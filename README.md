# FM27 Vanilla Enhanced Skin by AlexJeuVideal x Kinito

**FR** — Un skin pour Football Manager 27 qui garde l'esprit de l'interface d'origine en l'améliorant, avec une app
qui l'installe, le règle et le met à jour. Windows, Linux (Proton) et Mac.

**EN** — A Football Manager 27 skin that keeps the spirit of the original interface while improving it, with an app
that installs, tunes and updates it. Windows, Linux (Proton) and Mac.

## Télécharger / Download

Dernière version / latest version : **[Releases](../../releases/latest)**

| Système / System | Fichier / File |
|---|---|
| Windows | `… Setup.exe` |
| Linux (Steam + Proton) | `… - Linux.zip` → `Lancer - Launch.sh` |
| Mac (Steam) | `… - Mac.zip` → `Lancer - Launch.command` |

Mode d'emploi complet / full guide : `LISEZMOI.txt` (in the app folder).

Free code signing provided by [SignPath.io](https://signpath.io), certificate by
[SignPath Foundation](https://signpath.org) — [Code signing policy](CODE_SIGNING_POLICY.md).

## Contenu du dépôt / Repository content

- `app/` — page de l'app, données et scripts du skin / the app page, data and skin scripts
- `rust/` — l'app (Rust, à partir de FM27 Turbo de TonyBoy, avec son accord) : `serveur/` = programme de l'app
  (Windows, Linux, Mac), `core/` = toutes les fonctions du skin / the app (Rust, from TonyBoy's FM27 Turbo, with his
  permission)
- `installeur/` — fabrication du Setup Windows et des zips / builds the Windows Setup and the zips
- `moteur_rust/` — moteur rapide de lecture / écriture des fichiers de FM (Rust, from FM27 Turbo by TonyBoy) / fast
  engine to read / write FM's files
- `.github/workflows/release.yml` — chaque version est construite ici par GitHub Actions / each release is built here
  by GitHub Actions

Le skin ne contient aucun fichier de Football Manager : l'app modifie les fichiers du jeu sur l'ordinateur du joueur
(sauvegarde des originaux comprise). Football Manager appartient à Sports Interactive / SEGA.
The skin ships no Football Manager file: the app edits the game files on the player's computer (originals backed up).
Football Manager belongs to Sports Interactive / SEGA.

## Licence / License

[MIT](LICENSE) — AlexJeuVideal and Kinito ; Rust engine and app base: TonyBoy. Third-party software:
[app/THIRD_PARTY_NOTICES.txt](app/THIRD_PARTY_NOTICES.txt), Rust crates:
[app/THIRD_PARTY_LICENSES - Rust.txt](<app/THIRD_PARTY_LICENSES - Rust.txt>).

## Code signing policy

Free code signing provided by SignPath.io, certificate by SignPath Foundation:
[Code signing policy / Politique de signature](CODE_SIGNING_POLICY.md) (team roles, privacy policy).

## Vie privée / Privacy

L'app ne collecte rien et n'envoie aucune donnée personnelle. Elle se connecte seulement à GitHub (recherche de mise à
jour au démarrage, téléchargement d'une nouvelle version). Les liens (YouTube, Twitch, Discord, X) ne s'ouvrent que si
on clique dessus.
The app collects nothing and sends no personal data. It only connects to GitHub (update check at startup, downloading
a new version). Links (YouTube, Twitch, Discord, X) only open when clicked.

## Merci / Thanks

TonyBoy (FM27 Turbo) — AlexMorak — FM Scout — Jouz & Dhragga (Mac).

## Me retrouver / Find me

[YouTube](https://www.youtube.com/@AlexJeuVideal) · [Twitch](https://www.twitch.tv/alexjeuvideal) ·
[Discord](https://discord.com/invite/tuADR5ZE2X) · [X](https://x.com/AlexJeuVideal)
