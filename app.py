import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

ts = os.path.getmtime("ennoblements.csv")
dthr = (datetime.fromtimestamp(ts) - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")

st.set_page_config(page_title="Dashboard de Conquistas", layout="wide")
st.title("📊 Dashboard de Conquistas - Tribal Wars:Br 134")
st.subheader("Última atualização: " + str(dthr))

CSV_PATH = "ennoblements.csv"

try:
    df = pd.read_csv(CSV_PATH, sep=";")

    #st.subheader("Dados Carregados")
    #st.dataframe(df)

    # -------------------------
    # Conquistas por Jogador (incluindo jogadores sem tribo e aldeias bb)
    # -------------------------

    # Criar coluna ajustada para conquistado_tribo
    def ajustar_tribo(row):
        if pd.isna(row["conquistado_tribo"]) or row["conquistado_tribo"] == "":
            if row["conquistado_nome"] == "Aldeias de Bárbaros":
                return "Aldeias de Bárbaros"
            else:
                return "Sem tribo"
        return row["conquistado_tribo"]

    df["conquistado_tribo_ajustado"] = df.apply(ajustar_tribo, axis=1)

    # Remover conquistas do próprio jogador na própria tribo
    df_filtrado = df[~((df["conquistado_nome"] == df["conquistador_nome"]) &
                    (df["conquistado_tribo_ajustado"] == df["conquistador_tribo"]))]

    # Agrupar
    resumo = (
        df_filtrado.groupby(["conquistador_nome", "conquistador_tribo", "conquistado_tribo_ajustado"])
        .size()
        .reset_index(name="quantidade_conquistas")
    )

    # Mostrar no Streamlit
    st.title("Resumo de Conquistas por jogador")
    st.dataframe(resumo)

    # -------------------------
    # Filtra conquistas de Aldeias de Bárbaros
    # -------------------------
    df_barbaros = df_filtrado[df_filtrado["conquistado_nome"].str.contains("Aldeias de Bárbaros", case=False)]

    # -------------------------
    # Conquistas por Jogador (incluindo coluna de Bárbaros)
    # -------------------------
    conquistas_por_jogador = df_filtrado.groupby(["conquistador_tribo", "conquistador_nome"]) \
        .size().reset_index(name="total")
    barbaros_por_jogador = df_barbaros.groupby("conquistador_nome") \
        .size().reset_index(name="barbaros")
    conquistas_por_jogador = conquistas_por_jogador.merge(barbaros_por_jogador, on="conquistador_nome", how="left").fillna(0)
    conquistas_por_jogador["barbaros"] = conquistas_por_jogador["barbaros"].astype(int)
    conquistas_por_jogador = conquistas_por_jogador.sort_values(by="total", ascending=False)

    # -------------------------
    # Conquistas por Tribo (incluindo coluna de Bárbaros)
    # -------------------------
    conquistas_por_tribo = df_filtrado.groupby("conquistador_tribo").size().reset_index(name="total")
    barbaros_por_tribo = df_barbaros.groupby("conquistador_tribo").size().reset_index(name="barbaros")
    conquistas_por_tribo = conquistas_por_tribo.merge(barbaros_por_tribo, on="conquistador_tribo", how="left").fillna(0)
    conquistas_por_tribo["barbaros"] = conquistas_por_tribo["barbaros"].astype(int)
    conquistas_por_tribo = conquistas_por_tribo.sort_values(by="total", ascending=False)


    # -------------------------
    # Gráficos de Pizza para Jogador e Tribo
    # -------------------------
    def top5_com_outros(df, coluna_nome="conquistador_nome", coluna_valor="total", top_n=5):
        # Ordena pelo valor
        df_sorted = df.sort_values(by=coluna_valor, ascending=False)
        
        # Pega os top_n
        top = df_sorted.head(top_n)
        
        # Soma o restante
        outros = df_sorted.iloc[top_n:][coluna_valor].sum()
        
        # Adiciona linha "Outros" se houver
        if outros > 0:
            outros_row = pd.DataFrame({
                coluna_nome: ["Outros"],
                coluna_valor: [outros]
            })
            top = pd.concat([top, outros_row], ignore_index=True)
        
        return top

    # -------------------------
    # Gráficos de Pizza para Jogador e Tribo (com "Outros")
    # -------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Conquistas por Jogador")
        df_jogador_plot = top5_com_outros(conquistas_por_jogador, coluna_nome="conquistador_nome", coluna_valor="total", top_n=5)
        fig1 = px.pie(df_jogador_plot, values="total", names="conquistador_nome",
                    title="Distribuição de Conquistas por Jogador")
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(df_jogador_plot)

    with col2:
        st.subheader("🏅 Conquistas por Tribo")
        df_tribo_plot = top5_com_outros(conquistas_por_tribo, coluna_nome="conquistador_tribo", coluna_valor="total", top_n=5)
        fig2 = px.pie(df_tribo_plot, values="total", names="conquistador_tribo",
                    title="Distribuição de Conquistas por Tribo")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df_tribo_plot)


    # -------------------------
    # Conquistas de Jogadores por Tribo
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
    st.subheader("🏹 Conquistas de Tribos sobre Outras Tribos")
    conquistas_tribo_vs_tribo = df.groupby(["conquistador_tribo", "conquistado_tribo"]).size().reset_index(name="total")
    st.dataframe(conquistas_tribo_vs_tribo.sort_values(by="total", ascending=False))

    fig4 = px.treemap(conquistas_tribo_vs_tribo,
                      path=["conquistador_tribo", "conquistado_tribo"],
                      values="total",
                      title="Mapa de Conquistas: Tribo Conquistadora → Tribo Conquistada")
    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------
    # Conquistas de Aldeias de Bárbaros
    # -------------------------
    st.subheader("⚔️ Conquistas de Aldeias de Bárbaros")

    # Por jogador
    #barbaros_por_jogador = df_barbaros.groupby("conquistador_nome").size().reset_index(name="total")
    barbaros_por_jogador = df_barbaros.groupby(["conquistador_nome", "conquistador_tribo"]).size().reset_index(name="total")
    barbaros_por_jogador = barbaros_por_jogador.sort_values(by="total", ascending=False)
    # Por tribo
    barbaros_por_tribo = df_barbaros.groupby("conquistador_tribo").size().reset_index(name="total")
    barbaros_por_tribo = barbaros_por_tribo.sort_values(by="total", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Jogadores que conquistaram Bárbaros")
        fig5 = px.pie(barbaros_por_jogador, values="total", names="conquistador_nome", title="Distribuição de Conquistas de Bárbaros por Jogador")
        st.plotly_chart(fig5, use_container_width=True)
        st.dataframe(barbaros_por_jogador)

    with col2:
        st.subheader("Tribo que conquistou Bárbaros")
        fig6 = px.pie(barbaros_por_tribo, values="total", names="conquistador_tribo", title="Distribuição de Conquistas de Bárbaros por Tribo")
        st.plotly_chart(fig6, use_container_width=True)
        st.dataframe(barbaros_por_tribo)

    # -------------------------
    # Ranking detalhado
    # -------------------------
    st.subheader("📋 Detalhamento")
    st.dataframe(df.sort_values(by="data", ascending=False))

except FileNotFoundError:
    st.error(f"Arquivo {CSV_PATH} não encontrado. Execute primeiro o script Node para gerar o CSV.")

