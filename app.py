import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================================
# CONFIGURATION PAGE
# ==========================================================

st.set_page_config(
    page_title="Analyse de Portefeuille Obligataire",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# CHARGEMENT DES DONNEES
# ==========================================================

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)

        # Nettoyage des noms de colonnes
        df.columns = df.columns.str.strip()

        return df

    except FileNotFoundError:
        st.error(f"Fichier introuvable : {file_path}")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return pd.DataFrame()


excel_file = "Data_obligations_cleaned.xlsx"
df = load_data(excel_file)

# ==========================================================
# CONTROLES DE COHERENCE
# ==========================================================

required_columns = [
    "Classification",
    "Nominal Global Restant",
    "Duration",
    "TRA"
]

if not df.empty:

    missing_cols = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_cols:
        st.error(
            f"Colonnes manquantes dans le fichier Excel : {missing_cols}"
        )
        st.stop()

# ==========================================================
# DONNEES SYNTHETIQUES BENCHMARK
# ==========================================================

dates = pd.date_range(
    start="2022-01-31",
    periods=24,
    freq="ME"
)

np.random.seed(42)

df_benchmark = pd.DataFrame({
    "Date": dates,
    "MBI Index":
        100 + np.cumsum(np.random.normal(0.15, 0.4, 24)),
    "Performance Portefeuille":
        100 + np.cumsum(np.random.normal(0.20, 0.50, 24))
})

# ==========================================================
# DONNEES HISTORIQUES SYNTHETIQUES
# ==========================================================

dates_history = pd.date_range(
    start="2021-01-31",
    periods=36,
    freq="ME"
)

df_history = pd.DataFrame({
    "Date": dates_history,
    "TRA Moyen":
        0.03 + np.cumsum(np.random.normal(0, 0.0005, 36)),
    "Duration Moyenne":
        5 + np.cumsum(np.random.normal(0, 0.05, 36))
})

# ==========================================================
# TITRE
# ==========================================================

st.title("📈 Analyse de Portefeuille Obligataire")

st.markdown(
    """
    Plateforme de suivi, visualisation et stress testing
    d'un portefeuille obligataire.
    """
)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("Filtres")

if not df.empty:

    classifications = sorted(
        df["Classification"].dropna().unique()
    )

    selected_classifications = st.sidebar.multiselect(
        "Classification",
        classifications,
        default=classifications
    )

    filtered_df = df[
        df["Classification"].isin(
            selected_classifications
        )
    ].copy()

else:
    filtered_df = pd.DataFrame()

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💸 Tableau de bord",
    "📊 Benchmarking",
    "📉 Concentration",
    "💵 Stress Test",
    "📅 Historique"
])

# ==========================================================
# TAB 1 : DASHBOARD EXECUTIF
# ==========================================================

with tab1:

    st.header("Tableau de Bord Exécutif")

    if not filtered_df.empty:

        total_nominal = filtered_df[
            "Nominal Global Restant"
        ].sum()

        nb_lignes = len(filtered_df)

        duration_moyenne = filtered_df[
            "Duration"
        ].mean()

        tra_moyen = filtered_df[
            "TRA"
        ].mean()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Nominal Global",
            f"{total_nominal:,.0f} MAD"
        )

        col2.metric(
            "Nombre de lignes",
            f"{nb_lignes}"
        )

        col3.metric(
            "Duration moyenne",
            f"{duration_moyenne:.2f} ans"
        )

        col4.metric(
            "TRA moyen",
            f"{tra_moyen:.2%}"
        )

        st.divider()

        colA, colB = st.columns(2)

        with colA:

            repartition = (
                filtered_df["Classification"]
                .value_counts()
                .reset_index()
            )

            repartition.columns = [
                "Classification",
                "Nombre"
            ]

            fig = px.pie(
                repartition,
                names="Classification",
                values="Nombre",
                title="Répartition par Classification"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with colB:

            nominal_class = (
                filtered_df
                .groupby("Classification")
                ["Nominal Global Restant"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                nominal_class,
                x="Classification",
                y="Nominal Global Restant",
                title="Nominal par Classification"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.warning("Aucune donnée disponible.")

# ==========================================================
# TAB 2 : BENCHMARK
# ==========================================================

with tab2:

    st.header("Benchmarking")

    fig = px.line(
        df_benchmark,
        x="Date",
        y=[
            "MBI Index",
            "Performance Portefeuille"
        ],
        title="Portefeuille vs MBI",
        labels={
            "value": "Niveau d'indice",
            "variable": "Série"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# TAB 3 : CONCENTRATION
# ==========================================================

with tab3:

    st.header("Analyse de Concentration")

    if (
        not filtered_df.empty
        and "Périodicité Coupon" in filtered_df.columns
    ):

        concentration = (
            filtered_df["Périodicité Coupon"]
            .value_counts(normalize=True)
            .reset_index()
        )

        concentration.columns = [
            "Périodicité Coupon",
            "Poids"
        ]

        fig = px.bar(
            concentration,
            x="Périodicité Coupon",
            y="Poids",
            title="Concentration des Coupons"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning(
            "Colonne Périodicité Coupon indisponible."
        )

# ==========================================================
# TAB 4 : STRESS TEST
# ==========================================================

with tab4:

    st.header("Stress Testing de Taux")

    if not filtered_df.empty:

        shock_bp = st.slider(
            "Choc de taux (bps)",
            -300,
            300,
            0,
            25
        )

        shock = shock_bp / 10000

        st.metric(
            "Variation appliquée",
            f"{shock_bp} bps"
        )

        if (
            "Prix Unitaire" in filtered_df.columns
            and "Sensibilité" in filtered_df.columns
        ):

            scenario_df = filtered_df.copy()

            scenario_df["Prix Simulé"] = (
                scenario_df["Prix Unitaire"]
                * (
                    1
                    - scenario_df["Sensibilité"]
                    * shock
                )
            )

            st.dataframe(
                scenario_df[
                    [
                        "Code",
                        "Prix Unitaire",
                        "Prix Simulé",
                        "Sensibilité"
                    ]
                ]
            )

            impact = (
                scenario_df["Prix Simulé"].sum()
                - scenario_df["Prix Unitaire"].sum()
            )

            st.metric(
                "Impact estimé",
                f"{impact:,.2f}"
            )

        else:
            st.warning(
                "Colonnes Prix Unitaire ou Sensibilité manquantes."
            )

# ==========================================================
# TAB 5 : HISTORIQUE
# ==========================================================

with tab5:

    st.header("Suivi Historique")

    fig1 = px.line(
        df_history,
        x="Date",
        y="TRA Moyen",
        title="Evolution du TRA Moyen"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    fig2 = px.line(
        df_history,
        x="Date",
        y="Duration Moyenne",
        title="Evolution de la Duration Moyenne"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ==========================================================
# DONNEES DETAILLEES
# ==========================================================

st.divider()

with st.expander("Afficher les données détaillées"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
