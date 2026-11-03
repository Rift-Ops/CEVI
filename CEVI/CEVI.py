# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Pul-07 — CEVI est un logiciel libre sous licence GNU GPL v3 (voir LICENSE).
import subprocess as sps
from vrbls import adb, scrcpy
import time as t
import ver_bin as vb
import glob as g
import datetime as dt
import os

from noyau.i18n import _, choisir_langue_terminal

# Messages renvoyés par verifi_quel_appli(). Ils sont comparés avec
# appli_supportee() et NON avec un test du genre `"supportée" in message` :
# "Appli non supportée" contient lui aussi le mot "supportée", ce qui faisait
# croire à tort qu'une appli non supportée l'était.
MSG_APPLI_OK = "Appli supportée à l'écran"
MSG_APPLI_NON = "Appli non supportée"
MSG_AUCUN_RESULTAT = "Aucun résultat détecté"


def horodatage():
    """Date et heure actuelles, recalculées à chaque appel.

    Avant, l'heure était calculée une seule fois à l'import du fichier : toutes
    les captures d'une même session portaient le même nom et s'écrasaient.
    """
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def install_linux_headers_generic():
    try:
        print("Commande lancée: sudo apt install linux-headers-generic")
        cmd = ["sudo", "apt", "install", "linux-headers-generic", "-y"]

        proc = sps.run(
            cmd,
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )

        print(proc)
    except (TypeError, OSError, ValueError) as e:
        print(e)

def install_v4l2loopback():
    try:
        print("Commande lancée: sudo apt install v4l2loopback-dkms v4l2loopback-utils -y")
        # "-y" était affiché mais absent de la commande : apt attendait une
        # confirmation qui ne venait jamais.
        cmd = ["sudo", "apt", "install", "v4l2loopback-dkms", "v4l2loopback-utils", "-y"]

        proc = sps.run(
            cmd,
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )

        print(proc)
    except (TypeError, OSError, ValueError) as e:
        print(e)

def v4l2loopback_disponible():
    """True si le module v4l2loopback est chargé ou installé sur le système."""
    if os.path.isdir("/sys/module/v4l2loopback"):
        return True
    modinfo = vb.trouver_binaire("modinfo")
    if not modinfo:
        return False
    try:
        proc = sps.run(
            [modinfo, "v4l2loopback"],
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )
    except OSError:
        return False
    return proc.returncode == 0

def verifi_v4l2loopback():
    # Avant : la fonction lançait "modprobe" sans les droits root puis cherchait
    # le mot "mCurrentFocus" (copié de verifi_quel_appli) dans sa sortie : le
    # module était donc toujours déclaré "présent". On interroge maintenant
    # directement le système (module chargé ou fichier du module installé).
    try:
        print("Vérification de la présence de v4l2loopback")

        if not v4l2loopback_disponible():
            print("Module absent, installation des headers génériques pour linux...")
            install_linux_headers_generic()
            print("Installation du module v4l2loopback")
            install_v4l2loopback()
            return "Installation des headers et du module v4l2loopback terminée"
        else:
            print("module v4l2loopback présent")
            return "module v4l2loopback présent"
    except (ValueError, OSError, TypeError) as e:
        return str(e)

