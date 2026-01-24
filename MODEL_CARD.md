:Documentation Modèle:MODEL_CARD.md


# 🤖 Fiche Modèle (Model Card)

## 📝 Détails du Modèle

* **Nom** : Churn Prediction Classifier (Light Version)
* **Version** : 2.0.0
* **Date** : Janvier 2026
* **Type** : Classification Binaire (Apprentissage Supervisé)
* **Algorithme** : RandomForestClassifier (Ensemble Learning) avec SMOTE
* **Fichier** : `model/modele_churn_light.pkl`
* **Auteur** : Artur Agababyan
* **Licence** : MIT / Propriétaire

## 🎯 Objectif

L'objectif de ce modèle est de prédire si un employé est susceptible de quitter l'entreprise à court/moyen terme. Il est utilisé par l'équipe RH pour identifier les talents à risque et proposer des actions de rétention préventives.

Le modèle privilégie le **Recall** (capacité à détecter les départs) au détriment de la Précision, suivant le principe *"mieux vaut prévenir que guérir"*.

## 📊 Données d'Entraînement

Le modèle a été entraîné sur un jeu de données historique contenant des informations socio-professionnelles sur les employés.

* **Source** : Données internes RH (`final_data_set.csv`)
* **Volume** : 1470 entrées
* **Cible (Target)** : `a_quitte_l_entreprise_num` (1 = Départ, 0 = Reste)
* **Déséquilibre** : Classe minoritaire (départs) sur-échantillonnée avec SMOTE

### Features Utilisées (10 Variables Sélectionnées)

Le modèle utilise **uniquement 10 features** optimisées pour maximiser la performance tout en limitant la complexité :

| # | Nom de la Feature | Type | Description |
|---|-------------------|------|-------------|
| 1 | `ratio_surcharge_anciennete` | Float | Ratio charge de travail / années d'ancienneté |
| 2 | `nombre_participation_pee` | Integer | Nombre de participations au Plan d'Épargne Entreprise |
| 3 | `statut_marital_divorce` | Float (0/1) | 1.0 si divorcé(e), 0.0 sinon |
| 4 | `age` | Integer | Âge de l'employé (18-100 ans) |
| 5 | `annees_dans_l_entreprise` | Integer | Nombre d'années dans l'entreprise |
| 6 | `frequence_deplacement_frequent` | Float (0/1) | 1.0 si déplacements professionnels fréquents |
| 7 | `poste_representant_commercial` | Float (0/1) | 1.0 si Représentant Commercial |
| 8 | `niveau_education` | Integer (1-5) | Niveau d'éducation (1=Bac, 5=Doctorat) |
| 9 | `domaine_etude_marketing` | Float (0/1) | 1.0 si domaine d'étude = Marketing |
| 10 | `poste_consultant` | Float (0/1) | 1.0 si poste = Consultant |

> **Note** : Les variables catégorielles ont été encodées en One-Hot Encoding pendant la phase d'entraînement. L'API accepte les valeurs binaires (0.0 ou 1.0).

## ⚙️ Pipeline de Traitement

Le modèle suit ce pipeline :

1. **Sur-échantillonnage** : SMOTE pour équilibrer les classes (minorité = départs)
2. **Classification** : RandomForestClassifier avec :
   - `n_estimators` : 100 arbres
   - `max_depth` : 10 (limite la profondeur pour éviter l'overfitting)
   - `class_weight` : 'balanced'
   - `random_state` : 42 (reproductibilité)

3. **Seuil Personnalisé** : 0.235 (vs 0.5 par défaut)
   - Si `probability >= 0.235` → Prédiction = 1 (Churn)
   - Sinon → Prédiction = 0 (Reste)

## 📈 Performances

Le modèle a été évalué sur un jeu de validation indépendant (20% du dataset, stratifié).

| Métrique | Score | Interprétation |
|----------|-------|----------------|
| **ROC-AUC** | 0.806 | Bonne capacité à distinguer les profils à risque |
| **Recall** | **76.60%** | **Priorité métier** : Détection de 3 départs sur 4 |
| **Precision** | 31.30% | Compromis accepté : environ 7 fausses alertes pour 3 vrais départs détectés |
| **F1-Score** | 0.44 | Impacté par le déséquilibre et le choix de favoriser le Recall |

### Matrice de Confusion (Validation)

|                | Prédiction : Reste | Prédiction : Départ |
|----------------|-------------------|---------------------|
| **Réalité : Reste** | Vrai Négatif | Faux Positif (fausses alertes) |
| **Réalité : Départ** | Faux Négatif : **11** | Vrai Positif : **36** |

**Taux de détection** : 36 / (36 + 11) = **76.6%** des départs sont anticipés.

## ⚠️ Limitations et Biais

### 1. Compromis Recall vs Précision

**Contexte** : Le modèle génère des fausses alertes (précision = 31%).

**Impact métier** :
- Sur 10 employés signalés, ~3 partiront réellement
- Les RH doivent analyser les dossiers suggérés par le modèle
- **Justification** : Le coût d'une vérification inutile < le coût d'un talent perdu non détecté

### 2. Biais Historique

Le modèle apprend des **départs passés** uniquement. Si les raisons de départ changent (nouvelle politique RH, crise externe, etc.), les prédictions peuvent perdre en pertinence.

**Recommandation** : Monitoring trimestriel des performances (voir section Maintenance).

### 3. Gestion des Données Manquantes

Le modèle **ne gère pas les valeurs nulles/manquantes**. L'API renvoie une erreur de validation (HTTP 422) si un champ est absent.

**Recommandation** : Pré-traiter les données avant l'appel API (imputation ou valeur par défaut).

### 4. Biais de Sélection des Features

Les 10 features ont été sélectionnées via analyse d'importance. D'autres variables (non incluses) pourraient avoir un impact à l'avenir.

## 🔄 Protocole de Maintenance

### 1. Monitoring Continu

**Mécanisme** :
- Toutes les prédictions sont enregistrées dans `prediction_logs` (timestamp, inputs, prédiction, probabilité)
- Permet de calculer rétrospectivement les vraies performances

**Actions recommandées** :
- **Mensuel** : Vérifier le nombre de prédictions et la distribution des probabilités
- **Trimestriel** : Comparer les prédictions (J-90) avec les départs réels → calcul du Recall en production

### 2. Déclencheurs de Réentraînement

Réentraîner le modèle SI :
- **Recall en production < 70%** (seuil critique)
- **Changement significatif de politique RH** (télétravail, salaires, etc.)
- **Accumulation de 300+ nouveaux cas** avec ground truth

### 3. Détection de Data Drift

Surveiller les distributions des features :
- Si écart > 2 écarts-types sur 3+ features → Investigation nécessaire
- Utiliser des tests statistiques (Kolmogorov-Smirnov, Chi-2)

## 🛠️ Utilisation via l'API

### Endpoint de Prédiction

**URL** : `POST /predict`

**Payload JSON** :

```json
{
  "ratio_surcharge_anciennete": 0.14,
  "nombre_participation_pee": 0,
  "statut_marital_divorce": 0.0,
  "age": 41,
  "annees_dans_l_entreprise": 2,
  "frequence_deplacement_frequent": 1.0,
  "poste_representant_commercial": 0.0,
  "niveau_education": 3,
  "domaine_etude_marketing": 0.0,
  "poste_consultant": 1.0
}
```
