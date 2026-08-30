# -*- coding: utf-8 -*-
"""
fenetre.py — Interface graphique PyQt6 de CEVI.

Principe :
    - la liste des actions est remplie automatiquement depuis le registre
      (noyau/registre.py) : toute action ajoutée dans actions/ apparaît ici
      sans modifier ce fichier ;
    - le formulaire de paramètres est généré automatiquement à partir des
      Parametre déclarés par l'action (str -> champ texte, int -> compteur,
      float -> compteur décimal, bool -> case à cocher, choix -> liste) ;
    - chaque action s'exécute dans un thread d'arrière-plan (daemon) pour
      ne jamais figer la fenêtre, même pendant les commandes longues ;
    - tous les print() de l'action sont redirigés vers la console de la
      fenêtre (et affichés aussi dans le terminal s'il est ouvert).

Lancement : python main.py -mg   (PyQt6 doit être installé)
"""

import functools
import os
import sys
import threading
import traceback

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from noyau import registre
from noyau import sudo

STYLESHEET = """
QMainWindow, QWidget { background: #f4f6f8; color: #1f2933; font-size: 13px; }
QLabel#Titre { font-size: 18px; font-weight: 600; color: #0f766e; }
QListWidget {
    background: #ffffff; border: 1px solid #d5dbe1; border-radius: 6px; padding: 4px;
}
QListWidget::item { padding: 8px; border-radius: 4px; }
QListWidget::item:selected { background: #0f766e; color: #ffffff; }
QListWidget::item:hover { background: #e6f2f0; }
QGroupBox {
    background: #ffffff; border: 1px solid #d5dbe1; border-radius: 6px;
    margin-top: 12px; padding: 10px; font-weight: 600;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #0f766e; }
QPushButton {
    background: #0f766e; color: #ffffff; border: none; border-radius: 6px;
    padding: 8px 16px; font-weight: 600;
}
QPushButton:hover { background: #0d5f59; }
QPushButton:disabled { background: #9fc9c5; }
QPushButton#Secondaire { background: #e5e9ee; color: #1f2933; }
QPushButton#Secondaire:hover { background: #d5dbe1; }
QPlainTextEdit {
    background: #1f2933; color: #e5e9ee; border: none; border-radius: 6px;
    font-size: 12px;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #ffffff; border: 1px solid #d5dbe1; border-radius: 4px; padding: 5px;
}
QSplitter::handle { background: #d5dbe1; width: 2px; }
"""


class RedirectionSortie(QObject):
    """Redirige sys.stdout / sys.stderr vers la console de la fenêtre.

    La méthode write() peut être appelée depuis n'importe quel thread
    (les actions tournent en arrière-plan) : le signal Qt la réémet
    toujours dans le thread de l'interface, sans danger.

    Règle d'or : write() ne doit JAMAIS lever d'exception — sinon les
    tracebacks eux-mêmes disparaissent et les erreurs deviennent
    indéchiffrables. Tout y est donc protégé.
    """

    texte_emis = pyqtSignal(str)

    def write(self, texte):
        if not texte:
            return
        texte = str(texte)
        try:
            self.texte_emis.emit(texte)
        except Exception:
            pass  # fenêtre fermée ou erreur de slot : ne jamais propager
        try:
            sys.__stdout__.write(texte)  # écho dans le vrai terminal
            sys.__stdout__.flush()       # flush : visible même en cas d'arrêt brutal
        except Exception:
            pass

    def flush(self):
        try:
            sys.__stdout__.flush()
        except Exception:
            pass


