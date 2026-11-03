# Logiciels tiers / Third-party software

CEVI (GPL-3.0, voir [LICENSE](LICENSE)) s'appuie sur d'autres logiciels. Ils ne sont pas
couverts par la licence de CEVI : chacun garde la sienne.
*CEVI relies on other software. They are not covered by CEVI's license: each keeps its own.*

| Logiciel / Software | Rôle / Role | Licence / License | Fourni dans le dépôt / Shipped |
| --- | --- | --- | --- |
| [scrcpy](https://github.com/Genymobile/scrcpy) (`scrcpy`, `scrcpy-server`) | Affichage et enregistrement de l'écran / screen mirroring and recording | Apache-2.0 | oui, dans `outils.zip` / yes, in `outils.zip` |
| [adb](https://developer.android.com/tools/releases/platform-tools) (Android platform-tools) | Communication avec le téléphone / phone communication | Apache-2.0 | oui, dans `outils.zip` / yes, in `outils.zip` |
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | Interface graphique / GUI | GPL-3.0 ou licence commerciale / or commercial | non, `pip install PyQt6` / no |
| [FFmpeg](https://ffmpeg.org/) | Capture d'une image / frame capture | LGPL-2.1+ ou/or GPL-2.0+ selon la compilation / depending on the build | non, installé via apt / no, installed via apt |
| [v4l2loopback](https://github.com/umlaeute/v4l2loopback) | Caméra virtuelle / virtual camera | GPL-2.0+ | non, installé via apt / no, installed via apt |

Les binaires de `outils.zip` sont redistribués tels quels avec leurs licences d'origine
(Apache-2.0, compatible avec la GPL-3.0). Le texte de la licence Apache-2.0 est disponible sur
<https://www.apache.org/licenses/LICENSE-2.0>. Vérifiez l'origine et la version des binaires
avant toute redistribution.

*The binaries in `outils.zip` are redistributed unmodified under their original licenses
(Apache-2.0, compatible with GPL-3.0). Check the origin and version of the binaries before
redistributing them.*
