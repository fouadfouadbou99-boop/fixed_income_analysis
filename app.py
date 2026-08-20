import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Portefeuille Obligataire",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Plateforme d'Analyse du Portefeuille Obligataire")

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("Portefeuille Obligataire")

uploaded_file = st.sidebar.file_uploader(
    "Charger le portefeuille",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Veuillez charger le fichier Excel du portefeuille.")
    st.stop()

# ==========================================================
# CHARGEMENT DES DONNEES
# ==========================================================

try:

    df = pd.read_excel(uploaded_file)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
    )

except Exception as e:

    st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
    st.stop()

# ==========================================================
# CONTROLE DES COLONNES
# ==========================================================

required_columns = [
    "Description Titres",
    "Prix Global",
    "Duration",
    "Sensibilité",
    "TRA",
    "Taux facial",
    "Segments",
    "Classification"
]

missing = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(
        f"Colonnes manquantes : {missing}"
    )
    st.stop()

# ==========================================================
# KPI EXECUTIFS
# ==========================================================

encours = df["Prix Global"].sum()

duration_mp = (
    (
        df["Duration"]
        * df["Prix Global"]
    ).sum()
    / encours
)

sensibilite_mp = (
    (
        df["Sensibilité"]
        * df["Prix Global"]
    ).sum()
    / encours
)

tra_mp = (
    (
        df["TRA"]
        * df["Prix Global"]
    ).sum()
    / encours
)

coupon_mp = (
    (
        df["Taux facial"]
        * df["Prix Global"]
    ).sum()
    / encours
)

st.subheader("Tableau de bord exécutif")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Encours",
    f"{encours/1e9:,.2f} MMDH"
)

col2.metric(
    "Durée",
    f"{duration_mp:.2f}"
)

col3.metric(
    "Sensibilité",
    f"{sensibilite_mp:.2f}"
)

col4.metric(
    "TRA",
    f"{tra_mp:.2%}"
)

col5.metric(
    "Coupon",
    f"{coupon_mp:.2%}"
)

st.divider()

# ==========================================================
# REPARTITION PAR SEGMENT
# ==========================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Répartition par Segment")

    segment = (
        df.groupby("Segments")
        ["Prix Global"]
        .sum()
        .reset_index()
    )

    fig_segment = px.pie(
        segment,
        names="Segments",
        values="Prix Global",
        hole=0.4
    )

    st.plotly_chart(
        fig_segment,
        use_container_width=True
    )

with col2:

    st.subheader("Répartition par Classification")

    classification = (
        df.groupby("Classification")
        ["Prix Global"]
        .sum()
        .reset_index()
    )

    fig_class = px.bar(
        classification,
        x="Classification",
        y="Prix Global",
        color="Classification"
    )

    st.plotly_chart(
        fig_class,
        use_container_width=True
    )

st.divider()

# ==========================================================
# TOP 10 POSITIONS
# ==========================================================

st.subheader("Top 10 Positions")

top10 = (
    df.sort_values(
        "Prix Global",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    top10[
        [
            "Description Titres",
            "Prix Global",
            "Duration",
            "Sensibilité",
            "TRA",
            "Segments"
        ]
    ],
    use_container_width=True
)

# ==========================================================
# CONCENTRATION
# ==========================================================

st.subheader("Analyse de Concentration")

concentration = top10.copy()

concentration["Poids %"] = (
    concentration["Prix Global"]
    /
    encours
    * 100
)

st.dataframe(
    concentration[
        [
            "Description Titres",
            "Prix Global",
            "Poids %"
        ]
    ],
    use_container_width=True
)

# ==========================================================
# STRESS TEST
# ==========================================================

st.subheader("Stress Test de Taux")

shocks = [
    -200,
    -150,
    -100,
    -50,
    50,
    100,
    150,
    200
]

impacts = []

for shock in shocks:

    impact = (
        - sensibilite_mp
        * encours
        * (shock / 10000)
    )

    impacts.append(impact)

stress = pd.DataFrame(
    {
        "Choc (pb)": shocks,
        "Impact (MAD)": impacts
    }
)

fig_stress = px.line(
    stress,
    x="Choc (pb)",
    y="Impact (MAD)",
    markers=True
)

st.plotly_chart(
    fig_stress,
    use_container_width=True
)

st.dataframe(
    stress,
    use_container_width=True
)

st.divider()

# ==========================================================
# APERCU DETAILLE DU PORTEFEUILLE
# ==========================================================

st.subheader("Portefeuille détaillé")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ==========================================================
# EXPORT CSV
# ==========================================================

st.subheader("Téléchargement")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Télécharger le portefeuille CSV",
    data=csv,
    file_name="portefeuille.csv",
    mime="text/csv"
)

# ==========================================================
# INFORMATIONS
# ==========================================================

st.markdown("---")

st.success(
    "Application chargée avec succès."
)
