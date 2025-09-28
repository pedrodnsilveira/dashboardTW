import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Conquistas", layout="wide")

st.title("📊 Dashboard de Conquistas - Tribal Wars")

# Lê diretamente o CSV salvo pelo script Node
CSV_PATH = "ennoblements.csv"

try:
    df = pd.read_csv(CSV_PATH, sep=";")

    st.subheader("Dados Carregados")
    st.dataframe(df)

    # Agrupamento por jogador conquistador
    conquistas_por_jogador = df.groupby("conquistador_nome").size().reset_index(name="total")
    conquistas_por_jogador = conquistas_por_jogador.sort_values(by="total", ascending=False)

    # Agrupamento por tribo conquistadora
    conquistas_por_tribo = df.groupby("conquistador_tribo").size().reset_index(name="total")
    conquistas_por_tribo = conquistas_por_tribo.sort_values(by="total", ascending=False)

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Conquistas por Jogador")
        st.bar_chart(conquistas_por_jogador.set_index("conquistador_nome"))
        st.dataframe(conquistas_por_jogador)

    with col2:
        st.subheader("🏅 Conquistas por Tribo")
        st.bar_chart(conquistas_por_tribo.set_index("conquistador_tribo"))
        st.dataframe(conquistas_por_tribo)

    # Ranking detalhado
    st.subheader("📋 Detalhamento")
    st.dataframe(df.sort_values(by="data", ascending=False))

except FileNotFoundError:
    st.error(f"Arquivo {CSV_PATH} não encontrado. Execute primeiro o script Node para gerar o CSV.")