#vérification de l'appli actuellement ouverte
def verifi_quel_appli():
    try:
        cmd = adb + ["shell", "dumpsys", "window"]
        proc = sps.Popen(
            cmd,
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(timeout=20)
        except sps.TimeoutExpired:
            proc.kill()
            proc.communicate()
            return "adb ne répond pas (délai dépassé)"

        if not stdout:
            return MSG_AUCUN_RESULTAT

        output = ""
        for ligne in stdout.splitlines():
            if "mCurrentFocus" in ligne:
                output = ligne.lower()
                break

        if "whatsapp" in output or "facebook" in output:
            return MSG_APPLI_OK
        else:
            return MSG_APPLI_NON

    except (TypeError, OSError, ValueError) as e:
        return str(e)

def appli_supportee(message):
    """True uniquement si verifi_quel_appli() a détecté WhatsApp ou Facebook."""
    return message == MSG_APPLI_OK

#lancement de scrcpy en arrière plan
def scrcpy_arrpl(a):
    print("Lancement de scrcpy en arrière plan")
    cmd = scrcpy + ["--no-window", "--v4l2-sink=/dev/video"+str(a), "--audio-codec=aac"]
    # Le processus est retourné pour pouvoir l'arrêter ensuite (arreter_processus) :
    # avant, scrcpy restait actif indéfiniment après la capture.
    return sps.Popen(cmd)

def arreter_processus(proc):
    """Arrête proprement un processus lancé avec Popen (sans erreur s'il est déjà fini)."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except sps.TimeoutExpired:
        proc.kill()
        proc.wait()

def lancement_v4l2loopback():
    cmd = ["sudo", "modprobe", "v4l2loopback"]
    # run() et non Popen() : on attend la fin du chargement du module avant de
    # continuer, sinon /dev/video* n'existe pas encore au moment où scrcpy démarre.
    return sps.run(cmd)

def list_ecran_v():
    ecv = g.glob("/dev/video*")
    print(ecv)
    return ecv

def capture_directe(numero="2"):
    """Capture une image du périphérique virtuel /dev/video<numero> avec ffmpeg.

    Retourne True si l'image a bien été enregistrée. Le numéro était auparavant
    figé à 2, quel que soit le périphérique choisi pour scrcpy.
    """
    cmd = ["ffmpeg", "-y", "-i", "/dev/video" + str(numero), "-frames:v", "1",
           horodatage() + "capture.png"]
    print("Capture en cours...")
    proc = sps.run(cmd)
    if proc.returncode == 0:
        print("Capture terminée")
        return True
    print("Échec de la capture (ffmpeg a renvoyé le code", str(proc.returncode) + ")")
    return False

def install_ffmpeg():
    cmd = ["sudo", "apt", "install", "ffmpeg", "-y"]
    sps.run(cmd)

def install_modprobe():
    # Le paquet "modprobe" n'existe pas sous apt : modprobe est fourni par "kmod".
    cmd = ["sudo", "apt", "install", "kmod", "-y"]
    sps.run(cmd)

def appareil_connecte(sortie):
    """Analyse la sortie de "adb devices" : True si un appareil est prêt.

    Le simple test `"device" in sortie` était toujours vrai (l'en-tête
    "List of devices attached" contient "device") et un appareil "offline"
    ou "unauthorized" était pris pour un appareil connecté.
    """
    for ligne in (sortie or "").splitlines():
        mots = ligne.split()
        if ligne.startswith("*") or not mots:
            continue
        if mots[-1] == "device":
            return True
    return False

def analyser_connexion(sortie):
    """Analyse la réponse de "adb connect". Retourne (succès, message)."""
    texte = (sortie or "").strip().lower()
    if not texte:
        return False, "Aucune réponse d'adb."
    if "refused" in texte:
        return False, "Connexion échouée (connexion refusée)."
    if any(mot in texte for mot in ("failed", "cannot", "unable", "timed out")):
        return False, "Connexion échouée : " + texte
    if "connected" in texte:
        return True, "Connecté avec succès."
    return False, "Réponse d'adb : " + texte

def appairer_telephone(ip, port, code):
    """Appaire l'ordinateur au téléphone (adb pair). Retourne (succès, message)."""
    res = sps.run(
        adb + ["pair", str(ip) + ":" + str(port), str(code)],
        capture_output=True, text=True, env=os.environ, timeout=60
    )
    sortie = (res.stdout + res.stderr).strip()
    return ("successfully paired" in sortie.lower()), (sortie or "Aucune réponse d'adb.")


def _option_capture():
    """Option 1 du menu. Retourne True si le programme doit s'arrêter."""
    if "absent" in vb.verfi_ffmpeg():
        print("Installation de ffmpeg")
        install_ffmpeg()
        print("ffmpeg installé, relancez le script")
        return True
    print("ffmpeg détecté")

    if "absent" in vb.verfi_modprobe():
        print("modprobe absent, installation lancée")
        install_modprobe()
        print("Installation terminée, relancez le script")
        return True
    print("modprobe détecté")

    if "module v4l2loopback présent" not in verifi_v4l2loopback():
        print("Installation terminée, relancez le script")
        return True
    print("Module v4l2loopback présent")
    lancement_v4l2loopback()
    list_ecran_v()

    c = input(_("Écrivez le plus grand chiffre que vous voyez: ")).strip()
    if not c.isdigit():
        print("Entrée invalide : un nombre est attendu")
        return False

    flux = scrcpy_arrpl(c)
    try:
        t.sleep(2)  # laisse à scrcpy le temps de démarrer le flux
        etat = verifi_quel_appli()
        print(etat)
        if appli_supportee(etat):
            print("Appli détectée")
            capture_directe(c)
        else:
            print("Appli non supportée")
            try:
                sps.run(adb + ["kill-server"])
            except OSError as e:
                print(e)
            return True
    finally:
        arreter_processus(flux)
    return False


def _option_enregistrement():
    """Option 2 du menu. Retourne True si le programme doit s'arrêter."""
    try:
        resul_appli = verifi_quel_appli()
        print(resul_appli)

        if not appli_supportee(resul_appli):
            if resul_appli == MSG_APPLI_NON:
                print("Appli non supportée, relancez le script lorsque vous serez sur whatsapp ou facebook")
            else:
                print("Impossible de vérifier l'appli, vérifiez la connexion adb puis relancez le script")
            return True

        c = int(input(_("Mettez en seconde le temps d'enregistrement: ")))
        if c <= 0:
            raise ValueError("la durée doit être supérieure à 0")
        vraie_seconde = (c*10)/9
        print("Enregistrement commencé pour", c, "secondes")
        # scrcpy (outil du projet) et non "scrcpy" du PATH, comme partout ailleurs
        cmd = scrcpy + ["-r", horodatage() + "_capture.mp4", "--no-window"]
        proc = sps.Popen(cmd, env=os.environ)
        t.sleep(vraie_seconde)
        proc.terminate()
        proc.wait()
        print("Enregistrement terminé avec succès")
        print("Désactivation du module v4l2loopback...")
        try:
            # sudo nécessaire : modprobe -r échouait sans les droits root
            sps.run(["sudo", "modprobe", "-r", "v4l2loopback"])
        except (OSError, ValueError, TypeError) as e:
            print(e)
    except (TypeError, ValueError) as e:
        print("Entrée invalide: ", e)
        print("Relancez le script")
        return True
    return False


def _option_connexion():
    """Option 3 du menu."""
    try:
        cmd = adb + ["devices"]
        info = sps.run(cmd, capture_output=True, text=True, env=os.environ, timeout=15)
        if appareil_connecte(info.stdout):
            print("Appareil déjà connecté")
            return

        sps.run(adb + ["kill-server"])
        print("Entrez les infos")

        ip = input(_("IP du téléphone local: ")).strip()
        port = input(_("PORT: ")).strip()
        print("connexion en cours...")
        t.sleep(2)
        res = sps.run(adb + ["connect", ip + ":" + port], capture_output=True,
                      env=os.environ, text=True, timeout=30)
        print(analyser_connexion(res.stdout + res.stderr)[1])
    except (ValueError, TypeError, OSError, sps.TimeoutExpired) as e:
        print(e)


def _option_appairage():
    """Option 4 du menu (affichée avant mais jamais implémentée)."""
    print("Sur le téléphone : Options pour les développeurs > Débogage sans fil > "
          "Associer l'appareil avec un code d'association")
    try:
        ip = input(_("IP du téléphone local: ")).strip()
        port = input(_("PORT d'appairage (celui de la fenêtre d'association): ")).strip()
        code = input(_("Code d'appairage à 6 chiffres: ")).strip()
        ok, message = appairer_telephone(ip, port, code)
        print(message)
        if ok:
            print("Appairage réussi, vous pouvez maintenant utiliser l'option 3")
    except (ValueError, TypeError, OSError, sps.TimeoutExpired) as e:
        print(e)


def start():
    while True:
        print("Options Disponibles")
        print("1- Capture d'écran")
        print("2- Enregistrement d'écran")
        print("3- Connecter le téléphone (Assurez vous que votre appareil ait déjà été connecté au moins une fois, voir 4)")
        print("4- Appairage de l'ordinateur au téléphone")
        print("5- Quitter")
        print("6- Langue")

        choix = input(_("Quel choix prendre: "))

        if choix == "1":
            if _option_capture():
                break

        elif choix == "2":
            if _option_enregistrement():
                break

        elif choix == "3":
            _option_connexion()

        elif choix == "4":
            _option_appairage()

        elif choix == "5":
            break

        elif choix == "6":
            choisir_langue_terminal()

        else:
            print("Entrée invalide")


if __name__ == "__main__":
    from noyau import i18n
    i18n.initialiser()
    i18n.installer_flux_traduits()
    start()
