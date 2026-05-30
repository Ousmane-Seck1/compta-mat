# 🎬 Script de Démonstration — Pas à Pas

> **Durée estimée : 15-20 minutes**
> **Prérequis : serveur lancé, données de démo, 2 structures créées**

---

## INTRODUCTION (parler, pas montrer)

**Ce que vous dites :**

> « Je vais vous présenter notre application de comptabilité des matières.
> Elle remplace intégralement la gestion sur Excel que vous connaissez,
> avec la fiabilité, la sécurité et la conformité réglementaire en plus.
> Suivons ensemble le parcours d'un comptable au quotidien. »

---

## ÉTAPE 1 — Connexion 🔐

**Action :** Ouvrir le navigateur → `http://127.0.0.1:8000`

**Ce que vous montrez :**
- Page de connexion propre et professionnelle
- Saisir les identifiants admin

**Ce que vous dites :**
> « Chaque utilisateur a son compte sécurisé. Selon son rôle — administrateur,
> comptable ou consultation — il accède à des fonctionnalités différentes. »

---

## ÉTAPE 2 — Menu Principal 🏠

**Action :** Après connexion → Menu Principal

**Ce que vous montrez :**
- La barre de contexte en haut (structure + exercice)
- Les 4 écrans sous forme de cartes
- Le nom de l'utilisateur connecté

**Ce que vous dites :**
> « L'application est organisée en 4 écrans : Administration, Opérations
> comptables, Mouvements internes et Documents. En haut, vous voyez en permanence la structure
> et l'exercice fiscal sélectionnés. »

---

## ÉTAPE 3 — Écran Administration ⚙️

### 3a. Paramètres d'impression

**Action :** Écran 1 → Paramètres

**Ce que vous montrez :**
- Les champs configurables (pays, ministère, structure)
- Le logo uploadé
- Expliquer que ça apparaîtra sur tous les rapports imprimés

**Ce que vous dites :**
> « Chaque structure configure ses propres en-têtes. Le logo, le nom du
> ministère, la direction — tout apparaît automatiquement sur vos rapports
> officiels. »

### 3b. Nomenclature

**Action :** Nomenclature → Montrer la liste

