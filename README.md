# LogAnalyzer — Analyseur et archiveur de fichiers journaux

## 1. Description du projet et objectif

**LogAnalyzer** est un outil en ligne de commande Python qui automatise l'analyse, la génération de rapports et l'archivage de fichiers journaux (`.log`).

L'objectif est de permettre à un administrateur système ou développeur de :
- **Analyser** un dossier de fichiers `.log` et d'en extraire des statistiques (nombre de lignes, répartition par niveau ERROR / WARN / INFO, messages d'erreur récurrents).
- **Générer** automatiquement un rapport JSON horodaté résumant l'analyse.
- **Archiver** les fichiers journaux dans une archive compressée `.tar.gz` et nettoyer les anciens rapports dépassant un âge défini.

---

## 2. Prérequis et installation

### Version Python requise

```
Python 3.8 ou supérieur
```

### Dépendances externes

> ✅ **Aucune dépendance externe** — le projet utilise uniquement la bibliothèque standard Python.

Les modules utilisés sont : `os`, `sys`, `json`, `glob`, `tarfile`, `shutil`, `platform`, `time`, `datetime`, `pathlib`, `argparse`.

### Installation

```bash
# 1. Cloner ou télécharger le projet
git clone https://github.com/mugiwara-no-yazid/LogAnalyzer-Pro.git
cd loganalyzer

```

---

## 3. Utilisation

### Syntaxe générale

```bash
python main.py --source <source> --dest <destination> [--retention <nombre_de_jours>] [--niveau <"ERROR", "WARN", "INFO", "ALL">]
```

### Arguments

| Argument        | Type      | Description                                                              |
|-----------------|-----------|--------------------------------------------------------------------------|
| `--source`        | `str`   | Chemin du dossier contenant les fichiers `.log` à analyser               |
| `--dest`          | `str`   | Chemin du dossier où déposer l'archive `.tar.gz` générée                 |
| `--retention`     | `int`   | Nombre de jours au-delà duquel les anciens rapports JSON sont supprimés  |
| `--niveau`        | `str`   | *(Optionnel)* Niveau de log à cibler :`ALL`, `ERROR`, `WARN` ou `INFO`   |

### Exemples de commandes

```bash
# Analyse basique : logs dans ./logs, archive dans ./backups, supprime rapports > 30 jours
python main.py --source ./logs --dest ./backups

# Avec filtre sur le niveau ERROR uniquement
python main.py --source ./logs --dest ./backups --retention 30 --niveau ERROR

# Chemin absolu, conservation des rapports sur 7 jours
python main.py --source ./logs --dest ./backups --retention 7

```

### Exemple de sortie console

```
[1/3] Analyse des logs dans : C:\Users\test\Desktop\python\LogAnalyzer-Pro\logs_test
    → 62 lignes lues | ERROR=19 WARN=17 INFO=26

[2/3] Génération du rapport JSON...
Rapport sauvegardé avec succès : C:\Users\test\Desktop\python\LogAnalyzer-Pro\rapports\rapport_2026-03-25.json

[3/3] Archivage vers 'C:\Users\test\Desktop\python\LogAnalyzer-Pro' (rétention : 2 jours)...
    → Archive créée

 Pipeline terminé avec succès !
```

---

## 4. Description des modules

```
loganalyzer/
├── main.py        ← Point d'entrée, orchestration générale
├── analyser.py    ← Lecture et analyse des fichiers .log
├── rapport.py     ← Génération du rapport JSON
└── archiver.py    ← Compression et nettoyage des archives
```

### `main.py` — Point d'entrée

Gère la lecture des arguments en ligne de commande, orchestre l'appel aux trois autres modules dans le bon ordre et affiche les résultats finaux dans le terminal.

### `analyser.py` — Analyse des journaux

Parcourt tous les fichiers `.log` d'un dossier source. Pour chaque ligne, détecte le niveau (`ERROR`, `WARN`, `INFO`), comptabilise les occurrences et identifie les messages d'erreur récurrents. Retourne un dictionnaire complet de statistiques.

### `rapport.py` — Génération du rapport

Prend les statistiques produites par `analyser.py`, y ajoute les métadonnées système (date, utilisateur, OS, source) et écrit le tout dans un fichier `rapport_YYYY-MM-DD.json` dans le sous-dossier `rapports/`.

### `archiver.py` — Archivage et nettoyage

Vérifie l'espace disque disponible, compresse les fichiers `.log` dans une archive `backup_YYYY-MM-DD.tar.gz`, déplace celle-ci vers la destination, puis supprime les rapports JSON dont l'âge dépasse le nombre de jours configuré.

---

## 5. Planification automatique avec Cron

```cron
0 2 * * 1 /usr/bin/python3 /chemin/vers/loganalyzer/main.py --source /var/logs/app --dest /var/backups --niveau ALL --retention 30 >> /var/logs/loganalyzer.log 2>&1
```
> **Résultat :** le script s'exécute **tous les lundis à 2h00**, analyse les logs de `/var/logs/app`, dépose l'archive dans `/var/backups`, supprime les rapports de plus de 30 jours et consigne toute la sortie dans `/var/logs/loganalyzer.log`.

---

## 6. Répartition des tâches

**SOUMANOU Yazid** `analyser.py` :Lecture des fichiers `.log`, comptage par niveau détection des erreurs récurrentes 

**MESSOHOUNSOUNOU Caleb** `main.py` : Point d'entrée, gestion des arguments CLI, orchestration des modules 

**BOUDZOUMOU Florent** `archiver.py`: Compression `.tar.gz`, vérification d'espace disque, nettoyage des anciens rapports

**HOUEHO Vianney** `rapport.py`: Génération et sauvegarde du rapport JSON horodaté avec métadonnées système
