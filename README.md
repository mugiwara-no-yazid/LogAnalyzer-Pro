# LogAnalyzer Pro 🔍

> **Pipeline d'Analyse et d'Archivage de Logs en Python**  
> TP – Programmation Système en Python | L3 Informatique | 2026

---

## Table des Matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Contexte pédagogique (TP)](#2-contexte-pédagogique-tp)
3. [Architecture du projet](#3-architecture-du-projet)
4. [Prérequis & Installation](#4-prérequis--installation)
5. [Utilisation](#5-utilisation)
6. [Description détaillée de chaque fichier](#6-description-détaillée-de-chaque-fichier)
   - [main.py – Point d'entrée et orchestrateur](#61-mainpy--point-dentrée-et-orchestrateur)
   - [analyser.py – Analyse des fichiers de log](#62-analyserpy--analyse-des-fichiers-de-log)
   - [rapport.py – Génération du rapport JSON](#63-rapportpy--génération-du-rapport-json)
   - [archiver.py – Archivage et nettoyage](#64-archiverpy--archivage-et-nettoyage)
7. [Flux de données – Comment tout s'interconnecte](#7-flux-de-données--comment-tout-sinterconnecte)
8. [Format des fichiers .log](#8-format-des-fichiers-log)
9. [Format du rapport JSON généré](#9-format-du-rapport-json-généré)
10. [Structure des dossiers](#10-structure-des-dossiers)
11. [Exemple d'exécution complète](#11-exemple-dexécution-complète)
12. [Gestion des erreurs](#12-gestion-des-erreurs)
13. [Limitations et améliorations possibles](#13-limitations-et-améliorations-possibles)

---

## 1. Présentation du projet

**LogAnalyzer Pro** est un outil en ligne de commande écrit en **Python 3** qui implémente un **pipeline complet d'analyse et d'archivage de fichiers de logs**. Il se décompose en **4 modules** :

| Module | Rôle |
|--------|------|
| **Module 1** — `analyser.py` | Parcourt tous les fichiers `.log` d'un dossier, compte les niveaux (`ERROR`, `WARN`, `INFO`), identifie les messages d'erreur récurrents |
| **Module 2** — `rapport.py` | Génère un rapport structuré au format **JSON** avec les statistiques + des métadonnées système |
| **Module 3** — `archiver.py` | Compresse les fichiers `.log` dans une archive **`.tar.gz`**, la déplace vers une destination, puis supprime les anciens rapports selon une durée de rétention |
| **Module 4** — `main.py` | **Chef d'orchestre** — parse les arguments CLI, appelle les 3 modules dans l'ordre, gère les erreurs fatales et affiche la progression |

---

## 2. Contexte pédagogique (TP)

Ce projet répond au **TP de Programmation Système en Python (L3 – 2026)** dont l'objectif est de valider la maîtrise des thèmes suivants :

- **Manipulation du système de fichiers** : `os`, `pathlib`, `glob`, `shutil`
- **Archivage et compression** : module `tarfile` (format `.tar.gz`)
- **Sérialisation de données** : module `json`
- **Interface en ligne de commande** : module `argparse`
- **Introspection système** : module `platform`
- **Gestion des exceptions** : `try/except`, `sys.exit()`
- **Traitement de fichiers texte** : lecture ligne par ligne, parsing de logs

Le rendu attendu comprend : le code source commenté, ce README technique, et une démo.

---

## 3. Architecture du projet

```
LogAnalyzer-Pro/
│
├── main.py            ← Point d'entrée CLI — orchestre les 3 étapes
├── analyser.py        ← Étape 1 : Parsing et analyse des logs
├── rapport.py         ← Étape 2 : Génération du rapport JSON
├── archiver.py        ← Étape 3 : Archivage .tar.gz + nettoyage
│
├── logs_test/         ← Fichiers de logs de test fournis
│   ├── app1.log
│   ├── app2.log
│   └── app3.log
│
├── rapports/          ← Dossier auto-créé — contient les rapports JSON générés
│   ├── rapport_2026-03-21.json
│   └── rapport_2026-03-24.json
│
├── backups/           ← Dossier cible des archives .tar.gz (configurable)
│
├── .gitignore         ← Ignore __pycache__/
└── README.md          ← Ce fichier
```

### Diagramme de dépendances entre modules

```
main.py
  ├── import analyser   →  analyser.py
  ├── import rapport    →  rapport.py
  └── import archiver   →  archiver.py
```

`main.py` est le **seul chef d'orchestre**. Les trois autres modules sont des bibliothèques indépendantes qui n'importent pas entre elles.

---

## 4. Prérequis & Installation

### Prérequis

- **Python 3.8+** (testé sur Windows 10/11)
- Aucune dépendance externe — uniquement la **bibliothèque standard Python**

### Modules utilisés (stdlib uniquement)

| Module | Utilisé dans | Rôle |
|--------|-------------|------|
| `argparse` | `main.py` | Parsing des arguments CLI |
| `os` | tous | Manipulation chemins, variables environnement |
| `sys` | `main.py`, `rapport.py` | Sortie d'erreur fatale via `sys.exit(1)` |
| `glob` | `main.py`, `archiver.py` | Recherche de fichiers par motif |
| `pathlib` | `analyser.py` | Vérification dossier + glob des `.log` |
| `platform` | `analyser.py`, `rapport.py` | Détection OS et version |
| `json` | `rapport.py` | Sérialisation du rapport |
| `shutil` | `archiver.py` | Espace disque + déplacement de fichiers |
| `tarfile` | `archiver.py` | Création d'archives `.tar.gz` |
| `time` | `archiver.py` | Calcul de l'âge des fichiers |
| `datetime` | `rapport.py`, `archiver.py` | Horodatage des rapports et archives |

### Installation

```bash
# Cloner ou télécharger le projet
git clone <url-du-repo>
cd LogAnalyzer-Pro

# Aucune installation supplémentaire nécessaire (stdlib only)
```

---

## 5. Utilisation

### Syntaxe complète

```bash
python main.py --source <dossier_logs> --dest <dossier_archives> [--niveau NIVEAU] [--retention JOURS]
```

### Arguments

| Argument | Type | Obligatoire | Défaut | Description |
|----------|------|-------------|--------|-------------|
| `--source` | `str` | ✅ Oui | — | Chemin du dossier contenant les fichiers `.log` à analyser |
| `--dest` | `str` | ✅ Oui | — | Dossier de destination des archives `.tar.gz` |
| `--niveau` | `str` | ❌ Non | `ALL` | Filtre de criticité : `ERROR`, `WARN`, `INFO`, ou `ALL` |
| `--retention` | `int` | ❌ Non | `30` | Nombre de jours de rétention des rapports JSON |

> **Note sur `--niveau`** : Le paramètre `--niveau` est bien parsé et validé par `argparse` (choix restreints), mais dans la version actuelle, `analyser.py` compte toujours tous les niveaux indépendamment de ce filtre. Il s'agit d'un point d'amélioration.

### Exemples d'appel

```bash
# Analyse basique avec les dossiers de test fournis
python main.py --source ./logs_test --dest ./backups

# Filtrer uniquement les ERRORs, rétention de 7 jours
python main.py --source ./logs_test --dest ./backups --niveau ERROR --retention 7

# Chemin absolu Windows
python main.py --source "C:\Users\user\logs" --dest "C:\Users\user\archives" --retention 60
```

---

## 6. Description détaillée de chaque fichier

---

### 6.1 `main.py` – Point d'entrée et orchestrateur

**Rôle** : Chef d'orchestre du pipeline. Gère les arguments, appelle les trois modules dans l'ordre, et gère les erreurs fatales.

**Imports**

```python
import argparse   # Parsing des arguments CLI
import glob       # Recherche des fichiers .log traités
import os         # Chemins absolus
import sys        # sys.exit() en cas d'erreur fatale
from analyser import analyser
from rapport import generer_rapport
from archiver import archiver_et_nettoyer
```

---

#### Fonction `recuperer_arguments()` (lignes 14–41)

Définit et parse les 4 arguments CLI via `argparse` :

```python
parser = argparse.ArgumentParser(description="LogAnalyzer Pro — Pipeline d'analyse et d'archivage de logs")
parser.add_argument("--source", required=True, ...)
parser.add_argument("--niveau", choices=["ERROR", "WARN", "INFO", "ALL"], default="ALL", ...)
parser.add_argument("--dest", required=True, ...)
parser.add_argument("--retention", type=int, default=30, ...)
return parser.parse_args()
```

- `choices=["ERROR", "WARN", "INFO", "ALL"]` : argparse refuse automatiquement toute valeur non listée
- `type=int` sur `--retention` : conversion automatique et rejet des non-entiers
- Si `--source` ou `--dest` manque, argparse affiche l'aide et termine le programme

---

#### Fonction `main()` (lignes 44–113)

C'est le **pipeline principal** en 3 étapes :

**Initialisation**
```python
args = recuperer_arguments()
source_absolue = os.path.abspath(args.source)   # Convertit en chemin absolu
dest_absolue   = os.path.abspath(args.dest)
```
L'usage de `os.path.abspath()` garantit qu'un chemin relatif comme `./logs_test` fonctionnera quel que soit le répertoire de travail courant.

**Étape 1 — Analyse**
```python
resultats = analyser(source_absolue, args.niveau)
```
`analyser()` retourne un dictionnaire avec trois clés :
- `"Nombre total de lignes analysées"` → entier
- `"Comptage par niveau"` → dict `{ERROR, WARN, INFO}`
- `"message recurent"` → liste de `[message, count]` triée par fréquence décroissante

Le `main` extrait ensuite les 5 messages d'erreur les plus fréquents :
```python
messages_tris = resultats["message recurent"]
top5_erreurs  = [msg for msg, _ in messages_tris[:5]]
```

**Étape 2 — Rapport**
```python
chemin_rapport = generer_rapport(
    source=source_absolue,
    total_lignes=total_lignes,
    par_niveau=par_niveau,
    top5_erreurs=top5_erreurs,
    fichiers_traites=fichiers_traites
)
```
Retourne le chemin absolu vers le rapport JSON créé.

**Étape 3 — Archivage**
```python
resultat_archive = archiver_et_nettoyer(
    chemin_logs=fichiers_traites,
    destination=dest_absolue,
    jours_fichier=args.retention
)
```
Retourne un dict `{"archive": chemin, "rapports_supprimes": [liste]}`.

**Gestion des erreurs** : chaque étape est encapsulée dans un `try/except`. En cas d'erreur, le message est affiché et `sys.exit(1)` stoppe le programme proprement.

---

### 6.2 `analyser.py` – Analyse des fichiers de log

**Rôle** : Lit tous les fichiers `.log` du dossier source, compte les occurrences par niveau de criticité, et identifie les messages d'erreur les plus fréquents.

**Imports**

```python
from pathlib import Path
import os
import platform
```

---

#### Fonction `tri_dict(dictionnaire)` (lignes 5–12)

Implémente un **tri à bulles (bubble sort) manuel** pour trier un dictionnaire par valeur décroissante :

```python
def tri_dict(dictionnaire):
    items = [list(item) for item in dictionnaire.items()]
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if items[j][1] < items[j + 1][1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items
```

- Convertit les paires `(clé, valeur)` du dictionnaire en liste de listes `[[clé, valeur], ...]`
- Tri décroissant : le plus fréquent d'abord
- **Choix pédagogique** : utilise un bubble sort maison plutôt que `sorted()` pour démontrer la maîtrise des algorithmes de tri

**Exemple** :
```python
# Entrée : {"Erreur A": 5, "Erreur B": 12, "Erreur C": 2}
# Sortie :  [["Erreur B", 12], ["Erreur A", 5], ["Erreur C", 2]]
```

---

#### Fonction `obtenir_metadonnees()` (lignes 13–22)

Collecte des informations sur l'environnement d'exécution :

```python
def obtenir_metadonnees():
    systeme     = platform.system()    # "Windows", "Linux", "Darwin"
    version_os  = platform.release()   # ex: "10", "22.04"
    utilisateur = os.environ.get('USER') or os.environ.get('USERNAME') or "Inconnu"
    return {"os": f"{systeme} {version_os}", "user": utilisateur}
```

- `platform.system()` + `platform.release()` → nom et version de l'OS, compatible cross-plateforme
- `os.environ.get('USER')` fonctionne sur Linux/macOS ; `'USERNAME'` sur Windows
- Le `or "Inconnu"` est un fallback si les deux variables sont absentes

---

#### Fonction `analyser(source, niveau)` (lignes 24–55)

Cœur de l'analyse. Parcourt récursivement (en fait seulement le niveau racine via `*.log`) tous les fichiers de log :

```python
def analyser(source, niveau):
    nbrNiveau = {"ERROR": 0, "WARN": 0, "INFO": 0}
    allPhrase = 0
    nbrErrorPhrase = {}
    chemin = Path(source)

    if not chemin.is_dir():
        raise NotADirectoryError(...)

    for item in chemin.glob('*.log'):
        with open(item, "r", encoding="utf-8") as file:
            for numero, ligne in enumerate(file, start=1):
                if "ERROR" in ligne:
                    message = ligne.split("ERROR ")[1]
                    nbrErrorPhrase[message] = nbrErrorPhrase.get(message, 0) + 1
                    nbrNiveau["ERROR"] += 1
                if "WARN"  in ligne: nbrNiveau["WARN"]  += 1
                if "INFO"  in ligne: nbrNiveau["INFO"]  += 1
                allPhrase += 1
    ...
```

**Mécanisme d'extraction des messages d'erreur** :
- Pour chaque ligne contenant `"ERROR"`, on extrait la partie **après** `"ERROR "` (avec l'espace)
- Ce texte sert de clé dans le dictionnaire `nbrErrorPhrase` qui compte les occurrences

**Exemple** :
```
Ligne : "2024-04-01 07:16:01 ERROR Échec de la connexion au serveur LDAP"
Split  : ligne.split("ERROR ")[1]  →  "Échec de la connexion au serveur LDAP\n"
```

**Retour de la fonction** :
```python
return {
    "Nombre total de lignes analysées": allPhrase,
    "message recurent": tri_dict(nbrErrorPhrase),   # Trié par fréquence décrois.
    "Comptage par niveau": nbrNiveau,
    "metaDonne": obtenir_metadonnees()
}
```

> **Note** : Le comptage des niveaux `WARN` et `INFO` utilise un simple `in ligne`, ce qui signifie qu'une ligne contenant à la fois `"INFO"` et `"ERROR"` incrémenterait les deux compteurs.

---

### 6.3 `rapport.py` – Génération du rapport JSON

**Rôle** : Prend les résultats de l'analyse et les sérialise dans un fichier JSON nommé par la date courante, dans le dossier `rapports/`.

**Imports**

```python
import json
import os
import platform
import sys
from datetime import datetime
```

---

#### Fonction `generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites)` (lignes 9–52)

```python
def generer_rapport(source, total_lignes, par_niveau, top5_erreurs, fichiers_traites):
    maintenant    = datetime.now()
    date_fichier  = maintenant.strftime("%Y-%m-%d")        # Pour le nom de fichier
    date_rapport  = maintenant.strftime("%Y-%m-%d %H:%M:%S")  # Pour le contenu

    utilisateur = os.environ.get("USER") or os.environ.get("USERNAME") or "Inconnu"
    systeme_os  = platform.system()
```

**Construction du dictionnaire de données** :
```python
donnees_rapport = {
    "metadata": {
        "date":         date_rapport,    # Horodatage précis au moment de l'exécution
        "utilisateur":  utilisateur,     # Nom de l'utilisateur système
        "os":           systeme_os,      # Système d'exploitation
        "source":       source           # Chemin absolu du dossier analysé
    },
    "statistiques": {
        "total_lignes": total_lignes,    # Nombre total de lignes parcourues
        "par_niveau":   par_niveau,      # {"ERROR": n, "WARN": n, "INFO": n}
        "top5_erreurs": top5_erreurs     # Liste des 5 messages d'erreur les + fréquents
    },
    "fichiers_traites": fichiers_traites  # Liste des chemins absolus des .log analysés
}
```

**Création du dossier et écriture du fichier** :
```python
dossier_rapports = os.path.join(dossier_actuel, "rapports")
if not os.path.exists(dossier_rapports):
    os.makedirs(dossier_rapports)

nom_fichier = f"rapport_{date_fichier}.json"   # ex: rapport_2026-03-24.json
chemin_complet_fichier = os.path.join(dossier_rapports, nom_fichier)

with open(chemin_complet_fichier, "w", encoding="utf-8") as fichier:
    json.dump(donnees_rapport, fichier, indent=4)
```

- `os.makedirs()` crée récursivement le dossier s'il n'existe pas
- `json.dump(..., indent=4)` produit un JSON lisible (pretty-printed)
- Le nom de fichier inclut la date : si exécuté deux fois le même jour, le rapport est **écrasé**
- **Retourne** le chemin absolu du fichier créé, que `main.py` utilise pour l'afficher

---

### 6.4 `archiver.py` – Archivage et nettoyage

**Rôle** : Crée une archive `.tar.gz` des fichiers `.log`, la déplace vers la destination, puis supprime les rapports JSON dont l'âge dépasse la durée de rétention.

**Imports**

```python
import glob, os, shutil, subprocess, tarfile, time
from datetime import datetime
```

**Constantes globales** :
```python
dossier_sauvegarde  = "backups"
dossier_rapports    = "rapports"
BYTES_PER_MEGABYTE  = 1024 * 1024  # 1 048 576 octets
espace_min          = 50            # Espace disque minimum requis : 50 Mo
```

---

#### Fonctions utilitaires de chemin (lignes 16–25)

```python
def chemin_racine():       return os.path.dirname(os.path.abspath(__file__))
def chemin_sauvegarde():   return os.path.join(chemin_racine(), dossier_sauvegarde)
def chemin_rapports():     return os.path.join(chemin_racine(), dossier_rapports)
```

`__file__` désigne toujours `archiver.py` lui-même, ce qui permet de construire des chemins absolus **relatifs au projet** et non au répertoire de travail.

---

#### Fonction `creer_archive(date_creation)` (lignes 28–30)

```python
def creer_archive(date_creation):
    date_slug = date_creation.strftime("%Y-%m-%d")
    return f"backup_{date_slug}.tar.gz"   # ex: backup_2026-03-24.tar.gz
```

Génère le **nom** de l'archive basé sur la date courante. Ce nom est unique par jour.

---

#### Fonction `verifier_espace(destination)` (lignes 33–42)

```python
def verifier_espace(destination):
    total, used, free = shutil.disk_usage(destination if os.path.isdir(destination) else chemin_racine())
    espace_dispo = free // BYTES_PER_MEGABYTE

    if espace_dispo < espace_min:
        raise RuntimeError(f"Espace insuffisant : {espace_dispo} mo dispo (minimum requis : {espace_min} mo).")
```

- Utilise `shutil.disk_usage()` qui retourne un 3-tuple `(total, used, free)` en octets
- La division `// BYTES_PER_MEGABYTE` convertit en Mégaoctets
- Si l'espace est inférieur à **50 Mo**, lève une `RuntimeError` avant de créer quoi que ce soit

---

#### Fonction `compresse_archiv(chemin_logs, chemin_archives)` (lignes 46–49)

```python
def compresse_archiv(chemin_logs, chemin_archives):
    with tarfile.open(chemin_archives, "w:gz") as archive:
        for chemin_des_log in chemin_logs:
            archive.add(chemin_des_log, arcname=os.path.basename(chemin_des_log))
```

- Mode `"w:gz"` : écriture avec compression gzip (format `.tar.gz`)
- `arcname=os.path.basename(...)` : stocke seulement le **nom de fichier** dans l'archive, sans son chemin absolu complet
- L'archive temporaire est créée **dans le dossier racine du projet** avant d'être déplacée

---

#### Fonction `deplacer_archive(chemin_archiv, destination)` (lignes 51–57)

```python
def deplacer_archive(chemin_archiv, destination):
    os.makedirs(destination, exist_ok=True)
    dest_finale = os.path.join(destination, os.path.basename(chemin_archiv))

    if os.path.exists(dest_finale):
        os.remove(dest_finale)       # Supprime une archive du même jour si elle existe déjà
    return shutil.move(chemin_archiv, destination)
```

- `os.makedirs(..., exist_ok=True)` : crée le dossier de destination s'il n'existe pas (sans erreur s'il existe déjà)
- Si une archive du même nom (même jour) existe, elle est **supprimée** avant le déplacement
- `shutil.move()` déplace le fichier et **retourne le chemin de destination finale**

---

#### Fonction `age_fichier(chemin_fichier)` (lignes 59–62)

```python
def age_fichier(chemin_fichier):
    derniere_modif = os.path.getmtime(chemin_fichier)   # Timestamp Unix de la dernière modification
    en_second      = time.time() - derniere_modif        # Différence en secondes
    return en_second / 86400                             # Conversion en jours (60s × 60min × 24h)
```

Calcule l'âge d'un fichier en **jours flottants** à partir de son timestamp de dernière modification.

---

#### Fonction `supp_ancien_rapport(jours_fichier)` (lignes 65–76)

```python
def supp_ancien_rapport(jours_fichier):
    dossiers_rapports = chemin_rapports()
    model_rapport     = os.path.join(dossiers_rapports, "rapport_*.json")
    tout_rapports     = glob.glob(model_rapport)    # Trouve tous les rapport_*.json
    supp_rapport      = []

    for chemin_rapport in tout_rapports:
        if age_fichier(chemin_rapport) > jours_fichier:
            os.remove(chemin_rapport)
            supp_rapport.append(chemin_rapport)

    return supp_rapport
```

- `glob.glob("rapport_*.json")` cible uniquement les fichiers générés par ce pipeline
- Pour chaque rapport, si son âge dépasse `jours_fichier`, il est **supprimé du disque** et ajouté à la liste de résultat
- Retourne la liste des fichiers supprimés (utile pour l'affichage dans `main.py`)

---

#### Fonction `archiver_et_nettoyer(chemin_logs, destination, jours_fichier)` (lignes 79–94)

C'est la **fonction publique** appelée par `main.py`. Elle orchestre toutes les sous-fonctions :

```python
def archiver_et_nettoyer(chemin_logs, destination, jours_fichier):
    # 1. Vérification espace disque
    verifier_espace(destination if os.path.isdir(destination) else chemin_racine())

    # 2. Création de l'archive temporaire dans la racine du projet
    date_creation = datetime.now()
    nom_archive   = creer_archive(date_creation)        # ex: backup_2026-03-24.tar.gz
    temp          = os.path.join(chemin_racine(), nom_archive)

    # 3. Compression
    compresse_archiv(chemin_logs, temp)

    # 4. Déplacement vers la destination finale
    chemin_archiv = deplacer_archive(temp, destination)

    # 5. Nettoyage des anciens rapports
    supp_rapport = supp_ancien_rapport(jours_fichier)

    return {
        "archive":            chemin_archiv,
        "rapports_supprimes": supp_rapport
    }
```

---

## 7. Flux de données – Comment tout s'interconnecte

```
Utilisateur
    │
    ▼ python main.py --source ./logs_test --dest ./backups --retention 7
┌──────────────────────────────────────────────────┐
│                   main.py                        │
│  recuperer_arguments() → args                    │
│  source_absolue = os.path.abspath(args.source)   │
│  dest_absolue   = os.path.abspath(args.dest)     │
└──────────┬───────────────────────────────────────┘
           │
           │ ÉTAPE 1 : Appel à analyser()
           ▼
┌──────────────────────────────────────────────────┐
│                 analyser.py                      │
│  • Parcourt *.log dans source_absolue            │
│  • Compte ERROR / WARN / INFO par ligne          │
│  • Extrait le texte après "ERROR " → fréquences  │
│  • tri_dict() → tri décroissant bubble sort      │
│  • Retourne dict {total, comptage, top_msg, meta}│
└──────────┬───────────────────────────────────────┘
           │ resultats{}
           │
           │ ÉTAPE 2 : Appel à generer_rapport()
           ▼
┌──────────────────────────────────────────────────┐
│                 rapport.py                       │
│  • Construit un dict (metadata + statistiques)   │
│  • Crée ./rapports/ si inexistant                │
│  • json.dump() → rapport_YYYY-MM-DD.json         │
│  • Retourne le chemin absolu du fichier créé     │
└──────────┬───────────────────────────────────────┘
           │ chemin_rapport (str)
           │
           │ ÉTAPE 3 : Appel à archiver_et_nettoyer()
           ▼
┌──────────────────────────────────────────────────┐
│                 archiver.py                      │
│  • verifier_espace() → min 50 Mo                 │
│  • tarfile.open("w:gz") → backup_YYYY-MM-DD.tar.gz │
│  • shutil.move() → déplace vers dest             │
│  • supp_ancien_rapport() → supprime > retention  │
│  • Retourne {archive: chemin, rapports_supprimes} │
└──────────┬───────────────────────────────────────┘
           │
           ▼
    ✅ Pipeline terminé !
    → Archive : ./backups/backup_2026-03-24.tar.gz
    → Rapport  : ./rapports/rapport_2026-03-24.json
```

---

## 8. Format des fichiers .log

Les fichiers `.log` attendus suivent ce format :

```
YYYY-MM-DD HH:MM:SS NIVEAU Message textuel libre
```

**Exemples** (extraits de `logs_test/app1.log`) :
```
2024-04-01 07:00:01 INFO Démarrage du service d'authentification
2024-04-01 07:15:22 WARN Tentative de connexion échouée pour l'utilisateur admin (essai 1/3)
2024-04-01 07:16:01 ERROR Échec de la connexion au serveur LDAP
```

**Niveaux reconnus** :

| Niveau | Signification |
|--------|--------------|
| `INFO` | Information normale, déroulement attendu |
| `WARN` | Avertissement — situation anormale non bloquante |
| `ERROR` | Erreur — action échouée, nécessite attention |

Le pipeline traite **uniquement les fichiers `.log`** (extension stricte via `glob('*.log')`).

---

## 9. Format du rapport JSON généré

Le rapport est créé dans `rapports/rapport_YYYY-MM-DD.json`. Voici sa structure complète :

```json
{
    "metadata": {
        "date":         "2026-03-21 21:14:26",
        "utilisateur":  "LATITUDE 7410",
        "os":           "Windows",
        "source":       "C:\\Users\\LATITUDE 7410\\LogAnalyzer-Pro\\logs_test"
    },
    "statistiques": {
        "total_lignes": 62,
        "par_niveau": {
            "ERROR": 19,
            "WARN":  17,
            "INFO":  26
        },
        "top5_erreurs": [
            "Échec de la connexion au serveur LDAP\n",
            "Timeout de la requête SQL après 30 secondes sur la table utilisateurs\n",
            "Service distant /api/v2/orders injoignable après 3 tentatives\n",
            "Violation de contrainte d'unicité sur la colonne email\n",
            "Token JWT expiré pour l'utilisateur user_4872\n"
        ]
    },
    "fichiers_traites": [
        "C:\\Users\\LATITUDE 7410\\LogAnalyzer-Pro\\logs_test\\app1.log",
        "C:\\Users\\LATITUDE 7410\\LogAnalyzer-Pro\\logs_test\\app2.log",
        "C:\\Users\\LATITUDE 7410\\LogAnalyzer-Pro\\logs_test\\app3.log"
    ]
}
```

**Description de chaque champ** :

| Champ | Type | Description |
|-------|------|-------------|
| `metadata.date` | `str` | Horodatage de l'exécution (format `YYYY-MM-DD HH:MM:SS`) |
| `metadata.utilisateur` | `str` | Nom de l'utilisateur OS courant |
| `metadata.os` | `str` | Système d'exploitation (`Windows`, `Linux`, `Darwin`) |
| `metadata.source` | `str` | Chemin absolu du dossier source analysé |
| `statistiques.total_lignes` | `int` | Nombre total de lignes lues dans tous les `.log` |
| `statistiques.par_niveau` | `dict` | Comptage par niveau : `{ERROR, WARN, INFO}` |
| `statistiques.top5_erreurs` | `list[str]` | 5 messages d'erreur les plus fréquents (texte après `ERROR `) |
| `fichiers_traites` | `list[str]` | Chemins absolus de tous les `.log` traités |

---

## 10. Structure des dossiers

### Avant exécution

```
LogAnalyzer-Pro/
├── main.py
├── analyser.py
├── rapport.py
├── archiver.py
├── logs_test/
│   ├── app1.log
│   ├── app2.log
│   └── app3.log
└── .gitignore
```

### Après exécution

```
LogAnalyzer-Pro/
├── main.py
├── analyser.py
├── rapport.py
├── archiver.py
├── logs_test/
│   ├── app1.log
│   ├── app2.log
│   └── app3.log
├── rapports/                    ← Créé automatiquement
│   └── rapport_2026-03-24.json
├── backups/                     ← Créé si nécessaire (ou autre --dest)
│   └── backup_2026-03-24.tar.gz
└── .gitignore
```

---

## 11. Exemple d'exécution complète

```bash
$ python main.py --source ./logs_test --dest ./backups --retention 7
```

**Sortie console attendue** :

```
[1/3] Analyse des logs dans : C:\Users\LATITUDE 7410\LogAnalyzer-Pro\logs_test
    → 62 lignes lues | ERROR=19 WARN=17 INFO=26

[2/3] Génération du rapport JSON...
Rapport sauvegardé avec succès : C:\...\rapports\rapport_2026-03-24.json

[3/3] Archivage vers 'C:\...\backups' (rétention : 7 jours)...
    → Archive créée   : C:\...\backups\backup_2026-03-24.tar.gz
    → Aucun rapport à supprimer (tous récents).

✅ Pipeline terminé avec succès !
```

---

## 12. Gestion des erreurs

Le pipeline gère trois catégories d'erreurs :

### Erreurs bloquantes (sys.exit(1))

| Scénario | Module | Comportement |
|----------|--------|--------------|
| Dossier source introuvable ou pas un répertoire | `analyser.py` | Lève `NotADirectoryError` → catchée par `main.py` → `sys.exit(1)` |
| Aucun fichier `.log` trouvé dans la source | `main.py` | Affichage "ERREUR FATALE" + `sys.exit(1)` |
| Erreur lors de la génération du rapport | `rapport.py` | Affichage + `sys.exit(1)` |
| Espace disque insuffisant (< 50 Mo) | `archiver.py` | Lève `RuntimeError` → catchée par `main.py` → `sys.exit(1)` |
| Erreur lors de l'archivage | `archiver.py` | Lève une exception → catchée par `main.py` → `sys.exit(1)` |

### Erreurs silencieusement tolérées

| Scénario | Comportement |
|----------|-------------|
| Rapport du même jour déjà existant | Écrasé silencieusement |
| Archive du même jour déjà dans la destination | Supprimée puis remplacée |
| Aucun rapport à supprimer | Affiché "Aucun rapport à supprimer (tous récents)." |

### Codes de sortie

| Code | Signification |
|------|--------------|
| `0` | Pipeline terminé avec succès |
| `1` | Erreur fatale dans l'une des 3 étapes |

---

## 13. Limitations et améliorations possibles

### Limitations actuelles

1. **`--niveau` non appliqué** : Le paramètre `--niveau` passé par l'utilisateur est parsé mais non utilisé dans `analyser.py`. Tous les niveaux sont toujours comptés.

2. **Comptage cumulatif** : Une ligne contenant à la fois `"INFO"` et `"ERROR"` incrémentera les deux compteurs (cas rare en pratique).

3. **`\n` dans les messages d'erreur** : Les messages du `top5_erreurs` dans le JSON contiennent un `\n` final (résidu du split de la ligne).

4. **Import inutilisé** : `subprocess` est importé dans `archiver.py` mais n'est jamais utilisé.

5. **Rapport écrasé le même jour** : Si le pipeline est exécuté deux fois le même jour, le rapport JSON est silencieusement écrasé.

6. **Logs non sous-dossiers** : `glob('*.log')` ne cherche que dans le répertoire racine de la source, pas dans les sous-dossiers.

### Améliorations potentielles

- Appliquer réellement le filtre `--niveau` dans `analyser.py`
- Utiliser `pathlib.Path.rglob('*.log')` pour les sous-dossiers
- Horodater les rapports à la seconde pour éviter l'écrasement
- Ajouter des tests unitaires (`pytest`)
- Ajouter un mode verbeux (`--verbose`) vs silencieux
- Exporter en CSV ou HTML en plus du JSON
- Supprimer le `import subprocess` inutilisé

---

## Auteurs

Projet réalisé dans le cadre du **TP Programmation Système en Python — L3 Informatique 2026**.

---


