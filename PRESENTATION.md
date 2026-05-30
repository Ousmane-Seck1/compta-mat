# 🎯 Guide de Présentation — Comptabilité des Matières

> **Application web de gestion comptable des matières pour les administrations publiques**

---

## 1. Pitch d'accroche (30 secondes)

> « Aujourd'hui, la plupart des services gèrent leur comptabilité des matières sur Excel — avec les risques d'erreurs, de perte de données et l'impossibilité de consolider. Notre application web remplace intégralement ce processus : de la saisie des bons d'entrée/sortie jusqu'à la clôture d'exercice, en passant par l'inventaire physique et les rapports officiels — le tout accessible depuis un simple navigateur, multi-structures, et conforme aux modèles réglementaires. »

---

## 2. Problèmes que l'on résout

| Problème actuel (Excel / Papier)            | Notre solution                                           |
|---------------------------------------------|----------------------------------------------------------|
| Fichiers Excel non sécurisés, pas de backup | Application web avec authentification et rôles           |
| Erreurs de calcul manuelles (CMUP, soldes)  | Calculs automatiques et validation en temps réel         |
| Pas de consolidation multi-services          | Rapport central agrégé pour la hiérarchie                |
| Impression artisanale des bons               | Impression A4 professionnelle avec en-tête officiel      |
| Pas de traçabilité des modifications         | Journal d'audit complet (qui, quand, quoi)               |
| Report de solde manuel à chaque exercice     | Clôture et report automatique avec Bon N°1               |
| Inventaire physique sur papier               | PV de recensement numérique avec calcul des écarts       |
| Aucun contrôle des sorties                   | Validation automatique des stocks disponibles            |

---

## 3. Points forts à mettre en avant

### 🏛️ Conformité réglementaire
- Rapports conformes aux **Modèles 20, 21 et 22** de la comptabilité publique
- En-têtes officiels configurables (pays, ministère, structure)
- Pages de signature intégrées pour l'ordonnateur et le comptable

### 🔒 Sécurité et audit
- Authentification obligatoire avec 3 niveaux de rôle (**Admin**, **Comptable**, **Consultation**)
- Journal d'audit complet tracant chaque opération
- Contrôle de sécurité sur les documents uploadés (type, taille, antivirus optionnel)
- Logs de sécurité exportables en CSV

### 🏢 Multi-structures
- Chaque service/district/centre a son propre espace comptable
- Numérotation indépendante des bons par structure
- L'administrateur voit le rapport consolidé de toutes les structures
- Attribution des utilisateurs à une ou plusieurs structures

### 📊 Rapports professionnels
- **Livre-Journal** : historique chronologique de tous les mouvements
- **Grand Livre** : détail par matière avec solde cumulé
- **Relevé Récapitulatif** : vue synthétique (entrées/sorties/solde)
- **PV de Recensement** : inventaire physique avec calcul des écarts
- **Rapport Final** : balance générale avec régularisations
- **Rapport Central** : consolidation multi-structures (admin)
- Export **PDF** et **Excel** sur tous les rapports

### ⚡ Productivité
- Import Excel pour migration des données existantes
- Calcul automatique du CMUP (Coût Moyen Unitaire Pondéré)
- Recherche et filtrage avancés sur toutes les listes
- Clôture d'exercice en un clic avec report automatique

---

## 4. Architecture des écrans (parcours utilisateur)

```
Connexion
   │
   ▼
Menu Principal
   ├── Écran 1 — Administration
   │     ├── Gestion des utilisateurs
   │     ├── Nomenclature (plan comptable matières)
   │     ├── Paramètres d'impression (logo, en-tête)
   │     ├── Logs de sécurité
   │     ├── Rapport central consolidé
   │     └── Guide utilisateur
   │
   ├── Écran 2 — Opérations comptables
   │     ├── Tableau de bord (indicateurs clés)
   │     ├── Nouveau bon (Entrée / Sortie déf. / Sortie prov.)
   │     ├── Liste des bons (recherche, filtres)
   │     ├── Nomenclature des matières
   │     ├── Livre-Journal
   │     ├── Grand Livre
   │     ├── Relevé Récapitulatif
   │     ├── PV de Recensement (inventaire physique)
   │     ├── Rapport Final + Régularisations
   │     └── Clôture et report d'exercice
   │
      ├── Écran 3 — Mouvements internes
      │     ├── Localisations
      │     ├── Bordereaux (affectation / mutation / désaffectation)
      │     └── Inventaire individuel contradictoire
      │
      └── Écran 4 — Modèles de documents
         └── Téléchargement des formulaires officiels
```

---

## 5. Scénario de démonstration (15-20 min)

### Phase 1 — Contexte (2 min)
1. **Connexion** en tant qu'administrateur
2. Montrer le **menu principal** avec les 4 écrans
3. Montrer la **barre de contexte** (structure + exercice sélectionnés)

