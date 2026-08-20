import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Portefeuille Obligataire",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.image(
    "https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png",
    width=200
)

st.sidebar.title("Portefeuille Obligataire")

st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Charger le portefeuille",
    type=["xlsx"]
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if uploaded_file is not None:

    portefeuille = pd.read_excel(uploaded_file)

    st.session_state["portfolio"] = portefeuille

# --------------------------------------------------
# PAGE PRINCIPALE
# --------------------------------------------------

st.title("📊 Plateforme d'Analyse du Portefeuille Obligataire")

st.markdown(
"""
Cette plateforme permet :

✅ Suivi du portefeuille obligataire

✅ Analyse de duration

✅ Analyse de la sensibilité

✅ Benchmarking MBI

✅ Analyse de concentration

✅ Stress tests de taux

✅ Historisation des indicateurs

✅ Téléchargement des résultats
"""
)

st.divider()

# --------------------------------------------------
# CONTROLES
# --------------------------------------------------

if "portfolio" not in st.session_state:

    st.warning(
        "Veuillez charger un fichier Excel depuis le menu de gauche."
    )

    st.stop()

# --------------------------------------------------
# CHARGEMENT DONNÉES
# --------------------------------------------------

df = st.session_state["portfolio"]

# --------------------------------------------------
# KPI RAPIDES
# --------------------------------------------------

encours = df["Prix Global"].sum()

duration = (
    (
        df["Duration"]
        * df["Prix Global"]
    ).sum()
    / encours
)

sensibilite = (
    (
        df["Sensibilité"]
        * df["Prix Global"]
    ).sum()
    / encours
)

tra = (
    (
        df["TRA"]
        * df["Prix Global"]
    ).sum()
    / encours
)

coupon = (
    (
        df["Taux facial"]
        * df["Prix Global"]
    ).sum()
    / encours
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Encours",
    f"{encours/1e9:,.2f} MMAD"
)

col2.metric(
    "Duration",
    f"{duration:.2f}"
)

col3.metric(
    "Sensibilité",
    f"{sensibilite:.2f}"
)

col4.metric(
    "TRA",
    f"{tra:.2%}"
)

col5.metric(
    "Coupon",
    f"{coupon:.2%}"
)

st.divider()

# --------------------------------------------------
# APERÇU
# --------------------------------------------------

st.subheader("Aperçu du portefeuille")

colonnes = [
    "Description Titres",
    "Prix Global",
    "Duration",
    "Sensibilité",
    "TRA",
    "Segments",
    "Classification"
]

colonnes_existantes = [
    c for c in colonnes
    if c in df.columns
]

st.dataframe(
    df[colonnes_existantes],
    use_container_width=True
)

# --------------------------------------------------
# STATISTIQUES
# --------------------------------------------------

st.subheader("Statistiques globales")

stats = pd.DataFrame(
    {
        "Indicateur": [
            "Nombre de lignes",
            "Encours",
            "Duration",
            "Sensibilité",
            "TRA Moyen"
        ],
        "Valeur": [
            len(df),
            round(encours, 0),
            round(duration, 2),
            round(sensibilite, 2),
            round(tra * 100, 2)
        ]
    }
)

st.dataframe(
    stats,
    use_container_width=True
)

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

st.subheader("Exports")

csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Télécharger CSV",
    data=csv,
    file_name="portefeuille.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "Version 2.0 | Application d'analyse du portefeuille obligataire"
)
