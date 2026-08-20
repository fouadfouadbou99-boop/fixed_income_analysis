import streamlit as st
import pandas as pd
import plotly.express as px

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
        classification_counts.columns = ['Classification', 'Nombre d\'Obligations']
        fig_classification = px.pie(classification_counts, values='Nombre d\'Obligations', names='Classification',
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
    st.info("Cette section sera développée pour comparer le portefeuille aux indices du Marché Obligataire International (MBI).")
    # TODO: Intégrer les données des indices MBI et les visualisations comparatives

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
    st.info("Cette section simulera l'impact des variations des taux d'intérêt sur le portefeuille.")
    st.warning("**Implémentation requise :** Logique de calcul de l'impact des variations de taux sur la valeur du portefeuille et ses métriques (sensibilité, duration modifiée, etc.).")
    # TODO: Ajouter des sliders pour les variations de taux et afficher les résultats simulés

with tab5:
    st.header("Suivi Historique")