### Phase 2 — Administration (3 min)
4. **Paramètres** : montrer la configuration de l'en-tête (pays, ministère, logo)
5. **Nomenclature** : montrer le plan comptable des matières, ajouter un compte
6. **Utilisateurs** : montrer la création d'un utilisateur avec rôle et structure

### Phase 3 — Opérations quotidiennes (5 min)
7. **Tableau de bord** : montrer les indicateurs (nb matières, nb bons, stock total)
8. **Créer un Bon d'Entrée** : sélectionner une matière, quantité, prix → soumettre
9. **Voir le bon** créé et montrer l'**impression A4** (aperçu avec en-tête officiel)
10. **Créer un Bon de Sortie** : montrer la validation de stock disponible
11. **Livre-Journal** : montrer les 2 mouvements qui apparaissent
12. **Grand Livre** : sélectionner la matière → montrer le solde cumulé

### Phase 4 — Rapports et inventaire (5 min)
13. **Relevé Récapitulatif** : vue synthétique → export Excel
14. **PV de Recensement** : saisir l'inventaire physique → montrer les écarts
15. **Rapport Final** : montrer la balance et les régularisations automatiques
16. **Export PDF** d'un rapport avec en-tête officiel et signatures

### Phase 5 — Multi-structures et consolidation (3 min)
17. **Changer de structure** via le sélecteur
18. Montrer que chaque structure a ses propres données
19. **Rapport Central** : montrer la consolidation multi-structures en tableau
20. **Export Excel** du rapport central

### Phase 6 — Clôture (2 min)
21. Montrer la **checklist de pré-clôture** (vérifications automatiques)
22. Montrer l'**aperçu du Bon N°1** de report pour le nouvel exercice
23. Expliquer le processus (pas l'exécuter en démo !)

---

## 6. Questions fréquentes des clients (FAQ)

### « Peut-on migrer nos données Excel existantes ? »
> Oui, l'application dispose d'une fonction d'import Excel qui traite le fichier et crée automatiquement les bons et mouvements correspondants.

### « Combien de structures peut-on gérer ? »
> Il n'y a pas de limite. Chaque structure (service, district, centre) a son propre espace. L'admin peut voir toutes les structures consolidées.

### « L'application fonctionne-t-elle hors ligne ? »
> L'application nécessite un réseau local (LAN) ou internet. Elle peut être déployée sur un serveur local au sein de votre organisation.

### « Les rapports sont-ils conformes aux modèles officiels ? »
> Oui, les rapports suivent les Modèles 20, 21 et 22 de la comptabilité publique, avec les pages de signature requises.

### « Que se passe-t-il en cas de panne ? »
> La base de données est sauvegardable automatiquement (commande preprod_check). Des backups réguliers sont recommandés.

### « Peut-on personnaliser les en-têtes et le logo ? »
> Oui, depuis l'écran de paramétrage. Chaque structure peut avoir son propre logo, et les en-têtes (pays, ministère, direction) sont configurables.

### « Comment se passe la clôture d'exercice ? »
> Le système vérifie automatiquement les pré-requis (PV remplis, pas de stock négatif), puis reporte les soldes finaux comme Bon N°1 du nouvel exercice.

### « Qui peut voir quoi ? »
> Trois niveaux : **Admin** (tout voir, tout faire), **Comptable** (opérations et rapports), **Consultation** (lecture seule). Chaque utilisateur est affecté à sa structure.

---

## 7. Checklist avant la démo

- [ ] **Serveur lancé** et accessible (`python manage.py runserver`)
- [ ] **Compte admin** fonctionnel avec mot de passe connu
- [ ] **Données de démo** : au moins 5-10 matières, 3-4 bons variés
- [ ] **Logo** uploadé dans les paramètres de la structure de démo
- [ ] **Deux structures** créées pour montrer le multi-structures
- [ ] **Exercice actif** (non clôturé) pour pouvoir créer des bons
- [ ] **PV partiellement rempli** pour montrer le processus d'inventaire
- [ ] **Navigateur** en mode plein écran, zoom 100-110%
- [ ] **Imprimante PDF** disponible pour montrer l'aperçu d'impression
- [ ] **Fichier Excel** prêt pour montrer l'import (optionnel)

---

## 8. Arguments de vente clés

1. **Zéro installation côté client** — fonctionne depuis n'importe quel navigateur
2. **Conformité immédiate** — rapports Modèles 20, 21, 22 prêts à l'emploi
3. **Gain de temps** — calculs automatiques (CMUP, soldes, reports)
4. **Fiabilité** — validation des stocks, audit trail, multi-utilisateurs
5. **Évolutivité** — ajout de structures sans limite, multi-exercice
6. **Sécurité** — authentification, rôles, audit, contrôle des documents
7. **Migration facile** — import des données Excel existantes
8. **Autonomie** — déployable sur serveur local, sans dépendance cloud