def slot_protege(dialogue=True):
    """Décorateur de protection des slots Qt.

    Sans lui, une exception dans un slot remonte à PyQt6 qui, avec son
    excepthook par défaut, affiche seulement « Unhandled Python exception »
    puis arrête brutalement le programme (abort / IOT / core dumped).

    Avec lui, l'erreur est interceptée AVANT PyQt6 : elle est écrite en
    clair (traceback complet) dans le vrai terminal et, sauf si la variable
    d'environnement CEVI_SANS_DIALOGUES=1 est définie, une boîte de dialogue
    l'affiche également. L'application reste utilisable.
    """
    def decorateur(fonction):
        @functools.wraps(fonction)
        def wrapper(self, *args, **kwargs):
            try:
                return fonction(self, *args, **kwargs)
            except SystemExit:
                raise
            except BaseException:
                try:
                    self._signaler_erreur(fonction.__name__, dialogue)
                except Exception:
                    pass
        return wrapper
    return decorateur


class OuvrierAction(threading.Thread):
    """Exécute une action en arrière-plan pour ne pas figer la fenêtre.

    Thread démon : si l'utilisateur ferme malgré tout l'application pendant
    une action, le programme se termine proprement (aucun crash Qt).
    """

    def __init__(self, action, kwargs, sur_finie):
        super().__init__(daemon=True, name=f"CEVI-{action.identifiant}")
        self.action = action
        self.kwargs = kwargs
        self.sur_finie = sur_finie

    def run(self):
        try:
            resultat = self.action.fonction(**self.kwargs)
        except Exception as e:  # filet de sécurité : l'interface ne doit jamais planter
            resultat = f"Erreur pendant l'exécution : {e}"
        finally:
            sudo.oublier()  # le mot de passe sudo ne survit jamais à l'action
        if resultat is None:
            resultat = "Action terminée."
        try:
            self.sur_finie(resultat)
        except Exception:
            pass  # fenêtre déjà fermée


