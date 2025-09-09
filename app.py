import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard TW Conquistas", layout="wide")
st.title("📊 Dashboard de Conquistas - Últimas 6h")

# Lê CSV
df = pd.read_csv("ennoblements.csv")

# Certifique-se que os valores são numéricos
df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)

# Totais por conquistador
totais = df.groupby("conqueror")["total"].sum().reset_index().sort_values("total", ascending=False)

st.subheader("Total de conquistas por Conquistador")
st.dataframe(totais)

# Gráfico de barras
chart = alt.Chart(totais).mark_bar().encode(
    x=alt.X("total", title="Conquistas"),
    y=alt.Y("conqueror", sort="-x"),
    tooltip=["conqueror", "total"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# Detalhes: tribo / bárbaros / player isolado
st.subheader("Detalhamento por tipo de alvo")
# Agrupa por conquistador + tipo de alvo
detalhes = []

for idx, row in df.iterrows():
    # linha geral
    detalhes.append({
        "conqueror": row['conqueror'],
        "loser_type": "barbaros",
        "count": row['barbaros']
    })
    detalhes.append({
        "conqueror": row['conqueror'],
        "loser_type": "players",
        "count": row['players']
    })
    # linhas por tribo
    if pd.notna(row['tribo_name']):
        detalhes.append({
            "conqueror": row['conqueror'],
            "loser_type": row['tribo_name'],
            "count": row['tribo_count']
        })

df_detalhes = pd.DataFrame(detalhes)
st.dataframe(df_detalhes)
