import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Configuration de la page Streamlit ---
st.set_page_config(layout="wide", page_title="Analyse de Portefeuille Obligataire")

# --- Chargement des données ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Erreur : Le fichier {file_path} n'a pas été trouvé. Assurez-vous qu'il est dans le répertoire correct.")
        return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier Excel : {e}")
        return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur

excel_file = 'Data_obligations_cleaned.xlsx'
df = load_data(excel_file)

# --- Génération de données synthétiques pour le benchmarking ---
# Ces données sont des exemples pour illustrer la fonctionnalité.
dates = pd.date_range(start='2022-01-01', periods=24, freq='M')
mbi_index_values = 100 + np.cumsum(np.random.randn(24) * 0.5)
portfolio_benchmark_values = 100 + np.cumsum(np.random.randn(24) * 0.6 + 0.1) # légèrement en croissance
df_benchmark = pd.DataFrame({
    'Date': dates,
    'MBI Index': mbi_index_values,
    'Performance Portefeuille': portfolio_benchmark_values
})
# Assurez-vous que la colonne Date est de type datetime pour Plotly
df_benchmark['Date'] = pd.to_datetime(df_benchmark['Date'])

# --- Génération de données synthétiques pour le Suivi Historique ---
# Ces données sont des exemples pour illustrer la fonctionnalité.
dates_history = pd.date_range(start='2021-01-01', periods=36, freq='M')
tra_moyen_history = 0.03 + np.cumsum(np.random.randn(36) * 0.001)
duration_moyenne_history = 5 + np.cumsum(np.random.randn(36) * 0.1)

df_historical_metrics = pd.DataFrame({
    'Date': dates_history,
    'TRA Moyen Historique': tra_moyen_history,
    'Duration Moyenne Historique': duration_moyenne_history
})
df_historical_metrics['Date'] = pd.to_datetime(df_historical_metrics['Date'])


# --- Titre de l'application ---
st.title("📈 Analyse de Portefeuille Obligataire")
st.markdown("Une application pour l'analyse, le suivi et la gestion automatisée d'un portefeuille obligataire.")

# --- Sidebar pour les filtres globaux ---
st.sidebar.header("Filtres Globaux")

# Exemple de filtre: Sélection de la classification
selected_classification = st.sidebar.multiselect(
    "Filtrer par Classification",
    options=df['Classification'].unique() if not df.empty else [], # Handle empty DataFrame
    default=df['Classification'].unique() if not df.empty else [] # Handle empty DataFrame
)

filtered_df = df[df['Classification'].isin(selected_classification)] if not df.empty else pd.DataFrame()

st.sidebar.markdown("--- ")
st.sidebar.subheader("Options d'Analyse")
# Future functionality toggles can go here

# --- Onglets pour l'organisation de l'application ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💸 Tableau de Bord Exécutif",
    "📊 Benchmarking (Indices MBI)",
    "📉 Analyse de Concentration",
    "💵 Stress Test (Taux d'intérêt)",
    "🔍 Suivi Historique"
])

