import subprocess as sps
from vrbls import adb, scrcpy
import time as t
import ver_bin as vb
import glob as g
import datetime as dt
import os

heure = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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
        print("Commande lancée: sudo apt install v4l2loopback-dkms v4l2loopback-utils", "-y")
        cmd = ["sudo", "apt", "install", "v4l2loopback-dkms", "v4l2loopback-utils"]

        proc = sps.run(
            cmd,
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )

        print(proc)
    except (TypeError, OSError, ValueError) as e:
        print(e)

def verifi_v4l2loopback():
    try:
        print("Vérification de la présence de v42loopback par activation")
        cmd = ["modprobe", "v4l2loopback"]

        proc = sps.Popen(
            cmd,
            stdout=sps.PIPE,
            stderr=sps.PIPE,
            text=True
        )

        stdout, stderr = proc.communicate()

        output = ""
        for ligne in stdout.splitlines():
                    if "mCurrentFocus" in ligne:
                        output = ligne.lower()
                        break

        if "Erreur" in output or "Error" in output or "error" in output:
            print("Erreur, installation des headers génériques pour linux...")
            install_linux_headers_generic()
            print("Insatallation du module v4l2loopback")
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
        
        stdout, stderr = proc.communicate()

        if not stdout:
            return "Aucun résultat détecté"
            
        output = ""
        for ligne in stdout.splitlines():
            if "mCurrentFocus" in ligne:
                output = ligne.lower()
                break

        if "whatsapp" in output or "facebook" in output:
            return "Appli supportée à l'écran"
        else:
            return "Appli non supportée"
            
    except (TypeError, OSError, ValueError) as e:
        return str(e)

#lancement de scrcpy en arrière plan
def scrcpy_arrpl(a):
    print("Lancement de scrcpy en arrière plan")
    cmd = scrcpy + ["--no-window", "--v4l2-sink=/dev/video"+a, "--audio-codec=aac"] 
    sps.Popen(cmd)

def lancement_v4l2loopback():
    cmd = ["sudo", "modprobe", "v4l2loopback"]
    sps.Popen(cmd)

def list_ecran_v():
    ecv = g.glob("/dev/video*")
    print(ecv)
    return ecv

def capture_directe():
    cmd = ["ffmpeg", "-i", "/dev/video2", "-frames:v", "1", heure+"capture.png", "-y"]
    print("Capture en cours...")
    sps.run(cmd)
    print("Capture terminée")

def install_ffmpeg():
    cmd = ["sudo", "apt", "install", "ffmpeg", "-y"]
    sps.run(cmd)

def install_modprobe():
    cmd = ["sudo", "apt", "install", "modprobe", "-y"]
    sps.run(cmd)    

def start():
    while True:
        print("Options Disponibles")
        print("1- Capture d'écran")
        print("2- Enregistrement d'écran")
        print("3- Connecter le téléphone (Assurez vous que vous appareil était connecté déjà au moins une fois, voir 4)")
        print("4- Appairage de l'ordinateur au téléphone")
        print("5- Quitter")

        choix = input("Quelle choix prendre: ")

        if choix == "1":
            if "présent" in vb.verfi_ffmpeg():
                print("ffmpeg détecté")

                if "présent" in vb.verfi_modprobe():
                    print("modprobe détecté")

                    if "module v4l2loopback présent" in verifi_v4l2loopback():
                        print("Module v4l2loopback présent")
                        lancement_v4l2loopback()
                        list_ecran_v()

                        try:
                            c = input("Ecrivez le plus grand chiffre que vous voyez")
                            scrcpy_arrpl(c)
                        except (TypeError, ValueError) as e:
                            print(e)
                            break

                        if "supportée" in verifi_quel_appli():
                            print("Appli détectée")
                            capture_directe()
                        elif "non" in verifi_quel_appli():
                            print("Appli non supportée")
                            try:
                                sps.run(adb + ["kill-server"])
                                break
                            except (Exception, FileExistsError) as e:
                                print(e)    

                elif "absent" in vb.verfi_modprobe():
                    print("modprobe absent, installation lancée")
                    install_modprobe()
                    print("Installation terminée, relancez le script")
                    break

            elif "absent" in vb.verfi_ffmpeg():
                print("Installation de ffmpeg")
                install_ffmpeg()
                print("ffmpeg installé, relancez le script")
                break

        elif choix == "2":
            try:

                resul_appli = verifi_quel_appli()
                print(resul_appli)

                if "non" in resul_appli:
                    print("Appli non supportée, relancez le script lorsque vous serez sur whatsapp ou facebook")
                    break

                elif "écran" in resul_appli:
                    c = int(input("Mettez en seconde le temps d'enregistrement: "))
                    vraie_seconde = (c*10)/9
                    print("Enregistrement commencée pour", c, "secondes")
                    cmd = ["scrcpy", "-r", heure + "_capture.mp4", "--no-window"]
                    proc = sps.Popen(cmd, env= os.environ)
                    t.sleep(vraie_seconde)
                    proc.terminate()
                    proc.wait()
                    print("Enregistrement terminée avec succès")
                    print("Désactivaion du module v4l2loopback...")
                    try:
                        sps.run(["modprobe", "-r", "v4l2loopback"])
                    except (KeyError, ValueError, TypeError, Exception) as e:
                        print(e)

                else:
                    print("Erreur inconnue, relancez le script")
                    break
                
            except (TypeError, ValueError) as e:
                print("Entrée invalide: ", e)
                print("Relancez le script")
                break

        elif choix == "3":
            try:
                cmd = adb + ["devices"]
                info = sps.run(cmd, capture_output=True, text=True, env=os.environ)
                if "device" in info.stdout and len(info.stdout.strip().splitlines()) > 1:
                    print("Appareil déjà connecté")

                else:
                    c1 = adb + ["kill-server"]
                    sps.run(c1)
                    print("Entrez les infos")

                    ip = input("IP du téléphone local: ")
                    port = input("PORT: ")
                    c2 = adb + ["connect", ip + ":" + port]
                    print("connexion en cours...")
                    t.sleep(2)
                    res = sps.run(c2, capture_output=True, env=os.environ, text=True)
                    if "connected" in res.stdout.lower():
                        print("Connecté avec succès")
                    elif "refused" in res.stdout.strip():
                        print("Connexion échouée")
                    else:
                        print(res.stdout.lower())
            except (ValueError, TypeError) as e:
                print(e)

        #elif choix == "4":
            

        elif choix == "5":
            break
        
        else:
            print("Entrée invalide")

start()
