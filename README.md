# Application de comptabilite des matieres

Le projet inclut maintenant une application web Django, plus adaptee a la gestion multi-utilisateur, a l'authentification et a l'impression des bons.

## Fonctionnalites

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

## Navigation fonctionnelle

- Ecran 1 - Administration: utilisateurs, nomenclature, parametres, rapport central, guide utilisateur
- Ecran 2 - Operations comptables: bons, journaux, releves, PV, rapport final, cloture/report
- Ecran 3 - Mouvements internes: localisations, bordereaux internes, inventaire individuel contradictoire
- Ecran 4 - Modeles de documents: televersement/telechargement des formulaires officiels

## Prerequis

- Python 3.14+
- dependances installees via `pip install -r requirements.txt`

## Lancement de l'application web

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'application est ensuite accessible sur `http://127.0.0.1:8000`.

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

## Purge automatique des logs de sécurité (Windows)

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

