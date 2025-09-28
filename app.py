import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Conquistas", layout="wide")

st.title("📊 Dashboard de Conquistas - Tribal Wars")

# Caminho do CSV exportado pelo Node
CSV_PATH = "ennoblements.csv"

try:
    df = pd.read_csv(CSV_PATH, sep=";")

    st.subheader("Dados Carregados")
    st.dataframe(df)

    # -------------------------
    # Conquistas por Jogador
    # -------------------------
    conquistas_por_jogador = df.groupby("conquistador_nome").size().reset_index(name="total")
    conquistas_por_jogador = conquistas_por_jogador.sort_values(by="total", ascending=False)

    # -------------------------
    # Conquistas por Tribo
    # -------------------------
    conquistas_por_tribo = df.groupby("conquistador_tribo").size().reset_index(name="total")
    conquistas_por_tribo = conquistas_por_tribo.sort_values(by="total", ascending=False)

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Conquistas por Jogador")
        fig1 = px.pie(conquistas_por_jogador, values="total", names="conquistador_nome", title="Distribuição de Conquistas por Jogador")
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(conquistas_por_jogador)

    with col2:
        st.subheader("🏅 Conquistas por Tribo")
        fig2 = px.pie(conquistas_por_tribo, values="total", names="conquistador_tribo", title="Distribuição de Conquistas por Tribo")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(conquistas_por_tribo)

    # -------------------------
    # Conquistas de Jogador por Tribo
    # -------------------------
    st.subheader("👥 Conquistas de Jogadores por Tribo")
    conquistas_jogador_tribo = df.groupby(["conquistador_tribo", "conquistador_nome"]).size().reset_index(name="total")
    st.dataframe(conquistas_jogador_tribo.sort_values(by=["conquistador_tribo", "total"], ascending=[True, False]))

    fig3 = px.sunburst(conquistas_jogador_tribo,
                       path=["conquistador_tribo", "conquistador_nome"],
                       values="total",
                       title="Hierarquia de Conquistas: Tribos → Jogadores")
    st.plotly_chart(fig3, use_container_width=True)

    # -------------------------
    # Conquistas de Tribos por Tribo
    # -------------------------
    st.subheader("🏹 Conquistas de Tribos sobre Outras Tribos (incluindo Bárbaros)")
    conquistas_tribo_vs_tribo = df.groupby(["conquistador_tribo", "conquistado_tribo"]).size().reset_index(name="total")
    st.dataframe(conquistas_tribo_vs_tribo.sort_values(by="total", ascending=False))

    fig4 = px.treemap(conquistas_tribo_vs_tribo,
                      path=["conquistador_tribo", "conquistado_tribo"],
                      values="total",
                      title="Mapa de Conquistas: Tribo Conquistadora → Tribo Conquistada")
    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------
    # Ranking detalhado
    # -------------------------
    st.subheader("📋 Detalhamento")
    st.dataframe(df.sort_values(by="data", ascending=False))

except FileNotFoundError:
    st.error(f"Arquivo {CSV_PATH} não encontrado. Execute primeiro o script Node para gerar o CSV.")

