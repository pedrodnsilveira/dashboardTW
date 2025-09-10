import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Conquistas", layout="wide")

st.title("📊 Dashboard de Conquistas (TWStats)")

# --- Carregar CSV ---
try:
    df = pd.read_csv("ennoblements.csv")
except FileNotFoundError:
    st.error("❌ Arquivo ennoblements.csv não encontrado. Rode primeiro o script Node (ennoblements.js).")
    st.stop()

# --- Sidebar ---
st.sidebar.header("Filtros")
conquerors = st.sidebar.multiselect("Filtrar por Conquistador", df["conqueror"].unique())
tribos_alvo = st.sidebar.multiselect("Filtrar por Tribo Alvo", df["tribo_name"].dropna().unique())

filtro = df.copy()
if conquerors:
    filtro = filtro[filtro["conqueror"].isin(conquerors)]
if tribos_alvo:
    filtro = filtro[filtro["tribo_name"].isin(tribos_alvo)]

# --- Tabela geral ---
st.subheader("Resumo por Conquistador")
totais = (
    filtro.groupby(["conqueror", "tribo_conqueror"], dropna=False)[["total", "barbaros", "players"]]
    .max()
    .reset_index()
    .sort_values("total", ascending=False)
)
st.dataframe(totais, use_container_width=True)

# --- Tabela por tribo alvo ---
st.subheader("Conquistas por Tribo Alvo")
tribos = (
    filtro.groupby(["conqueror", "tribo_name"], dropna=False)["tribo_count"]
    .sum()
    .reset_index()
    .sort_values("tribo_count", ascending=False)
)
st.dataframe(tribos, use_container_width=True)

# --- Gráficos ---
st.subheader("📈 Ranking de Conquistadores")
st.bar_chart(totais.set_index("conqueror")["total"])

st.subheader("🏹 Conquistas por Tribo Alvo")
st.bar_chart(tribos.set_index("tribo_name")["tribo_count"])

