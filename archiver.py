#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import os
import shutil
import subprocess
import tarfile
import time
from datetime import datetime


dossier_sauvegarde = "backups"
dossier_rapports = "rapports"
BYTES_PER_MEGABYTE = 1024 * 1024
espace_min = 50


def chemin_racine():
    """
    Retourne le chemin absolu du répertoire contenant le script courant.

    :return: Chemin absolu du répertoire racine du projet.
    :rtype: str
    """
    return os.path.dirname(os.path.abspath(__file__))


def chemin_sauvegarde():
    """
    Retourne le chemin absolu du dossier de sauvegarde.

    Construit le chemin en combinant la racine du projet
    et le nom du dossier défini par la variable ``dossier_sauvegarde``.

    :return: Chemin absolu vers le dossier de sauvegarde.
    :rtype: str
    """
    return os.path.join(chemin_racine(), dossier_sauvegarde)


def chemin_rapports():
    """
    Retourne le chemin absolu du dossier des rapports.

    Construit le chemin en combinant la racine du projet
    et le nom du dossier défini par la variable ``dossier_rapports``.

    :return: Chemin absolu vers le dossier des rapports.
    :rtype: str
    """
    return os.path.join(chemin_racine(), dossier_rapports)


def creer_archive(date_creation):
    """
    Génère le nom du fichier archive au format ``backup_YYYY-MM-DD.tar.gz``.

    :param date_creation: Date à utiliser pour nommer l'archive.
    :type date_creation: datetime
    :return: Nom du fichier archive (ex: ``"backup_2024-06-15.tar.gz"``).
    :rtype: str

    :exemple:
        >>> from datetime import datetime
        >>> creer_archive(datetime(2024, 6, 15))
        'backup_2024-06-15.tar.gz'
    """
    date_slug = date_creation.strftime("%Y-%m-%d")
    return f"backup_{date_slug}.tar.gz"


def verifier_espace(destination):
    """
    Vérifie que l'espace disque disponible est suffisant avant une sauvegarde.

    Calcule l'espace libre sur le disque associé à ``destination``
    (ou à la racine du projet si ``destination`` n'est pas un répertoire valide)
    et lève une exception si celui-ci est inférieur au seuil ``espace_min``.

    :param destination: Chemin du répertoire de destination à vérifier.
    :type destination: str

    :raises RuntimeError: Si l'espace disque disponible est inférieur
                          à ``espace_min`` mégaoctets.

    :exemple:
        >>> verifier_espace("/var/backups")  # Lève RuntimeError si < 50 Mo disponibles
    """
    total, used, free = shutil.disk_usage(destination if os.path.isdir(destination) else chemin_racine())
    espace_dispo = free // BYTES_PER_MEGABYTE

    if espace_dispo < espace_min:
        raise RuntimeError(
            f"Espace insuffisant : {espace_dispo} mo dispo "
            f"(minimum requis : {espace_min} mo)."
        )


def compresse_archiv(chemin_logs, chemin_archives):
    """
    Compresse une liste de fichiers journaux dans une archive ``.tar.gz``.

    Chaque fichier est ajouté à l'archive en conservant uniquement
    son nom de base (sans le chemin complet).

    :param chemin_logs: Liste des chemins absolus ou relatifs des fichiers ``.log`` à archiver.
    :type chemin_logs: list[str]
    :param chemin_archives: Chemin complet de destination de l'archive générée.
    :type chemin_archives: str

    :exemple:
        >>> compresse_archiv(["/logs/app.log", "/logs/error.log"], "/tmp/backup.tar.gz")
    """
    with tarfile.open(chemin_archives, "w:gz") as archive:
        for chemin_des_log in chemin_logs:
            archive.add(chemin_des_log, arcname=os.path.basename(chemin_des_log))


