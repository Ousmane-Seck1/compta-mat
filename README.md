# Application de comptabilite des matieres

Application web Django pour la gestion des matieres: bons, inventaires, mouvements internes, PV et reporting.

## Fonctionnalites principales

- gestion de la nomenclature des matieres
- creation de bons d'entree, de sortie definitive et de sortie provisoire
- gestion des mouvements internes (affectation, mutation, desaffectation)
- gestion des localisations et inventaire individuel contradictoire
- impression des bons au format A4
- livre-journal des mouvements
- grand livre par matiere
- releve recapitulatif avec inventaire physique
- ecran documents (televersement/telechargement des modeles officiels)
- authentification Django avec profils utilisateurs

## Guide utilisateur (vue d'ensemble)

Cette section decrit les ecrans et les actions usuelles. Ajoute tes captures d'ecran aux emplacements indiques.

### Acces et selection du contexte

- Connexion via l'ecran d'authentification.
- Choisir le service et l'exercice si necessaire.
- Acces aux 4 ecrans principaux via le menu.

Capture a ajouter: ecran de connexion.

### Ecran 1 - Administration

- Gestion des utilisateurs et profils.
- Parametres globaux et par structure.
- Rapport central et consolidation trimestrielle (admin).

Capture a ajouter: ecran Administration.

### Ecran 2 - Operations comptables

- Creation des bons (entree, sortie definitive, sortie provisoire).
- Livre-journal et grand livre.
- Releve recapitulatif et PV de recensement.
- Cloture d'exercice et report.

Capture a ajouter: ecran Operations.

### Ecran 3 - Mouvements internes

- Localisations et responsables.
- Bordereaux internes (affectation, mutation, desaffectation).
- Inventaire individuel contradictoire par localisation.

Capture a ajouter: ecran Mouvements internes.

### Ecran 4 - Modeles de documents

- Televersement/telechargement des modeles officiels.
- Suivi des controles de securite documents.

Capture a ajouter: ecran Documents.

## Flux principaux (pas a pas)

### 1) Creer un bon d'entree

1. Aller sur l'ecran Operations comptables.
2. Cliquer sur "Nouveau bon".
3. Choisir "Entree", renseigner la date, la provenance et les lignes.
4. Enregistrer puis imprimer si besoin.

### 2) Creer un bon de sortie

1. Aller sur l'ecran Operations comptables.
2. Choisir "Sortie definitive" ou "Sortie provisoire".
3. Renseigner les lignes, enregistrer, puis imprimer.

### 3) Realiser un mouvement interne

1. Aller sur l'ecran Mouvements internes.
2. Choisir le type (affectation, mutation, desaffectation).
3. Renseigner les localisations et les lignes.

### 4) Produire un PV de recensement

1. Aller sur l'ecran Operations comptables.
2. Ouvrir le PV de recensement.
3. Saisir les quantites physiques puis enregistrer.
4. Imprimer le PV.

## Navigation fonctionnelle

- Ecran 1 - Administration: utilisateurs, nomenclature, parametres, rapport central, guide utilisateur
- Ecran 2 - Operations comptables: bons, journaux, releves, PV, rapport final, cloture/report
- Ecran 3 - Mouvements internes: localisations, bordereaux internes, inventaire individuel contradictoire
- Ecran 4 - Modeles de documents: televersement/telechargement des formulaires officiels

## Prerequis

- Python 3.14+
- dependances installees via `pip install -r requirements.txt`

## Installation locale

Windows (PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Variables d'environnement (optionnel en dev):

- `DJANGO_DEBUG` (True/False)
- `DJANGO_SECRET_KEY` (obligatoire si DEBUG=False)
- `DJANGO_ALLOWED_HOSTS` (liste separee par des virgules)

Exemples PowerShell:

```bash
$env:DJANGO_DEBUG="True"
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
```

Exemples Bash:

```bash
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
```

## Lancement de l'application web

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'application est ensuite accessible sur `http://127.0.0.1:8000`.

## Deploiement (essentiel)

- definir `DJANGO_DEBUG=False`
- definir `DJANGO_SECRET_KEY` (obligatoire en production)
- definir `DJANGO_ALLOWED_HOSTS`
- collecter les statiques:

```bash
python manage.py collectstatic
```

## Verification qualite rapide

Pour lancer les verifications essentielles (check Django + tests inventory):

```bash
python manage.py quality_check
```

Pour executer uniquement les checks Django (sans tests):

```bash
python manage.py quality_check --skip-tests
```

Pour une verification pre-production complete (backup SQLite + check + tests + collectstatic):

```bash
python manage.py preprod_check
```

Variantes utiles:

```bash
python manage.py preprod_check --skip-tests
python manage.py preprod_check --skip-collectstatic
python manage.py preprod_check --skip-backup
```

Purge automatique des logs securite documents (planifiable via cron/Task Scheduler):

```bash
python manage.py purge_document_security_logs
python manage.py purge_document_security_logs --days 90
```

## Comptes et profils

- Django gere l'authentification
- chaque utilisateur dispose d'un profil avec role et centre de responsabilite
- les administrateurs peuvent piloter les utilisateurs depuis l'admin Django

## Impression

- chaque bon dispose d'une page detail imprimable
- l'impression utilise un gabarit HTML/CSS A4, sans dependance externe

## Documents et medias

- Les modeles officiels sont dans `compta_web/media/documents/`.
- Les rapports generes (PDF/XLSX) sont stockes dans `compta_web/media/quarterly_reports/` et sont ignores par Git.

## Structure principale

- `manage.py`: point d'entree Django
- `compta_web/`: configuration du projet Django
- `inventory/`: application metier de comptabilite des matieres

## Parametres de securite et performance

Dans `compta_web/settings.py`, vous pouvez ajuster:

- `DOCUMENT_UPLOAD_MAX_BYTES`: taille max des documents uploades
- `DOCUMENT_UPLOAD_ALLOWED_CONTENT_TYPES`: liste MIME autorisee
- `DOCUMENT_UPLOAD_SCAN_ENABLED`: active/desactive le scan antivirus optionnel
- `DOCUMENT_UPLOAD_SCAN_COMMAND`: commande externe de scan (exemple ClamAV)
- `DOCUMENT_SECURITY_LOG_RETENTION_DAYS`: nombre de jours de conservation des logs de securite documents
- `CENTRAL_RECAP_CACHE_TIMEOUT_SECONDS`: duree du cache du rapport central

Notes techniques:

- Le cache du rapport central est invalide automatiquement a chaque creation/modification/suppression de bon.
- Les rejets de documents (extension/MIME/taille/scan) sont traces dans le journal d'audit (entite `DocumentSecurity`).

## Purge automatique des logs de securite (Windows)

Pour automatiser la purge des logs de sécurité selon la politique de rétention :

1. Ouvrez un terminal PowerShell en mode administrateur.
2. Exécutez le script batch fourni :

    schedule_purge_task.bat

Ce script crée une tâche planifiée Windows qui lance chaque nuit à 2h la commande :

    C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe manage.py purge_document_security_logs

- La politique de rétention est celle définie dans `DOCUMENT_SECURITY_LOG_RETENTION_DAYS` dans `settings.py`.
- Pour vérifier ou modifier la tâche : utilisez l’outil Planificateur de tâches Windows (`taskschd.msc`).
- Pour supprimer la tâche :

    schtasks /Delete /TN "PurgeDocumentSecurityLogs" /F

**Remarque :**
- Le script et la tâche nécessitent des droits administrateur.
- Adaptez les chemins si votre installation diffère.

