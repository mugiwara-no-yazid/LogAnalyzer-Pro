
import json
import os
import platform
import sys
from datetime import datetime


def generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites):

    try:
        maintenant = datetime.now()
        date_fichier = maintenant.strftime("%Y-%m-%d")
        date_rapport = maintenant.strftime("%Y-%m-%d %H:%M:%S")

        utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "Inconnu"
        systeme_os = platform.system()

        donnees_rapport = {
            "metadata": {
                "date": date_rapport,
                "utilisateur": utilisateur,
                "os": systeme_os,
                "source": source
            },
            "statistiques": {
                "total_lignes": total_lignes,
                "par_niveau": par_niveau,
                "top5_erreurs": top5_erreurs
            },
            "fichiers_traites": fichiers_traites
        }

        chemin_fichier_actuel = os.path.abspath(__file__)
        dossier_actuel = os.path.dirname(chemin_fichier_actuel)
        dossier_rapports = os.path.join(dossier_actuel, "rapports")

        if not os.path.exists(dossier_rapports):
            os.makedirs(dossier_rapports)

        nom_fichier = f"rapport_{date_fichier}.json"
        chemin_complet_fichier = os.path.join(dossier_rapports, nom_fichier)

        with open(chemin_complet_fichier, "w", encoding="utf-8") as fichier:
            json.dump(donnees_rapport, fichier, indent=4)

        print(f"Rapport sauvegardé avec succès : {chemin_complet_fichier}")
        return chemin_complet_fichier

    except Exception as erreur:
        print(f"Une erreur s'est produite lors de la génération du rapport : {erreur}")
        sys.exit(1)
