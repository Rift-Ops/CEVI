# -*- coding: utf-8 -*-
"""
traductions.py — Catalogues de traduction de CEVI.

Chaque catalogue associe un texte FRANÇAIS (celui du code source) à sa
traduction. Les textes à trous s'écrivent avec {nom} des deux côtés :

    "Erreur : {e}": "Error: {e}",

Un texte absent d'un catalogue reste affiché en français : ajoutez simplement
une ligne ici pour le traduire. Pour une nouvelle langue, créez un dictionnaire
(ex. ES = {...}) puis déclarez-le dans noyau/i18n.py (CATALOGUES, NOMS_LANGUES).
"""

EN = {
    # ------------------------------------------------------------ interface
    "Langue": "Language",
    "Langue :": "Language:",
    "Numéro de la langue (Entrée pour annuler) : ": "Language number (Enter to cancel): ",
    "Langue changée : {langue}": "Language changed: {langue}",
    "Quitter": "Quit",
    "Quel choix prendre: ": "Which option? ",
    "Au revoir !": "Goodbye!",
    "Entrée invalide": "Invalid input",
    "Entrée invalide : {e}": "Invalid input: {e}",
    "Entrée invalide: {e}": "Invalid input: {e}",
    "Entrée invalide : un nombre est attendu": "Invalid input: a number is expected",
    "la durée doit être supérieure à 0": "the duration must be greater than 0",
    "Ce paramètre est obligatoire.": "This parameter is required.",
    "(défaut : {defaut})": "(default: {defaut})",
    "CEVI — menu des options": "CEVI — options menu",
    "Action terminée.": "Action finished.",
    "Résultat : {resultat}": "Result: {resultat}",
    "Erreur : {e}": "Error: {e}",
    "Argument invalide : '{brut}' (format attendu : param=valeur)":
        "Invalid argument: '{brut}' (expected format: param=value)",
    "Astuce : 'python main.py -l' montre chaque action et ses paramètres.":
        "Tip: 'python main.py -l' shows every action and its parameters.",
    "PyQt6 n'est pas installé.": "PyQt6 is not installed.",
    "Installez-le avec la commande : pip install PyQt6":
        "Install it with: pip install PyQt6",
    "Impossible de charger l'interface graphique : {e}": "Unable to load the graphical interface: {e}",
    "L'interface graphique n'a pas pu démarrer.": "The graphical interface could not start.",
    "Vérifiez votre installation :  pip install --upgrade PyQt6":
        "Check your installation:  pip install --upgrade PyQt6",
    "CEVI — lanceur unique : ligne de commande ou interface graphique.":
        "CEVI — single launcher: command line or graphical interface.",
    "lancer l'interface graphique (PyQt6)": "start the graphical interface (PyQt6)",
    "afficher la liste des actions disponibles et leurs paramètres":
        "show the available actions and their parameters",
    "exécuter directement une action (voir les identifiants avec -l)":
        "run an action directly (see the identifiers with -l)",
    "paramètres de l'action, ex : --args ip=192.168.1.24 port=5555":
        "action parameters, e.g. --args ip=192.168.1.24 port=5555",
    "langue de l'interface : fr ou en (le choix est mémorisé)":
        "interface language: fr or en (the choice is remembered)",
    "Langue inconnue : '{code}'. Langues disponibles : {liste}":
        "Unknown language: '{code}'. Available languages: {liste}",

    # --------------------------------------------------------------- fenêtre
    "CEVI — Panneau d'actions": "CEVI — Action panel",
    "Console CEVI — les messages des actions s'affichent ici.\n":
        "CEVI console — action messages appear here.\n",
    "Actions disponibles": "Available actions",
    "Paramètres": "Parameters",
    "Console": "Console",
    "Exécuter l'action": "Run the action",
    "Exécution en cours...": "Running...",
    "Effacer la console": "Clear the console",
    "Cette action n'a besoin d'aucun paramètre.": "This action needs no parameters.",
    "Aucune action enregistrée": "No action registered",
    "Aucune action enregistrée.": "No action registered.",
    "Une action est déjà en cours d'exécution.": "An action is already running.",
    "Aucune action sélectionnée.": "No action selected.",
    "Paramètre invalide": "Invalid parameter",
    "\n>>> Exécution de « {nom} »...\n": "\n>>> Running “{nom}”...\n",
    "\n[Résultat] {resultat}\n": "\n[Result] {resultat}\n",
    "Action en cours": "Action in progress",
    "Une action est en cours d'exécution.\nVoulez-vous vraiment quitter ?":
        "An action is running.\nDo you really want to quit?",
    "Erreur interne — CEVI": "Internal error — CEVI",
    "Une erreur est survenue ({contexte}).": "An error occurred ({contexte}).",
    "Erreur au démarrage de l'interface.\nLe détail complet est écrit dans le terminal.":
        "Error while starting the interface.\nFull details are written in the terminal.",
    "Erreur pendant l'exécution : {e}": "Error during execution: {e}",

    # ------------------------------------------------------------- registre
    "{n} actions disponibles :": "{n} actions available:",
    "requis": "required",
    "défaut : {defaut}": "default: {defaut}",
    "Action inconnue : '{identifiant}'. Utilisez 'python main.py -l' pour voir la liste des actions.":
        "Unknown action: '{identifiant}'. Use 'python main.py -l' to see the list of actions.",
    "Paramètre inconnu '{cle}' pour '{identifiant}'. Paramètres acceptés : {valides}":
        "Unknown parameter '{cle}' for '{identifiant}'. Accepted parameters: {valides}",
    "(aucun)": "(none)",
    "Paramètre requis manquant pour '{identifiant}' : {label} ({nom})":
        "Missing required parameter for '{identifiant}': {label} ({nom})",
    "Valeur invalide pour '{nom}' (type attendu : {type}) : '{valeur}' ({e})":
        "Invalid value for '{nom}' (expected type: {type}): '{valeur}' ({e})",
    "répondez par oui/non": "answer yes/no",
    "choisir parmi : {liste}": "choose from: {liste}",
    "[registre] Attention : l'identifiant '{identifiant}' est déjà utilisé, l'ancienne action est remplacée.":
        "[registry] Warning: the identifier '{identifiant}' is already used, the old action is replaced.",

    # ----------------------------------------------------------------- sudo
    "Mot de passe administrateur requis": "Administrator password required",
    "Cette action doit exécuter une commande avec les droits administrateur (sudo).":
        "This action must run a command with administrator rights (sudo).",
    "Mot de passe (sudo) : ": "Password (sudo): ",
    "Mot de passe refusé par sudo (essai {essai}/{total}).":
        "Password rejected by sudo (attempt {essai}/{total}).",
    "Commande lancée : sudo {commande}": "Command run: sudo {commande}",
    "La commande sudo est introuvable sur ce système.": "The sudo command was not found on this system.",
    "Mot de passe non fourni : opération annulée.": "No password provided: operation cancelled.",
    "Mot de passe incorrect après {n} tentatives : opération abandonnée.":
        "Wrong password after {n} attempts: operation aborted.",
    "La commande sudo a dépassé le temps imparti et a été interrompue.":
        "The sudo command exceeded the time limit and was interrupted.",
    "Impossible de lancer sudo : {e}": "Unable to run sudo: {e}",
    "Un mot de passe administrateur (sudo) est requis, mais aucun moyen de le demander n'est disponible (ni interface graphique, ni terminal interactif).":
        "An administrator password (sudo) is required, but there is no way to ask for it (no graphical interface and no interactive terminal).",
    "(aucun message d'erreur)": "(no error message)",

    # ------------------------------------------ CEVI.py : menu et messages
    "Options Disponibles": "Available options",
    "1- Capture d'écran": "1- Screenshot",
    "2- Enregistrement d'écran": "2- Screen recording",
    "3- Connecter le téléphone (Assurez vous que votre appareil ait déjà été connecté au moins une fois, voir 4)":
        "3- Connect the phone (make sure your device has already been connected at least once, see 4)",
    "4- Appairage de l'ordinateur au téléphone": "4- Pair the computer with the phone",
    "5- Quitter": "5- Quit",
    "6- Langue": "6- Language",
    "Commande lancée: sudo apt install linux-headers-generic":
        "Command run: sudo apt install linux-headers-generic",
    "Commande lancée: sudo apt install v4l2loopback-dkms v4l2loopback-utils -y":
        "Command run: sudo apt install v4l2loopback-dkms v4l2loopback-utils -y",
    "Vérification de la présence de v4l2loopback": "Checking that v4l2loopback is present",
    "Module absent, installation des headers génériques pour linux...":
        "Module missing, installing the generic Linux headers...",
    "Installation du module v4l2loopback": "Installing the v4l2loopback module",
    "Installation des headers et du module v4l2loopback terminée":
        "Headers and v4l2loopback module installation finished",
    "module v4l2loopback présent": "v4l2loopback module present",
    "Module v4l2loopback présent": "v4l2loopback module present",
    "adb ne répond pas (délai dépassé)": "adb is not responding (timeout)",
    "Aucun résultat détecté": "No result detected",
    "Appli supportée à l'écran": "Supported app on screen",
    "Appli non supportée": "Unsupported app",
    "Lancement de scrcpy en arrière plan": "Starting scrcpy in the background",
    "Capture en cours...": "Capturing...",
    "Capture terminée": "Capture finished",
    "Échec de la capture (ffmpeg a renvoyé le code {code})":
        "Capture failed (ffmpeg returned code {code})",
    "Aucune réponse d'adb.": "No response from adb.",
    "Connexion échouée (connexion refusée).": "Connection failed (connection refused).",
    "Connexion échouée : {detail}": "Connection failed: {detail}",
    "Connecté avec succès.": "Connected successfully.",
    "Réponse d'adb : {detail}": "adb response: {detail}",
    "Installation de ffmpeg": "Installing ffmpeg",
    "ffmpeg installé, relancez le script": "ffmpeg installed, restart the script",
    "ffmpeg détecté": "ffmpeg detected",
    "modprobe absent, installation lancée": "modprobe missing, installation started",
    "Installation terminée, relancez le script": "Installation finished, restart the script",
    "modprobe détecté": "modprobe detected",
    "Écrivez le plus grand chiffre que vous voyez: ": "Type the highest number you see: ",
    "Appli détectée": "App detected",
    "Appli non supportée, relancez le script lorsque vous serez sur whatsapp ou facebook":
        "Unsupported app, restart the script once you are on WhatsApp or Facebook",
    "Impossible de vérifier l'appli, vérifiez la connexion adb puis relancez le script":
        "Unable to check the app, check the adb connection then restart the script",
    "Mettez en seconde le temps d'enregistrement: ": "Recording time in seconds: ",
    "Enregistrement commencé pour {c} secondes": "Recording started for {c} seconds",
    "Enregistrement terminé avec succès": "Recording finished successfully",
    "Désactivation du module v4l2loopback...": "Unloading the v4l2loopback module...",
    "Relancez le script": "Restart the script",
    "Appareil déjà connecté": "Device already connected",
    "Entrez les infos": "Enter the details",
    "IP du téléphone local: ": "Phone local IP: ",
    "PORT: ": "PORT: ",
    "connexion en cours...": "connecting...",
    "Sur le téléphone : Options pour les développeurs > Débogage sans fil > Associer l'appareil avec un code d'association":
        "On the phone: Developer options > Wireless debugging > Pair device with pairing code",
    "PORT d'appairage (celui de la fenêtre d'association): ": "PAIRING port (from the pairing window): ",
    "Code d'appairage à 6 chiffres: ": "6-digit pairing code: ",
    "Appairage réussi, vous pouvez maintenant utiliser l'option 3":
        "Pairing succeeded, you can now use option 3",
    "ffmpeg présent": "ffmpeg present",
    "ffmpeg absent": "ffmpeg missing",
    "modprobe présent": "modprobe present",
    "modprobe absent": "modprobe missing",

    # ------------------------------------------------- actions : capture.py
    "Capture d'écran du téléphone": "Phone screenshot",
    "Reprend le déroulé de l'option 1 de CEVI.py : vérifie ffmpeg et modprobe, vérifie/active v4l2loopback, lance scrcpy vers le périphérique vidéo choisi puis capture une image avec ffmpeg.":
        "Follows option 1 of CEVI.py: checks ffmpeg and modprobe, checks/enables v4l2loopback, starts scrcpy towards the chosen video device, then captures an image with ffmpeg.",
    "Numéro du périphérique vidéo": "Video device number",
    "scrcpy envoie le flux vers /dev/video<N> et la capture lit ce même périphérique":
        "scrcpy sends the stream to /dev/video<N> and the capture reads that same device",
    "ffmpeg absent : utilisez l'action 'installer_ffmpeg' puis relancez.":
        "ffmpeg missing: use the 'installer_ffmpeg' action then try again.",
    "modprobe absent : utilisez l'action 'installer_modprobe' puis relancez.":
        "modprobe missing: use the 'installer_modprobe' action then try again.",
    "Chargement du module v4l2loopback (mot de passe demandé si nécessaire)...":
        "Loading the v4l2loopback module (password requested if needed)...",
    "Impossible de charger v4l2loopback :\n{detail}\nSi le module n'est pas installé, lancez d'abord les actions 'installer_headers' et 'installer_v4l2loopback'.":
        "Unable to load v4l2loopback:\n{detail}\nIf the module is not installed, first run the 'installer_headers' and 'installer_v4l2loopback' actions.",
    "module v4l2loopback chargé": "v4l2loopback module loaded",
    "Lancement de scrcpy vers /dev/video{n}...": "Starting scrcpy towards /dev/video{n}...",
    "Attente de 2 secondes pour le démarrage du flux...": "Waiting 2 seconds for the stream to start...",
    "Capture d'écran effectuée.": "Screenshot taken.",
    "La capture a échoué : voir les messages de ffmpeg ci-dessus.":
        "The capture failed: see the ffmpeg messages above.",
    "Impossible de vérifier l'appli : {detail}": "Unable to check the app: {detail}",
    "Appli non supportée, arrêt du serveur adb...": "Unsupported app, stopping the adb server...",
    "Appli non supportée : ouvrez WhatsApp ou Facebook sur le téléphone puis relancez.":
        "Unsupported app: open WhatsApp or Facebook on the phone then try again.",
    "Erreur pendant la capture : {e}": "Error during capture: {e}",
    "Enregistrement d'écran du téléphone": "Phone screen recording",
    "Reprend le déroulé de l'option 2 de CEVI.py : vérifie l'application affichée, enregistre l'écran du téléphone via scrcpy pendant la durée choisie, puis décharge le module v4l2loopback.":
        "Follows option 2 of CEVI.py: checks the displayed app, records the phone screen through scrcpy for the chosen duration, then unloads the v4l2loopback module.",
    "Durée (secondes)": "Duration (seconds)",
    "Durée de l'enregistrement en secondes": "Recording duration in seconds",
    "Nom du fichier": "File name",
    "Laissez vide pour un nom automatique basé sur la date et l'heure":
        "Leave empty for an automatic name based on the date and time",
    "Enregistrement lancé pour {duree} secondes...": "Recording started for {duree} seconds...",
    "Impossible de décharger v4l2loopback : {detail}": "Unable to unload v4l2loopback: {detail}",
    "Désactivation ignorée : {e}": "Unloading skipped: {e}",
    "Enregistrement terminé : {nom}": "Recording finished: {nom}",
    "Erreur pendant l'enregistrement : {e}": "Error during recording: {e}",

    # ---------------------------------------------- actions : connexion.py
    "Connecter le téléphone (adb)": "Connect the phone (adb)",
    "Reprend le déroulé de l'option 3 de CEVI.py : vérifie si un appareil est déjà connecté, sinon relance le serveur adb et tente une connexion sans fil avec l'IP et le port du téléphone sur le réseau local.":
        "Follows option 3 of CEVI.py: checks whether a device is already connected, otherwise restarts the adb server and tries a wireless connection with the phone's IP and port on the local network.",
    "IP du téléphone (réseau local)": "Phone IP (local network)",
    "Exemple : 192.168.1.24": "Example: 192.168.1.24",
    "Port": "Port",
    "Exemple : 5555": "Example: 5555",
    "Appareil déjà connecté.": "Device already connected.",
    "Connexion en cours...": "Connecting...",
    "Erreur pendant la connexion : adb ne répond pas (délai dépassé).":
        "Error while connecting: adb is not responding (timeout).",
    "Erreur pendant la connexion : {e}": "Error while connecting: {e}",
    "Appairer le téléphone (adb pair)": "Pair the phone (adb pair)",
    "Reprend l'option 4 de CEVI.py (jamais implémentée à l'origine) : associe l'ordinateur au téléphone avec le code à 6 chiffres affiché dans Options pour les développeurs > Débogage sans fil > Associer l'appareil.":
        "Follows option 4 of CEVI.py (never implemented originally): pairs the computer with the phone using the 6-digit code shown in Developer options > Wireless debugging > Pair device.",
    "Port d'appairage": "Pairing port",
    "Port affiché dans la fenêtre d'association (différent de celui de connexion)":
        "Port shown in the pairing window (different from the connection port)",
    "Code d'appairage": "Pairing code",
    "Code à 6 chiffres affiché sur le téléphone": "6-digit code shown on the phone",
    "Erreur pendant l'appairage : adb ne répond pas (délai dépassé).":
        "Error while pairing: adb is not responding (timeout).",
    "Erreur pendant l'appairage : {e}": "Error while pairing: {e}",
    "Déconnecter le téléphone (adb kill-server)": "Disconnect the phone (adb kill-server)",
    "Arrête le serveur adb de l'ordinateur (coupe aussi les sessions scrcpy adb).":
        "Stops the computer's adb server (also cuts adb scrcpy sessions).",
    "Serveur adb arrêté.": "adb server stopped.",

    # --------------------------------------------- actions : diagnostic.py
    "Diagnostic de l'environnement": "Environment diagnostic",
    "Vérifie la présence de ffmpeg et modprobe, liste les périphériques /dev/video* et teste la connexion adb. Aucune modification n'est effectuée sur le système.":
        "Checks that ffmpeg and modprobe are present, lists the /dev/video* devices and tests the adb connection. Nothing is changed on the system.",
    "Périphériques vidéo : {liste}": "Video devices: {liste}",
    "Périphériques vidéo : aucun (/dev/video*)": "Video devices: none (/dev/video*)",
    "adb : introuvable (vérifiez le dossier outils/)": "adb: not found (check the outils/ folder)",
    "adb devices : délai dépassé": "adb devices: timeout",
    "adb : erreur ({e})": "adb: error ({e})",
    "(réponse vide)": "(empty response)",
    "Diagnostic terminé : voir les détails ci-dessus.": "Diagnostic finished: see the details above.",
    "Lister les périphériques vidéo": "List video devices",
    "Affiche la liste des périphériques /dev/video* présents sur l'ordinateur.":
        "Shows the /dev/video* devices present on the computer.",
    "{n} périphérique(s) trouvé(s).": "{n} device(s) found.",
    "Aucun périphérique /dev/video* détecté": "No /dev/video* device detected",
    "Aucun périphérique détecté.": "No device detected.",
    "Vérifier l'application affichée sur le téléphone": "Check the app shown on the phone",
    "Indique si l'application affichée à l'écran du téléphone est supportée (WhatsApp ou Facebook). Réutilise verifi_quel_appli() de CEVI.py.":
        "Tells whether the app shown on the phone screen is supported (WhatsApp or Facebook). Reuses verifi_quel_appli() from CEVI.py.",

    # -------------------------------------------- actions : installation.py
    "Installer ffmpeg": "Install ffmpeg",
    "Installe ffmpeg (sudo apt install ffmpeg -y). Le mot de passe administrateur est demandé explicitement : dialogue en mode graphique, saisie cachée dans le terminal.":
        "Installs ffmpeg (sudo apt install ffmpeg -y). The administrator password is explicitly requested: dialog in graphical mode, hidden input in the terminal.",
    "Installer modprobe": "Install modprobe",
    "Installe modprobe, fourni par le paquet kmod (sudo apt install kmod -y). Le mot de passe administrateur est demandé explicitement : dialogue en mode graphique, saisie cachée dans le terminal.":
        "Installs modprobe, provided by the kmod package (sudo apt install kmod -y). The administrator password is explicitly requested: dialog in graphical mode, hidden input in the terminal.",
    "Installer les en-têtes Linux": "Install the Linux headers",
    "Installe linux-headers-generic (sudo apt install linux-headers-generic -y), comme install_linux_headers_generic de CEVI.py. Le mot de passe administrateur est demandé explicitement.":
        "Installs linux-headers-generic (sudo apt install linux-headers-generic -y), like install_linux_headers_generic in CEVI.py. The administrator password is explicitly requested.",
    "Installer v4l2loopback": "Install v4l2loopback",
    "Installe v4l2loopback-dkms et v4l2loopback-utils (sudo apt install ... -y), comme install_v4l2loopback de CEVI.py. Le mot de passe administrateur est demandé explicitement.":
        "Installs v4l2loopback-dkms and v4l2loopback-utils (sudo apt install ... -y), like install_v4l2loopback in CEVI.py. The administrator password is explicitly requested.",
    "Charger le module v4l2loopback": "Load the v4l2loopback module",
    "Lance 'sudo modprobe v4l2loopback' pour activer la caméra virtuelle. Le mot de passe administrateur est demandé explicitement (dialogue en mode graphique, saisie cachée dans le terminal).":
        "Runs 'sudo modprobe v4l2loopback' to enable the virtual camera. The administrator password is explicitly requested (dialog in graphical mode, hidden input in the terminal).",
    "Installation de {nom} terminée.": "Installation of {nom} finished.",
    "Échec de l'installation de {nom} (code retour {code}) :\n{detail}":
        "Installation of {nom} failed (return code {code}):\n{detail}",
    "Module v4l2loopback chargé.": "v4l2loopback module loaded.",
    "Échec du chargement de v4l2loopback (code retour {code}) :\n{detail}\nSi le module n'est pas installé, lancez d'abord les actions 'installer_headers' et 'installer_v4l2loopback'.":
        "Failed to load v4l2loopback (return code {code}):\n{detail}\nIf the module is not installed, first run the 'installer_headers' and 'installer_v4l2loopback' actions.",
}
