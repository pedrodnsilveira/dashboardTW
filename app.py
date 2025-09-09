import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard TW Conquistas", layout="wide")

st.title("📊 Dashboard de Conquistas - Últimas 6h")

# Carrega o CSV
df = pd.read_csv("ennoblements.csv")

# Totais por Conquistador
totais = df.groupby("conqueror")["count"].sum().reset_index().sort_values("count", ascending=False)

st.subheader("Total de conquistas por Conquistador")
st.dataframe(totais)

# Gráfico de barras
chart = alt.Chart(totais).mark_bar().encode(
    x=alt.X("count", title="Conquistas"),
    y=alt.Y("conqueror", sort="-x"),
    tooltip=["conqueror", "count"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# Detalhes: tribo / bárbaros / player isolado
st.subheader("Detalhamento por tipo de alvo")
detalhes = df.groupby(["conqueror", "loser_type"])["count"].sum().reset_index()

st.dataframe(detalhes)
