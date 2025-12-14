:Documentation Modèle:MODEL_CARD.md

# 🤖 Fiche Modèle (Model Card)

## 📝 Détails du Modèle

* Nom : Churn Prediction Classifier
* Version : 1.0.0
* Date : Décembre 2025
* Type : Classification Binaire (Apprentissage Supervisé)
* Algorithme : Gradient Boosting (XGBoost / LightGBM)
* Auteur : Artur Agababyan
* Licence : MIT / Propriétaire

# 🎯 Objectif

L'objectif de ce modèle est de prédire si un employé est susceptible de quitter l'entreprise (Churn = 1) ou de rester (Churn = 0) à court/moyen terme.
Il est utilisé par l'équipe RH pour identifier les talents à risque et proposer des actions de rétention préventives.

# 📊 Données d'Entraînement

Le modèle a été entraîné sur un jeu de données historique contenant des informations socio-professionnelles sur les employés.

* Source : Données internes RH (final_data_set.csv).
* Volume : Environ 1400+ entrées.
* Cible (Target) : Atteint_Churn (1 = Départ, 0 = Reste).

### Features utilisées (Variables d'entrée)

Le modèle se base sur 10 variables clés identifiées lors de l'analyse exploratoire :

1. ratio_surcharge_anciennete (Float) : Ratio charge de travail / années.
2. nombre_participation_pee (Int) : Participation au plan d'épargne.
3. departement_consulting (Float/Bool) : Appartenance au département Consulting.
4. age (Int) : Âge de l'employé.
5. poste_consultant (Float/Bool) : Poste occupé.
6. tension_salaire (Float) : Indicateur de satisfaction salariale.
7. statut_marital_marie (Float/Bool) : Situation familiale.
8. annees_dans_l_entreprise (Int) : Ancienneté.
9. satisfaction_globale_moyenne (Float) : Note de satisfaction générale.
10. satisfaction_employee_nature_travail (Int) : Note sur le travail quotidien.

# ⚙️ Traitement et Pipeline

Les données brutes subissent les transformations suivantes avant d'être injectées dans le modèle (gérées par l'API ou le pipeline de pré-traitement) :

* Encodage : One-Hot Encoding pour les variables catégorielles (ex: Statut Marital, Département).
* Sélection : Conservation uniquement des 10 features les plus influentes (Feature Importance).

# 📈 Performances

Le modèle a été évalué sur un jeu de test indépendant (20% du dataset original).

| Métrique | Score Obtenu | Interprétation |
| ---: | :---: | :--- |
| Accuracy | 0.73 | Taux global de bonnes prédictions |
| F1-Score (Classe 1) | 0.51 | Moyenne harmonique entre précision et rappel. Indique la performance globale sur la classe cible (Départ) |
| ROC-AUC | 0.825 | Capacité globale à discriminer les deux classes (1.0 étant parfait) |
| Rappel (Recall) | 0.87 | Capacité à identifier la grande majorité des employés qui vont réellement partir (minimisation des "ratés") |
| Précision (Precision) | 0.36 | Fiabilité des alertes : quand le modèle prédit un départ, il a raison dans 36% des cas (accepte des fausses alertes pour maximiser le rappel) |

# ⚠️ Limitations et Biais

* **Biais historique :** Le modèle reproduit les schémas de départs passés. Si la culture d'entreprise change radicalement, le modèle deviendra obsolète.
* **Compromis Rappel/Précision :** Le modèle privilégie la détection des départs (Rappel élevé) au risque de générer des fausses alertes (Précision faible). Cela nécessite un filtrage humain par les RH.
* **Données manquantes :** Le modèle ne gère pas les valeurs nulles en entrée (l'API renverra une erreur 422).

# 🔄 Protocole de Maintenance

Pour garantir la pérennité du service :

1. **Monitoring :**

    * Toutes les prédictions et les données d'entrée sont stockées dans la table PostgreSQL prediction_logs.
    * Une revue mensuelle compare les prédictions aux départs réels.

2. **Réentraînement (Retraining) :**

    * Fréquence : Trimestrielle ou si le F1-Score descend sous 0.50.
    * Procédure : Lancer le script d'entraînement avec les nouvelles données validées, générer un nouveau .joblib, et mettre à jour via le pipeline CI/CD.

# 🛠️ Exemple d'Utilisation (API)

Le modèle est exposé via une API REST sécurisée.

**Endpoint :** POST /predict

**Payload JSON :**
```json
{
  "ratio_surcharge_anciennete": 0.14,
  "nombre_participation_pee": 0,
  "departement_consulting": 0.0,
  "age": 41,
  "poste_consultant": 0.0,
  "tension_salaire": 0.0003,
  "statut_marital_marie": 0.0,
  "annees_dans_l_entreprise": 2,
  "satisfaction_globale_moyenne": 2.0,
  "satisfaction_employee_nature_travail":
}
```