def deplacer_archive(chemin_archiv, destination):
    """
    Déplace une archive vers un dossier de destination.

    Crée le dossier de destination s'il n'existe pas. Si une archive
    portant le même nom existe déjà à destination, elle est supprimée
    avant le déplacement.

    :param chemin_archiv: Chemin complet de l'archive à déplacer.
    :type chemin_archiv: str
    :param destination: Chemin du dossier de destination.
    :type destination: str
    :return: Chemin final de l'archive après déplacement.
    :rtype: str

    :exemple:
        >>> deplacer_archive("/tmp/backup_2024-06-15.tar.gz", "/var/backups")
        '/var/backups/backup_2024-06-15.tar.gz'
    """
    os.makedirs(destination, exist_ok=True)
    dest_finale = os.path.join(destination, os.path.basename(chemin_archiv))

    if os.path.exists(dest_finale):
        os.remove(dest_finale)
    return shutil.move(chemin_archiv, destination)


def age_fichier(chemin_fichier):
    """
    Calcule l'âge d'un fichier en jours depuis sa dernière modification.

    :param chemin_fichier: Chemin vers le fichier dont on veut connaître l'âge.
    :type chemin_fichier: str
    :return: Nombre de jours écoulés depuis la dernière modification du fichier.
    :rtype: float

    :exemple:
        >>> age_fichier("/var/log/app.log")
        3.741...
    """
    derniere_modif = os.path.getmtime(chemin_fichier)
    en_second = time.time() - derniere_modif
    return en_second / 86400


def supp_ancien_rapport(jours_fichier):
    """
    Supprime les rapports JSON dont l'âge dépasse un nombre de jours donné.

    Recherche tous les fichiers correspondant au motif ``rapport_*.json``
    dans le dossier des rapports et supprime ceux dont la dernière
    modification est antérieure à ``jours_fichier`` jours.

    :param jours_fichier: Âge maximal (en jours) au-delà duquel un rapport est supprimé.
    :type jours_fichier: int ou float
    :return: Liste des chemins des rapports supprimés.
    :rtype: list[str]

    :exemple:
        >>> supp_ancien_rapport(30)
        ['/projet/rapports/rapport_2024-01-10.json']
    """
    dossiers_rapports = chemin_rapports()
    model_rapport = os.path.join(dossiers_rapports, "rapport_*.json")
    tout_rapports = glob.glob(model_rapport)
    supp_rapport = []

    for chemin_rapport in tout_rapports:
        if age_fichier(chemin_rapport) > jours_fichier:
            os.remove(chemin_rapport)
            supp_rapport.append(chemin_rapport)

    return supp_rapport


def archiver_et_nettoyer(chemin_logs, destination, jours_fichier):
    """
    Orchestre la sauvegarde complète : compression, déplacement et nettoyage.

    Effectue les étapes suivantes dans l'ordre :

    1. Vérifie que l'espace disque est suffisant.
    2. Crée une archive ``.tar.gz`` des fichiers journaux fournis.
    3. Déplace l'archive vers le dossier de destination.
    4. Supprime les anciens rapports JSON dépassant l'âge limite.

    :param chemin_logs: Liste des chemins des fichiers ``.log`` à archiver.
    :type chemin_logs: list[str]
    :param destination: Chemin du dossier où stocker l'archive finale.
    :type destination: str
    :param jours_fichier: Âge maximal (en jours) des rapports à conserver.
    :type jours_fichier: int ou float

    :return: Dictionnaire contenant :
        - **archive** (*str*) : Chemin final de l'archive créée.
        - **rapports_supprimes** (*list[str]*) : Liste des rapports supprimés.
    :rtype: dict

    :raises RuntimeError: Si l'espace disque disponible est insuffisant
                          (délégué à :func:`verifier_espace`).

    :exemple:
        >>> resultat = archiver_et_nettoyer(["/logs/app.log"], "/var/backups", 30)
        >>> resultat["archive"]
        '/var/backups/backup_2024-06-15.tar.gz'
        >>> resultat["rapports_supprimes"]
        ['/projet/rapports/rapport_2024-01-10.json']
    """
    verifier_espace(destination if os.path.isdir(destination)
                               else chemin_racine())

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