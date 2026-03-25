#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import shutil
import subprocess
import tarfile
import time
import platform
from datetime import datetime

dossier_sauvegarde = "backups"
dossier_rapports = "rapports"
BYTES_PER_MEGABYTE = 1024 * 1024
espace_min = 50


def chemin_racine():
    """Retourne le chemin absolu du répertoire du script."""
    return os.path.dirname(os.path.abspath(__file__))


def chemin_sauvegarde():
    """Retourne le chemin absolu du dossier de sauvegarde."""
    return os.path.join(chemin_racine(), dossier_sauvegarde)


def chemin_rapports():
    """Retourne le chemin absolu du dossier des rapports."""
    return os.path.join(chemin_racine(), dossier_rapports)


def creer_archive(date_creation):
    """Génère le nom de l'archive au format backup_YYYY-MM-DD.tar.gz."""
    date_slug = date_creation.strftime("%Y-%m-%d")
    return f"backup_{date_slug}.tar.gz"


def verifier_espace(destination):
    """Vérifie l'espace disque disponible via subprocess avant d'archiver."""
    if platform.system() == "Windows":
        cmd = ["powershell", "-Command", f"(Get-PSDrive -Name '{destination[0]}').Free / 1MB"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        espace_dispo = int(float(result.stdout.strip().replace(',', '.')))
    else:
        result = subprocess.run(
            ["df", "-m", destination],
            capture_output=True,
            text=True,
            check=True
        )
        output_lines = result.stdout.strip().splitlines()
        df_fields = output_lines[-1].split()
        espace_dispo = int(df_fields[3])

    if espace_dispo < espace_min:
        raise RuntimeError(
            f"Espace insuffisant : {espace_dispo} mo dispo "
            f"(minimum requis : {espace_min} mo)."
        )


def compresse_archiv(chemin_logs, chemin_archives):
    """Archive les fichiers .log traités dans une archive compressée."""
    with tarfile.open(chemin_archives, "w:gz") as archive:
        for chemin_des_log in chemin_logs:
            if os.path.exists(chemin_des_log):
                archive.add(str(chemin_des_log), arcname=str(os.path.basename(chemin_des_log)))


def deplacer_archive(chemin_archiv, destination):
    """Déplace l'archive vers le dossier de destination via shutil."""
    os.makedirs(destination, exist_ok=True)
    dest_finale = os.path.join(destination, os.path.basename(chemin_archiv))
    if os.path.exists(dest_finale):
        os.remove(dest_finale)
    return shutil.move(chemin_archiv, destination)


def age_fichier(chemin_fichier):
    """Calcule l'âge d'un fichier en jours via os.path.getmtime()."""
    derniere_modif = os.path.getmtime(chemin_fichier)
    en_second = time.time() - derniere_modif
    return en_second / 86400


def supp_ancien_rapport(jours_fichier):
    """Supprime les rapports JSON plus vieux que N jours."""
    dossiers_rapports = chemin_rapports()
    model_rapport = os.path.join(dossiers_rapports, "rapport_*.json")
    tout_rapports = glob.glob(model_rapport)
    supp_rapport = []

    for chemin_rapport in tout_rapports:
        if age_fichier(chemin_rapport) > jours_fichier:
            os.remove(chemin_rapport)
            supp_rapport.append(os.path.basename(chemin_rapport))

    return supp_rapport


def archiver_et_nettoyer(chemin_logs, destination, jours_fichier):
    """Orchestre l'appel des étapes d'archivage et de nettoyage."""
    verifier_espace(destination if os.path.isdir(destination) else chemin_racine())

    date_creation = datetime.now()
    nom_archive = creer_archive(date_creation)
    temp = os.path.join(chemin_racine(), nom_archive)

    compresse_archiv(chemin_logs, temp)
    chemin_archiv = deplacer_archive(temp, destination)
    supp_rapport = supp_ancien_rapport(jours_fichier)

    return {
        "archive": chemin_archiv,
        "rapports_supprimes": supp_rapport,
    }