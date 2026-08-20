import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Portefeuille Obligataire",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Plateforme d'Analyse du Portefeuille Obligataire")

# =====================================================
# CHARGEMENT FICHIER
# =====================================================

st.sidebar.title("Portefeuille Obligataire")

uploaded_file = st.sidebar.file_uploader(
    "Charger le portefeuille",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Veuillez charger votre fichier Excel.")
    st.stop()

# =====================================================
# LECTURE EXCEL
# =====================================================

try:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.astype(str).str.strip()

except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

# =====================================================
# VERIFICATION DES COLONNES
# =====================================================

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

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.stop()

# =====================================================
# KPI
# =====================================================

encours = df["Prix Global"].sum()

duration_mp = (
    (df["Duration"] * df["Prix Global"]).sum()
    / encours
)

sensibilite_mp = (
    (df["Sensibilité"] * df["Prix Global"]).sum()
    / encours
)

tra_mp = (
    (df["TRA"] * df["Prix Global"]).sum()
    / encours
)

coupon_mp = (
    (df["Taux facial"] * df["Prix Global"]).sum()
    / encours
)

st.subheader("Tableau de Bord Exécutif")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Encours", f"{encours:,.0f}")
c2.metric("Durée", f"{duration_mp:.2f}")
c3.metric("Sensibilité", f"{sensibilite_mp:.2f}")
c4.metric("TRA", f"{tra_mp:.2%}")
c5.metric("Coupon", f"{coupon_mp:.2%}")

# =====================================================
# GRAPHIQUES
# =====================================================

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.subheader("Répartition par Segment")

    segment = (
        df.groupby("Segments")["Prix Global"]
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
        df.groupby("Classification")["Prix Global"]
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

# =====================================================
# TOP 10
# =====================================================

st.divider()

st.subheader("Top 10 Positions")

top10 = (
    df.sort_values(
        by="Prix Global",
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

# =====================================================
# CONCENTRATION
# =====================================================

st.divider()

st.subheader("Analyse de Concentration")

concentration = top10.copy()

concentration["Poids %"] = (
    concentration["Prix Global"]
    / encours
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

# =====================================================
# STRESS TEST
# =====================================================

st.divider()

st.subheader("Stress Test de Taux")

shocks = [-200, -150, -100, -50, 50, 100, 150, 200]

impacts = []

for shock in shocks:

    impact = (
        -sensibilite_mp
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

# =====================================================
# STATISTIQUES
# =====================================================

st.divider()

st.subheader("Statistiques")

stats = pd.DataFrame(
    {
        "Indicateur": [
            "Nombre de lignes",
            "Encours",
            "Durée",
            "Sensibilité",
            "TRA (%)",
            "Coupon (%)"
        ],
        "Valeur": [
            len(df),
            round(encours, 0),
            round(duration_mp, 2),
            round(sensibilite_mp, 2),
            round(tra_mp * 100, 2),
            round(coupon_mp * 100, 2)
        ]
    }
)

st.dataframe(
    stats,
    use_container_width=True
)

# =====================================================
# PORTEFEUILLE DETAILLE
# =====================================================

st.divider()

st.subheader("Portefeuille Détaillé")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# =====================================================
# EXPORT EXCEL
# =====================================================

st.divider()

st.subheader("Téléchargements")

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Portefeuille",
        index=False
    )

    top10.to_excel(
        writer,
        sheet_name="Top10",
        index=False
    )

    concentration.to_excel(
        writer,
        sheet_name="Concentration",
        index=False
    )

    stress.to_excel(
        writer,
        sheet_name="StressTest",
        index=False
    )

excel_data = excel_buffer.getvalue()

st.download_button(
    label="📊 Télécharger le Rapport Excel",
    data=excel_data,
    file_name="Rapport_Portefeuille_Obligataire.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =====================================================
# EXPORT CSV
# =====================================================

csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📄 Télécharger CSV",
    data=csv,
    file_name="Portefeuille.csv",
    mime="text/csv"
)

# =====================================================
# FIN
# =====================================================

st.success("Application chargée avec succès.")