class Fenetre(QMainWindow):
    """Fenêtre principale : liste des actions, formulaire, console."""

    signal_finie = pyqtSignal(object)  # résultat de l'action (émis depuis le thread)
    signal_mdp = pyqtSignal(str, str, object)  # demande de mot de passe sudo

    def __init__(self, redirection):
        super().__init__()
        self.setWindowTitle("CEVI — Panneau d'actions")
        self.resize(980, 640)
        self.occupe = False
        self.action_courante = None
        self.actions_liste = []
        self.champs = {}

        self.signal_finie.connect(self.sur_action_finie)
        self.signal_mdp.connect(self._afficher_demande_mdp)
        redirection.texte_emis.connect(self.ajouter_console)

        self.setStyleSheet(STYLESHEET)
        self._construire_ui()
        self._remplir_liste()
        self.ajouter_console("Console CEVI — les messages des actions s'affichent ici.\n")

    def _signaler_erreur(self, contexte, dialogue=True):
        """Signale une erreur interne sans jamais faire planter l'application.

        - écrit le traceback complet dans le VRAI terminal (sys.__stderr__) ;
        - affiche une boîte de dialogue avec le détail, sauf si la variable
          d'environnement CEVI_SANS_DIALOGUES=1 est définie (mode tests).
        """
        texte = traceback.format_exc()
        try:
            sys.__stderr__.write(
                f"=== ERREUR INTERNE CEVI ({contexte}) ===\n{texte}=== FIN ===\n"
            )
            sys.__stderr__.flush()
        except Exception:
            pass
        if dialogue and os.environ.get("CEVI_SANS_DIALOGUES") != "1":
            try:
                boite = QMessageBox(self)
                boite.setIcon(QMessageBox.Icon.Critical)
                boite.setWindowTitle("Erreur interne — CEVI")
                boite.setText(f"Une erreur est survenue ({contexte}).")
                boite.setDetailedText(texte)
                boite.exec()
            except Exception:
                pass

    # ------------------------------------------------- mot de passe sudo

    def demander_mot_de_passe(self, titre, message):
        """Demande un mot de passe à l'utilisateur — SÛR pour les threads.

        Appelée depuis le thread d'une action (noyau/sudo.py) : la boîte
        de dialogue s'ouvre dans le thread de l'interface via un signal,
        et le thread d'arrière-plan attend la réponse (Event). Retourne
        le mot de passe saisi, ou None si annulé / délai dépassé.
        """
        resultat = {"mot": None, "pret": threading.Event()}
        self.signal_mdp.emit(titre, message, resultat)
        resultat["pret"].wait(timeout=sudo._DELAI_DIALOGUE)
        return resultat["mot"]

    @slot_protege(dialogue=False)
    def _afficher_demande_mdp(self, titre, message, resultat):
        """Ouvre le dialogue de mot de passe (thread de l'interface)."""
        try:
            mot, ok = QInputDialog.getText(
                self, titre, message, QLineEdit.EchoMode.Password,
            )
            resultat["mot"] = mot if ok and mot else None
        finally:
            # l'événement est TOUJOURS levé : jamais d'attente infinie
            resultat["pret"].set()

    # ------------------------------------------------------------------ UI

    def _construire_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        racine = QVBoxLayout(central)
        racine.setContentsMargins(14, 12, 14, 12)
        racine.setSpacing(10)

        titre = QLabel("CEVI — Panneau d'actions")
        titre.setObjectName("Titre")
        racine.addWidget(titre)

        separateur = QSplitter(Qt.Orientation.Horizontal)
        racine.addWidget(separateur, 1)

        # Colonne gauche : liste des actions + description
        gauche = QWidget()
        gl = QVBoxLayout(gauche)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.addWidget(QLabel("Actions disponibles"))
        self.liste = QListWidget()
        gl.addWidget(self.liste, 1)
        self.libelle_description = QLabel("")
        self.libelle_description.setWordWrap(True)
        gl.addWidget(self.libelle_description)
        separateur.addWidget(gauche)

        # Colonne droite : paramètres, boutons, console
        droite = QWidget()
        dl = QVBoxLayout(droite)
        dl.setContentsMargins(0, 0, 0, 0)

        groupe_params = QGroupBox("Paramètres")
        gp = QVBoxLayout(groupe_params)
        zone = QScrollArea()
        zone.setWidgetResizable(True)
        zone.setFrameShape(QScrollArea.Shape.NoFrame)
        self.conteneur_params = QWidget()
        self.formulaire = QFormLayout(self.conteneur_params)
        self.formulaire.setSpacing(8)
        zone.setWidget(self.conteneur_params)
        gp.addWidget(zone)
        dl.addWidget(groupe_params)

        # La console est créée AVANT les boutons : le bouton "Effacer"
        # se connecte à self.console.clear (l'ordre visuel reste le même,
        # seul l'ordre de création change).
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(5000)
        try:
            police = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        except Exception:
            police = QFont()  # police par défaut si l'API change selon la version
            police.setFamily("monospace")
        self.console.setFont(police)

        boutons = QHBoxLayout()
        self.bouton_executer = QPushButton("Exécuter l'action")
        # NB : le signal clicked de Qt émet un booléen (checked). On passe par
        # une lambda SANS argument pour que ce booléen ne soit jamais transmis
        # à la méthode (PyQt6 compte les paramètres du slot pour tronquer).
        self.bouton_executer.clicked.connect(
            lambda *args: self.executer_action_courante()
        )
        boutons.addWidget(self.bouton_executer)
        boutons.addStretch(1)
        bouton_effacer = QPushButton("Effacer la console")
        bouton_effacer.setObjectName("Secondaire")
        bouton_effacer.clicked.connect(self.console.clear)
        boutons.addWidget(bouton_effacer)
        dl.addLayout(boutons)

        groupe_console = QGroupBox("Console")
        gc = QVBoxLayout(groupe_console)
        gc.addWidget(self.console)
        dl.addWidget(groupe_console, 1)

        separateur.addWidget(droite)
        separateur.setSizes([340, 640])

    @slot_protege()
    def _remplir_liste(self):
        self.actions_liste = registre.actions_triees()
        for action in self.actions_liste:
            item = QListWidgetItem(action.nom)
            item.setToolTip(action.identifiant)
            self.liste.addItem(item)
        if not self.actions_liste:
            self.liste.addItem("Aucune action enregistrée")
            self.bouton_executer.setEnabled(False)
            return
        self.liste.currentRowChanged.connect(self._afficher_action)
        self.liste.setCurrentRow(0)
        self._afficher_action(0)  # appel direct : garantit l'affichage initial

    @slot_protege()
    def _afficher_action(self, row):
        self._vider_formulaire()
        if row < 0 or row >= len(self.actions_liste):
            self.action_courante = None
            self.libelle_description.setText("")
            return
        action = self.actions_liste[row]
        self.action_courante = action
        self.libelle_description.setText(action.description)
        for p in action.parametres:
            widget = self._creer_champ(p)
            self.formulaire.addRow(p.label or p.nom, widget)
        if not action.parametres:
            self.formulaire.addRow(QLabel("Cette action n'a besoin d'aucun paramètre."))

    def _vider_formulaire(self):
        # NB : on utilise count() (fiable même sur un QFormLayout vide) plutôt
        # que rowCount(), et on garde un garde-fou si takeAt renvoie None.
        while self.formulaire.count():
            item = self.formulaire.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self.champs = {}

    def _creer_champ(self, p):
        """Crée le widget adapté au type du paramètre (formulaire automatique)."""
        if p.type == "int":
            widget = QSpinBox()
            mini = int(p.mini) if p.mini is not None else -2147483647
            maxi = int(p.maxi) if p.maxi is not None else 2147483647
            widget.setRange(mini, maxi)
            try:
                widget.setValue(int(p.defaut))
            except (TypeError, ValueError):
                widget.setValue(0)
        elif p.type == "float":
            widget = QDoubleSpinBox()
            mini = float(p.mini) if p.mini is not None else -1e9
            maxi = float(p.maxi) if p.maxi is not None else 1e9
            widget.setRange(mini, maxi)
            widget.setDecimals(2)
            try:
                widget.setValue(float(p.defaut))
            except (TypeError, ValueError):
                widget.setValue(0.0)
        elif p.type == "bool":
            widget = QCheckBox()
            widget.setChecked(bool(p.defaut))
        elif p.type == "choix":  # noqa: SIM114 — branches volontairement explicites
            widget = QComboBox()
            widget.addItems([str(c) for c in p.choix])
            if str(p.defaut) in [str(c) for c in p.choix]:
                widget.setCurrentText(str(p.defaut))
        else:  # "str" par défaut
            widget = QLineEdit()
            if p.defaut not in ("", None):
                widget.setText(str(p.defaut))
        if p.aide:
            widget.setToolTip(p.aide)
        self.champs[p.nom] = (p, widget)
        return widget

    def _lire_champ(self, p, widget):
        if p.type == "int":
            return widget.value()
        if p.type == "float":
            return widget.value()
        if p.type == "bool":
            return widget.isChecked()
        if p.type == "choix":
            return widget.currentText()
        return widget.text().strip()

    # ------------------------------------------------------------- actions

    @slot_protege()
    def executer_action_courante(self, checked=False):
        # `checked` : argument optionnel que le signal clicked de Qt peut
        # transmettre. En l'accepter, la méthode tolère toutes les façons
        # d'être appelée (bouton, signal, appel direct) sans TypeError.
        if self.occupe:
            QMessageBox.information(self, "CEVI", "Une action est déjà en cours d'exécution.")
            return
        if self.action_courante is None:
            QMessageBox.warning(self, "CEVI", "Aucune action sélectionnée.")
            return

        action = self.action_courante
        valeurs = {}
        # self.champs = {nom: (parametre, widget)} -> on déballe le tuple.
        # (l'ancienne boucle `for p, widget in ...items()` affectait le NOM
        #  du champ dans p, d'où AttributeError dès qu'une action avait
        #  au moins un paramètre)
        for _nom, (p, widget) in self.champs.items():
            valeurs[p.nom] = self._lire_champ(p, widget)

        try:
            kwargs = registre.preparer_parametres(action, valeurs)
        except ValueError as e:
            QMessageBox.warning(self, "Paramètre invalide", str(e))
            return

        self.occupe = True
        self.bouton_executer.setEnabled(False)
        self.bouton_executer.setText("Exécution en cours...")
        self.ajouter_console(f"\n>>> Exécution de « {action.nom} »...\n")
        self.ouvrier = OuvrierAction(action, kwargs, self.signal_finie.emit)
        self.ouvrier.start()

    @slot_protege()
    def sur_action_finie(self, resultat):
        self.ajouter_console(f"\n[Résultat] {resultat}\n")
        self.occupe = False
        self.bouton_executer.setEnabled(True)
        self.bouton_executer.setText("Exécuter l'action")

    @slot_protege(dialogue=False)
    def ajouter_console(self, texte):
        self.console.insertPlainText(str(texte))
        barre = self.console.verticalScrollBar()
        barre.setValue(barre.maximum())

    @slot_protege()
    def closeEvent(self, evenement):
        if self.occupe:
            reponse = QMessageBox.question(
                self, "Action en cours",
                "Une action est en cours d'exécution.\nVoulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reponse != QMessageBox.StandardButton.Yes:
                evenement.ignore()
                return
        evenement.accept()


def lancer():
    """Point d'entrée du mode graphique (appelé par main.py avec l'option -mg)."""
    import actions  # noqa: F401 — déclenche l'enregistrement de toutes les actions

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("CEVI")

    # --- Filet de sécurité n°1 : excepthook personnalisé -------------------
    # Sans lui, une exception qui échappe dans un slot est traitée par
    # l'excepthook PAR DÉFAUT de PyQt6 : message « Unhandled Python
    # exception » puis abort() brutal (IOT / core dumped), sans aucun
    # traceback. Avec lui, l'erreur est écrite en clair dans le vrai
    # terminal et l'application continue de fonctionner.
    def _excepthook(etype, valeur, tb):
        try:
            traceback.print_exception(etype, valeur, tb, file=sys.__stderr__)
            sys.__stderr__.flush()
        except Exception:
            pass

    sys.excepthook = _excepthook

    redirection = RedirectionSortie()

    # --- Filet de sécurité n°2 : fenêtre construite AVANT redirection ------
    # Si la construction de la fenêtre échoue (police manquante, version de
    # PyQt6 différente, etc.), l'erreur remonte en traceback Python normal
    # dans le terminal (exit 1 propre) au lieu d'un crash Qt silencieux.
    try:
        fenetre = Fenetre(redirection)
    except SystemExit:
        raise
    except BaseException:
        sys.excepthook(*sys.exc_info())
        try:
            QMessageBox.critical(
                None, "CEVI",
                "Erreur au démarrage de l'interface.\n"
                "Le détail complet est écrit dans le terminal.",
            )
        except Exception:
            pass
        sys.exit(1)

    # --- Redirection des print() vers la console de la fenêtre -------------
    # (uniquement maintenant : la fenêtre et sa console existent déjà)
    sortie_originale, erreur_originale = sys.stdout, sys.stderr
    sys.stdout = redirection
    sys.stderr = redirection

    # Les actions peuvent demander le mot de passe sudo : noyau/sudo.py
    # utilisera la méthode de la fenêtre (sûre pour les threads : le
    # dialogue s'ouvre dans le thread de l'interface via un signal).
    sudo.fixuer_demandeur(fenetre.demander_mot_de_passe)

    fenetre.show()
    code = app.exec()

    # nettoyage : plus de mot de passe en mémoire, plus de demandeur
    sudo.oublier()
    sudo.fixuer_demandeur(None)

    sys.stdout, sys.stderr = sortie_originale, erreur_originale
    sys.exit(code)
