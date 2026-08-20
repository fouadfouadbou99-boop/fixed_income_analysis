# Application d'Analyse de Portefeuille Obligataire avec Streamlit

Cette application web interactive, développée avec Streamlit, permet l'analyse, le suivi, l'évaluation et la gestion automatisée d'un portefeuille obligataire. Elle est conçue pour fournir un aperçu rapide de la composition du portefeuille, des analyses de concentration, et des outils pour évaluer la sensibilité aux changements du marché.

## Fonctionnalités

*   **Tableau de Bord Exécutif** : Vue d'ensemble des métriques clés du portefeuille (Nominal Global Restant, Nombre d'Obligations, Duration Moyenne, TRA Moyen).
*   **Benchmarking (Indices MBI)** : (À implémenter) Comparaison de la performance du portefeuille avec des indices de référence.
*   **Analyse de Concentration** : Visualisation de la répartition du portefeuille par différents critères (e.g., classification, périodicité coupon).
*   **Stress Test (Taux d'intérêt)** : (À implémenter) Simulation de l'impact des variations de taux d'intérêt.
*   **Suivi Historique** : (À implémenter) Visualisation des tendances et de l'évolution du portefeuille au fil du temps.

## Données

L'application utilise un fichier Excel (`Data_obligations_cleaned.xlsx`) comme source de données. Ce fichier doit être placé dans le même répertoire que le script `app.py`.

## Comment l'utiliser (Localement)

Pour exécuter cette application sur votre machine locale, suivez les étapes ci-dessous :

1.  **Cloner le dépôt GitHub** :
    ```bash
    git clone <URL_DU_VOTRE_DEPOT>
    cd <NOM_DU_REPERTOIRE>
    ```

2.  **Créer un environnement virtuel (recommandé)** :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Placer le fichier de données** :
    Assurez-vous que le fichier `Data_obligations_cleaned.xlsx` est bien présent dans le répertoire racine du projet.

5.  **Exécuter l'application Streamlit** :
    ```bash
    streamlit run app.py
    ```

    L'application s'ouvrira automatiquement dans votre navigateur web par défaut.

## Déploiement sur Streamlit Community Cloud

1.  **Assurez-vous que votre dépôt GitHub contient** :
    *   `app.py`
    *   `requirements.txt`
    *   `Data_obligations_cleaned.xlsx` (ou assurez-vous qu'il est accessible via un autre moyen si trop volumineux ou sensible).

2.  **Connectez-vous à Streamlit Community Cloud** et déployez votre application en pointant vers votre dépôt GitHub.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou à soumettre des pull requests pour améliorer l'application.

