import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Analyse Portefeuille Obligataire",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# CHARGEMENT DATA
# ==========================================================

@st.cache_data
def load_data(path):

    try:

        df = pd.read_excel(path)

        # nettoyage colonnes
        df.columns = df.columns.str.strip()

        return df

    except Exception as e:

        st.error(f"Erreur chargement Excel : {e}")

        return pd.DataFrame()


# ==========================================================
# BENCHMARK SYNTHETIQUE
# ==========================================================

@st.cache_data
def generate_benchmark():

    np.random.seed(42)

    dates = pd.date_range(
        start="2022-01-31",
        periods=24,
        freq="ME"
    )

    return pd.DataFrame({
        "Date": dates,
        "MBI Index":
            100 + np.cumsum(
                np.random.normal(0.15, 0.40, 24)
            ),
        "Performance Portefeuille":
            100 + np.cumsum(
                np.random.normal(0.20, 0.50, 24)
            )
    })


# ==========================================================
# HISTORIQUE SYNTHETIQUE
# ==========================================================

@st.cache_data
def generate_history():

    np.random.seed(7)

    dates = pd.date_range(
        start="2021-01-31",
        periods=36,
        freq="ME"
    )

    return pd.DataFrame({
        "Date": dates,
        "TRA Moyen":
            0.03 + np.cumsum(
                np.random.normal(0, 0.0004, 36)
            ),
        "Duration Moyenne":
            5 + np.cumsum(
                np.random.normal(0, 0.05, 36)
            )
    })


# ==========================================================
# CHARGEMENT
# ==========================================================

df = load_data("Data_obligations_cleaned.xlsx")

df_benchmark = generate_benchmark()

df_history = generate_history()

# ==========================================================
# CONTROLE
# ==========================================================

required_columns = [
    "Classification",
    "Nominal Global Restant",
    "Duration",
    "TRA"
]

if not df.empty:

    missing = [
        c for c in required_columns
        if c not in df.columns
    ]

    if missing:

        st.error(
            f"Colonnes manquantes : {missing}"
        )

        st.stop()

# ==========================================================
# TITRE
# ==========================================================

st.title("📈 Analyse de Portefeuille Obligataire")

st.markdown(
    "Suivi, pilotage et stress testing du portefeuille."
)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("Filtres")

if not df.empty:

    classifications = sorted(
        df["Classification"]
        .dropna()
        .unique()
    )

    selected = st.sidebar.multiselect(
        "Classification",
        classifications,
        default=classifications
    )

    filtered_df = df[
        df["Classification"]
        .isin(selected)
    ].copy()

else:

    filtered_df = pd.DataFrame()

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💸 Dashboard",
    "📊 Benchmark",
    "📉 Concentration",
    "💵 Stress Test",
    "📅 Historique"
])

# ==========================================================
# DASHBOARD
# ==========================================================

with tab1:

    st.header("Tableau de Bord")

    if not filtered_df.empty:

        total_nominal = (
            filtered_df["Nominal Global Restant"]
            .sum()
        )

        avg_duration = (
            filtered_df["Duration"]
            .mean()
        )

        avg_tra = (
            filtered_df["TRA"]
            .mean()
        )

        nb_titres = len(filtered_df)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Nominal Total",
            f"{total_nominal:,.0f} MAD"
        )

        c2.metric(
            "Nombre de titres",
            nb_titres
        )

        c3.metric(
            "Duration Moyenne",
            f"{avg_duration:.2f}"
        )

        c4.metric(
            "TRA Moyen",
            f"{avg_tra:.2%}"
        )

        col1, col2 = st.columns(2)

        with col1:

            pie_data = (
                filtered_df["Classification"]
                .value_counts()
                .reset_index()
            )

            pie_data.columns = [
                "Classification",
                "Nombre"
            ]

            fig1 = px.pie(
                pie_data,
                names="Classification",
                values="Nombre",
                title="Répartition Classification"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True,
                key="pie_classification"
            )

        with col2:

            bar_data = (
                filtered_df.groupby(
                    "Classification"
                )["Nominal Global Restant"]
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                bar_data,
                x="Classification",
                y="Nominal Global Restant",
                title="Nominal par Classification"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True,
                key="bar_nominal"
            )

# ==========================================================
# BENCHMARK
# ==========================================================

with tab2:

    st.header("Benchmarking")

    fig_benchmark = px.line(
        df_benchmark,
        x="Date",
        y=[
            "MBI Index",
            "Performance Portefeuille"
        ]
    )

    st.plotly_chart(
        fig_benchmark,
        use_container_width=True,
        key="benchmark"
    )

# ==========================================================
# CONCENTRATION
# ==========================================================

with tab3:

    st.header("Analyse de Concentration")

    if (
        "Périodicité Coupon"
        in filtered_df.columns
    ):

        concentration = (
            filtered_df[
                "Périodicité Coupon"
            ]
            .value_counts(normalize=True)
            .reset_index()
        )

        concentration.columns = [
            "Périodicité Coupon",
            "Poids"
        ]

        fig3 = px.bar(
            concentration,
            x="Périodicité Coupon",
            y="Poids"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True,
            key="concentration_coupon"
        )

# ==========================================================
# STRESS TEST
# ==========================================================

with tab4:

    st.header("Stress Test")

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
            "Choc appliqué",
            f"{shock_bp} bps"
        )

        if (
            "Prix Unitaire" in filtered_df.columns
            and "Sensibilité" in filtered_df.columns
        ):

            scenario_df = filtered_df.copy()

            scenario_df["Prix Simulé"] = (
                scenario_df["Prix Unitaire"]
                *
                (
                    1
                    - scenario_df["Sensibilité"]
                    * shock
                )
            )

            cols = [
                c
                for c in [
                    "Code",
                    "Prix Unitaire",
                    "Prix Simulé",
                    "Sensibilité"
                ]
                if c in scenario_df.columns
            ]

            st.dataframe(
                scenario_df[cols],
                use_container_width=True
            )

            impact = (
                scenario_df["Prix Simulé"].sum()
                -
                scenario_df["Prix Unitaire"].sum()
            )

            st.metric(
                "Impact estimé",
                f"{impact:,.2f}"
            )

# ==========================================================
# HISTORIQUE
# ==========================================================

with tab5:

    st.header("Historique")

    fig_tra = px.line(
        df_history,
        x="Date",
        y="TRA Moyen"
    )

    st.plotly_chart(
        fig_tra,
        use_container_width=True,
        key="history_tra"
    )

    fig_duration = px.line(
        df_history,
        x="Date",
        y="Duration Moyenne"
    )

    st.plotly_chart(
        fig_duration,
        use_container_width=True,
        key="history_duration"
    )

# ==========================================================
# DONNEES DETAILLEES
# ==========================================================

st.divider()

with st.expander(
    "Afficher les données détaillées"
):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