**Ce que vous montrez :**
- La liste des comptes de matières avec codes, noms, unités
- Le bouton "Ajouter" (montrer qu'on peut enrichir le plan comptable)
- La synchronisation automatique vers les structures

**Ce que vous dites :**
> « La nomenclature est le plan comptable des matières. Elle est gérée
> centralement par l'administrateur et se propage automatiquement
> à toutes les structures actives. »

### 3c. Gestion des utilisateurs

**Action :** Gestion utilisateurs → Montrer la liste

**Ce que vous montrez :**
- La liste des utilisateurs avec leurs rôles
- L'attribution d'une structure par défaut

**Ce que vous dites :**
> « L'administrateur crée les comptes, attribue les rôles et assigne
> chaque utilisateur à sa structure. Un comptable ne voit que les données
> de son service. »

---

## ÉTAPE 4 — Tableau de Bord 📊

**Action :** Écran 2 → Tableau de bord

**Ce que vous montrez :**
- Nombre de matières
- Nombre total de bons
- Quantité et valeur du stock
- Alertes éventuelles (stock négatif, PV manquants)

**Ce que vous dites :**
> « Le tableau de bord donne une vue instantanée de la situation comptable :
> combien de matières, combien de mouvements, la valeur totale du stock,
> et les alertes s'il y a des anomalies à corriger. »

---

## ÉTAPE 5 — Créer un Bon d'Entrée ✅ (MOMENT CLÉ)

**Action :** Nouveau bon → Type "Entrée"

**Ce que vous montrez :**
1. Sélectionner le type "Bon d'Entrée"
2. Renseigner la date, la provenance, un commentaire
3. Ajouter une ligne : choisir une matière, quantité, prix unitaire
4. **Montrer que le numéro se génère automatiquement**
5. Soumettre

**Ce que vous dites :**
> « Créer un bon, c'est aussi simple que remplir un formulaire. On choisit
> le type, la matière, la quantité et le prix. Le numéro se génère
> automatiquement. Pas de risque de doublon. »

### 5b. Imprimer le bon

**Action :** Cliquer sur le bon créé → Aperçu → Ctrl+P

**Ce que vous montrez :**
- L'aperçu d'impression avec l'en-tête officiel
- Le format A4 propre, prêt à signer
- Les lignes de signature

**Ce que vous dites :**
> « Et voilà le bon prêt à imprimer. En-tête officiel, numérotation,
> lignes de signature — tout est conforme, sans mise en page manuelle. »

---

## ÉTAPE 6 — Créer un Bon de Sortie 📤

**Action :** Nouveau bon → Type "Sortie définitive"

**Ce que vous montrez :**
1. Sélectionner la même matière
2. Entrer une quantité **inférieure au stock** → ça passe
3. Montrer le CMUP appliqué automatiquement
4. **BONUS** : tenter une quantité **supérieure** au stock → montrer le message d'erreur

**Ce que vous dites :**
> « Pour les sorties, le système vérifie en temps réel que le stock est
> suffisant. Le coût moyen pondéré (CMUP) est calculé automatiquement.
> Impossible de sortir plus que ce qui est disponible. »

---

## ÉTAPE 7 — Livre-Journal 📖

**Action :** Livre-Journal → montrer les 2 mouvements

**Ce que vous montrez :**
- Les 2 lignes (entrée + sortie) en ordre chronologique
- Les filtres par type et par date
- La recherche textuelle

**Ce que vous dites :**
> « Le livre-journal est l'historique complet de tous les mouvements,
> dans l'ordre chronologique. On peut filtrer par type, par date,
> ou rechercher par texte. »

---

## ÉTAPE 8 — Grand Livre 📗

**Action :** Grand Livre → Sélectionner la matière utilisée

**Ce que vous montrez :**
- Le détail des mouvements pour cette matière
- Le solde cumulé qui évolue (entrée, puis sortie)

**Ce que vous dites :**
> « Le grand livre donne l'historique détaillé matière par matière,
> avec le solde cumulé en temps réel. C'est la fiche de stock
> individuelle de chaque article. »

---

## ÉTAPE 9 — Relevé Récapitulatif 📋

**Action :** Relevé Récapitulatif

**Ce que vous montrez :**
- Le tableau synthétique (ouverture, entrées, sorties, solde)
- **Export Excel** → ouvrir le fichier téléchargé
- **Export PDF** → montrer la mise en page officielle

**Ce que vous dites :**
> « Le relevé récapitulatif est la synthèse de l'exercice. Un clic
> pour l'Excel, un clic pour le PDF officiel avec en-tête et signatures.
> C'est le Modèle 20 de la comptabilité publique. »

---

## ÉTAPE 10 — PV de Recensement 📝

**Action :** PV de Recensement

**Ce que vous montrez :**
1. La liste des matières avec leur solde comptable
2. Saisir les quantités physiques (en attente, en service, prêt)
3. Montrer le calcul automatique des **écarts** (en plus / en moins)
4. Marquer comme "PV renseigné"

**Ce que vous dites :**
> « L'inventaire physique se fait directement dans l'application.
> On saisit ce qu'on a compté, et le système calcule automatiquement
> les écarts avec la comptabilité. C'est le cœur du contrôle. »

---

## ÉTAPE 11 — Rapport Final et Régularisations 📊

**Action :** Rapport Final

**Ce que vous montrez :**
- La balance comptable vs inventaire physique
- Les écarts identifiés
- La fonction de **régularisation automatique** (création de bons correctifs)
- L'export PDF (Modèle 22 — Balance Générale)

**Ce que vous dites :**
> « Le rapport final compare la comptabilité à l'inventaire physique.
> S'il y a des écarts, le système peut générer automatiquement les bons
> de régularisation. C'est la Balance Générale — Modèle 22. »

---

## ÉTAPE 12 — Multi-Structures 🏢 (WOW EFFECT)

**Action :** Cliquer sur "Changer" dans la barre de contexte

**Ce que vous montrez :**
1. Le sélecteur de structure avec la liste des services
2. Changer de structure → les données changent instantanément
3. Revenir en admin → **Rapport Central** → tableau de consolidation
4. Les totaux agrégés de toutes les structures

**Ce que vous dites :**
> « C'est l'avantage clé : chaque service travaille dans son espace,
> mais l'administrateur voit la situation consolidée de tous les services
> en un seul tableau. Plus besoin de collecter les fichiers Excel de chacun. »

---

## ÉTAPE 13 — Clôture d'exercice 🔒 (montrer SANS exécuter)

**Action :** Report d'exercice (montrer la page, ne PAS valider)

**Ce que vous montrez :**
- La checklist de pré-clôture (conditions vérifiées automatiquement)
- L'aperçu du Bon N°1 de report
- Expliquer le processus irréversible

**Ce que vous dites :**
> « En fin d'exercice, le système vérifie que tout est en ordre —
> PV remplis, pas de stock négatif — puis reporte automatiquement
> les soldes comme Bon N°1 du nouvel exercice. Fini les reports
> manuels risqués. »

---

## CONCLUSION (1 min)

**Ce que vous dites :**

> « En résumé, cette application vous apporte :
>
> 1. **La conformité** — rapports officiels prêts à l'emploi
> 2. **La fiabilité** — calculs automatiques, validation des stocks
> 3. **La traçabilité** — qui a fait quoi, quand, sur quelle matière
> 4. **La consolidation** — vision centralisée de tous vos services
> 5. **La simplicité** — accessible depuis un navigateur, sans installation
>
> Des questions ? »

---

## 🚨 ASTUCES POUR UNE DÉMO RÉUSSIE

### À FAIRE ✅
- **Préparer les données à l'avance** — ne pas créer en direct ce qui prend du temps
- **Agrandir la taille du texte** du navigateur (Ctrl+= pour zoomer)
- **Utiliser le mode plein écran** (F11) pour plus de visibilité
- **Commenter chaque clic** — ne jamais cliquer en silence
- **Raconter une histoire** — « Imaginons que vous recevez 50 ramettes de papier... »
- **Montrer l'impression** — c'est ce qui impressionne le plus les comptables
- **Montrer les erreurs volontaires** — tenter une sortie > stock pour montrer la sécurité

### À NE PAS FAIRE ❌
- Ne pas exécuter la clôture d'exercice (irréversible)
- Ne pas se perdre dans les paramètres techniques
- Ne pas montrer l'admin Django (trop technique)
- Ne pas parler de code ou de base de données
- Ne pas passer plus de 2 min sur un écran sans passer au suivant
