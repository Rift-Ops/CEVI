# CEVI

🇬🇧 [Read in English](README.md)

[![License: GNUv3](https://img.shields.io/badge/License-GNUv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

CEVI — boîte à outils Android sous Linux : connectez votre téléphone en Wi-Fi (ADB),
affichez et enregistrez son écran avec scrcpy + v4l2loopback, lancez des diagnostics
et installez les dépendances avec une demande explicite du mot de passe sudo.
Architecture à extensions : déposez un fichier Python dans `actions/` et il fonctionne
à la fois en ligne de commande et dans l'interface graphique PyQt6.

## Fonctionnalités

- **Capture et enregistrement d'écran** d'un téléphone Android directement depuis Linux
- **Capture « Vue unique »** — enregistrez les photos/vidéos à vue unique de WhatsApp et Facebook
- **Connexion sans fil** au téléphone via ADB en Wi-Fi, avec appairage
- **Interface graphique** (PyQt6) : formulaires générés automatiquement, console en direct
  et demande explicite du mot de passe sudo
- **Système d'extensions** — chaque action est un fichier Python autonome, détecté automatiquement
- Fonctionne de la même façon en **ligne de commande** et en **mode graphique**

## Prérequis

- Linux (droits sudo nécessaires pour l'installation et le chargement des modules)
- Python 3.8+
- Paquet Python : `pip install PyQt6`
- Outils système : `adb`, `scrcpy`, `ffmpeg`, `v4l2loopback`
  (CEVI peut installer ceux qui manquent — voir les actions `installer_*`)

## Installation

```bash
python -m venv venv && source venv/bin/activate
git clone https://github.com/Rift-Ops/CEVI.git
cd CEVI && cd CEVI
pip install PyQt6
unzip ../outils.zip -d .   # adb + scrcpy -> CEVI/outils/ (facultatif s'ils sont déjà installés)
```

adb et scrcpy sont cherchés d'abord dans `CEVI/outils/`, puis dans le `PATH` du système.

Activez le débogage USB sur le téléphone, puis appairez-le une fois avec l'action
`appairer_telephone` (ou `adb pair <ip-du-téléphone>:<port>`) pour l'usage sans fil.

## Utilisation

**Mode graphique :**

```bash
python main.py -mg
```

**Lister les actions disponibles :**

```bash
python main.py -l
```

**Exécuter une action depuis le terminal :**

```bash
# Capturer l'écran du téléphone
python main.py -e capture_ecran

# Enregistrer l'écran pendant 10 secondes
python main.py -e enregistrer_ecran --args duree=10

# Appairer puis connecter le téléphone en Wi-Fi
python main.py -e appairer_telephone --args ip=192.168.1.24 port=37000 code=123456
python main.py -e connecter_telephone --args ip=192.168.1.24 port=5555
```

**Menu interactif :**

```bash
python main.py
```

Quand une action exige les droits administrateur (par exemple charger le module
`v4l2loopback`), CEVI **demande explicitement votre mot de passe sudo** — par une boîte
de dialogue en mode graphique, ou par une saisie masquée dans le terminal. Le mot de passe
n'est ni affiché ni conservé.

## Fonctionnement — capture des médias « Vue unique »

CEVI capture les photos à vue unique de WhatsApp et Facebook en reproduisant l'écran du
téléphone sur l'ordinateur, au lieu de faire une capture d'écran sur l'appareil. Trois
composants Linux standards sont utilisés :

1. **v4l2loopback** (module noyau) — crée une caméra virtuelle sur le PC (`/dev/video2`).
2. **scrcpy** (mode sans fenêtre) — envoie l'écran du téléphone vers ce périphérique :
   `scrcpy --no-window --v4l2-sink=/dev/video2`.
3. **ffmpeg** — lit une seule image de la caméra virtuelle et l'enregistre en PNG horodaté :
   `ffmpeg -i /dev/video2 -frames:v 1 <date>_<heure>capture.png`.

Avant la capture, CEVI vérifie quelle application est au premier plan en lisant
`mCurrentFocus` dans la sortie de `dumpsys window` d'Android, et ne continue que si
WhatsApp ou Facebook est affiché. Il suffit alors d'ouvrir la photo sur le téléphone :
pendant qu'elle s'affiche sur l'écran reproduit, ffmpeg saisit l'image côté ordinateur.

L'image étant prise depuis la caméra virtuelle du PC, le téléphone n'effectue jamais de
capture d'écran lui-même : la capture se fait entièrement en dehors de l'application.

Pour les **vidéos à vue unique**, utilisez l'enregistrement d'écran : scrcpy enregistre le
flux dans un fichier MP4 pendant la durée choisie (puis v4l2loopback est déchargé).

## Actions disponibles

| Action                       | Description                                                    |
| ---------------------------- | -------------------------------------------------------------- |
| `capture_ecran`              | Capture d'écran du téléphone (photos à vue unique)             |
| `enregistrer_ecran`          | Enregistrement d'écran en MP4 (vidéos à vue unique)            |
| `connecter_telephone`        | Connexion du téléphone en Wi-Fi (ADB TCP/IP)                   |
| `appairer_telephone`         | Appairage de l'ordinateur et du téléphone (`adb pair`)         |
| `deconnecter_adb`            | Arrêt du serveur ADB                                           |
| `diagnostic`                 | Vérifie que tout est installé et accessible                    |
| `lister_peripheriques_video` | Liste les périphériques `/dev/video*`                          |
| `verifier_appli`             | Indique quelle application est au premier plan                 |
| `installer_headers`          | Installe les en-têtes Linux (sudo)                             |
| `installer_ffmpeg`           | Installe ffmpeg (sudo)                                         |
| `installer_modprobe`         | Installe modprobe (paquet kmod, sudo)                          |
| `installer_v4l2loopback`     | Installe v4l2loopback (sudo)                                   |
| `lancer_v4l2loopback`        | Charge le module v4l2loopback (sudo)                           |

## Quelques captures d'écran

1. Le champ qui permet de définir la durée d'enregistrement de l'écran du téléphone relié au PC via adb.
   En arrière-plan, il utilise le module v4l2loopback du noyau Linux (installé automatiquement s'il est absent).

![Champ de durée d'enregistrement](screenshots/Capture%20d%E2%80%99%C3%A9cran%20du%202026-08-30%2017-58-22.png)

2. Ici, vous choisissez le numéro du périphérique virtuel créé par v4l2loopback (caméra virtuelle) qui permet l'enregistrement et la capture d'écran.

![Choix du périphérique virtuel](screenshots/Capture%20d%E2%80%99%C3%A9cran%20du%202026-09-01%2018-59-41.png)

3. L'interface pour définir l'IP et le port avec lesquels l'ordinateur se connecte à votre téléphone via adb.

![Paramètres de connexion ADB](screenshots/Capture%20d%E2%80%99%C3%A9cran%20du%202026-09-01%2019-07-40.png)

4. Le reste de l'interface permet d'**installer facilement les dépendances** nécessaires à v4l2loopback.

![Installation des dépendances](screenshots/Capture%20d%E2%80%99%C3%A9cran%20du%202026-09-01%2019-10-40.png)

## Ajouter vos propres actions

CEVI fonctionne par extensions : créez un fichier `.py` dans le dossier `actions/`,
enregistrez votre fonction, et elle apparaît aussitôt dans la liste en ligne de commande
et dans l'interface graphique, sans autre modification.

```python
# actions/bonjour.py
from noyau.registre import enregistrer_action, Parametre

@enregistrer_action(
    "bonjour", "Dire bonjour",
    "Une action minimale.",
    parametres=[Parametre("nom", type="str", defaut="le monde")],
)
def bonjour(nom="le monde"):
    return f"Bonjour, {nom} !"
```

```bash
python main.py -e bonjour --args nom=CEVI
```

## Avertissement ⚠️

Ce projet est proposé à des fins éducatives et personnelles. Ne conservez que des médias
que vous avez le droit de garder, et respectez la vie privée des personnes avec lesquelles
vous communiquez ainsi que les conditions d'utilisation de l'application concernée.
Toute utilisation en dehors de ce cadre se fait à vos seuls risques.

## Licence

Ce projet est placé sous licence **GNU General Public License v3.0** — voir le fichier
[LICENSE.md](LICENSE.md).