with tab1:
    st.header("Tableau de Bord Exécutif")
    if not filtered_df.empty:
        # Exemples de KPI
        total_nominal_global_restant = filtered_df['Nominal Global Restant '].sum()
        nombre_obligations = filtered_df.shape[0]
        avg_duration = filtered_df['Duration'].mean()
        avg_tra = filtered_df['TRA'].mean()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Nominal Global Restant Total", value=f"{total_nominal_global_restant:,.2f} MAD")
        with col2:
            st.metric(label="Nombre d'Obligations", value=f"{nombre_obligations}")
        with col3:
            st.metric(label="Duration Moyenne", value=f"{avg_duration:.2f} ans")
        with col4:
            st.metric(label="TRA Moyen", value=f"{avg_tra:.2%}")

        st.markdown("### Visualisations Clés")
        # Exemple: Distribution par classification
        classification_counts = filtered_df['Classification'].value_counts().reset_index()
        classification_counts.columns = ['Classification', 'Nombre d'Obligations']
        fig_classification = px.pie(classification_counts, values='Nombre d'Obligations', names='Classification',
                                      title='Distribution des Obligations par Classification')
        st.plotly_chart(fig_classification, use_container_width=True)

        # Exemple: Nominal Global Restant par Classification
        nominal_by_classification = filtered_df.groupby('Classification')['Nominal Global Restant '].sum().reset_index()
        fig_nominal_classification = px.bar(nominal_by_classification, x='Classification', y='Nominal Global Restant ',
                                               title='Nominal Global Restant par Classification')
        st.plotly_chart(fig_nominal_classification, use_container_width=True)

    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")

with tab2:
    st.header("Benchmarking (Indices MBI)")
    st.info("Cette section compare la performance du portefeuille aux indices du Marché Obligataire International (MBI) à l'aide de données synthétiques.")

    st.markdown("### Performance du Portefeuille vs. Indice MBI (Données Synthétiques)")
    fig_benchmark = px.line(df_benchmark, x='Date', y=['MBI Index', 'Performance Portefeuille'],
                            title='Comparaison de la Performance',
                            labels={'value': 'Valeur de l'Indice', 'variable': 'Série'})
    st.plotly_chart(fig_benchmark, use_container_width=True)

with tab3:
    st.header("Analyse de Concentration")
    st.info("Cette section analysera la concentration du portefeuille par émetteur, secteur, etc.")
    if not filtered_df.empty:
        st.markdown("### Concentration par Type de Périodicité Coupon")
        concentration_pc = filtered_df['Périodicité Coupon'].value_counts(normalize=True).reset_index()
        concentration_pc.columns = ['Périodicité Coupon', 'Proportion']
        fig_concentration = px.bar(concentration_pc, x='Périodicité Coupon', y='Proportion',
                                   title='Concentration par Périodicité Coupon', labels={'Proportion': 'Proportion du Portefeuille'})
        st.plotly_chart(fig_concentration, use_container_width=True)
    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés pour l'analyse de concentration.")

with tab4:
    st.header("Stress Test (Taux d'intérêt)")
    st.info("Cette section simule l'impact des variations des taux d'intérêt sur le portefeuille.")

    if not filtered_df.empty:
        st.markdown("### Paramètres du Stress Test")
        col_stress1, col_stress2 = st.columns(2)
        with col_stress1:
            # Slider pour la variation des taux d'intérêt (en points de base)
            rate_change_bp = st.slider(
                "Variation des taux d'intérêt (en points de base)",
                min_value=-100,
                max_value=100,
                value=0,
                step=5
            )
            # Convertir les points de base en pourcentage
            rate_change_pct = rate_change_bp / 10000.0

        with col_stress2:
            st.metric(label="Variation de taux appliquée", value=f"{rate_change_bp} bps ({rate_change_pct:.2%})")

        st.markdown("### Résultats Simulé")
        # Calcul simple de l'impact sur le prix (approximation avec la sensibilité)
        # Nouvelle colonne pour le prix simulé
        if 'Prix Unitaire' in filtered_df.columns and 'Sensibilité' in filtered_df.columns:
            filtered_df['Prix Unitaire Simulé'] = filtered_df['Prix Unitaire'] * (1 - filtered_df['Sensibilité'] * rate_change_pct)
            st.write("**Impact sur le Prix Unitaire :**")
            st.dataframe(filtered_df[['Code', 'Prix Unitaire', 'Prix Unitaire Simulé', 'Sensibilité']].head())

            # Calcul de la nouvelle duration (simplifié pour l'exemple)
            # Supposons que la duration change proportionnellement ou de manière plus complexe
            # Pour cet exemple, nous allons simplement ajuster un peu la duration existante
            if 'Duration' in filtered_df.columns:
                filtered_df['Duration Simulée'] = filtered_df['Duration'] * (1 + rate_change_pct * 5) # Facteur arbitraire pour montrer un changement
                st.write("**Impact sur la Duration :**")
                st.dataframe(filtered_df[['Code', 'Duration', 'Duration Simulée']].head())
        else:
            st.warning("Les colonnes 'Prix Unitaire' ou 'Sensibilité' nécessaires aux calculs ne sont pas disponibles dans les données filtrées.")

        st.info("**Note :** Les calculs ci-dessus sont des approximations simplifiées pour illustrer la fonctionnalité. Une implémentation complète nécessiterait des modèles de valorisation obligataire plus sophistiqués.")
    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés pour le stress test.")

with tab5:
    st.header("Suivi Historique")
    st.info("Cette section permet de suivre l'évolution des métriques clés du portefeuille sur des périodes définies, à l'aide de données synthétiques.")

    st.markdown("### Évolution Historique du TRA Moyen (Données Synthétiques)")
    fig_tra_history = px.line(df_historical_metrics, x='Date', y='TRA Moyen Historique',
                              title='Évolution du TRA Moyen',
                              labels={'TRA Moyen Historique': 'TRA Moyen'})
    st.plotly_chart(fig_tra_history, use_container_width=True)

    st.markdown("### Évolution Historique de la Duration Moyenne (Données Synthétiques)")
    fig_duration_history = px.line(df_historical_metrics, x='Date', y='Duration Moyenne Historique',
                                   title='Évolution de la Duration Moyenne',
                                   labels={'Duration Moyenne Historique': 'Duration Moyenne'})
    st.plotly_chart(fig_duration_history, use_container_width=True)
