import streamlit as st
import pandas as pd
import plotly.express as px

#dthr = (datetime.fromtimestamp(ts) - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")

st.set_page_config(page_title="Dashboard de Conquistas", layout="wide")
st.title("📊 Dashboard de Conquistas - Tribal Wars:Br 134")

CSV_PATH = "ennoblements.csv"

try:
    df = pd.read_csv(CSV_PATH, sep=";")

    # Certifica que a coluna 'data' é datetime
    df['data'] = pd.to_datetime(df['data'], format="%Y-%m-%d - %H:%M:%S")

    # Primeira e última data
    primeira_data = df['data'].min()
    ultima_data = df['data'].max()
    st.subheader("Período: " + str(primeira_data.strftime("%d/%m/%Y %H:%M:%S") + " à " + str(ultima_data.strftime("%d/%m/%Y %H:%M:%S"))

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
    # Gráficos de Pizza para Jogador e Tribo (top 5 apenas nos gráficos)
    # -------------------------
    def top5_para_grafico(df, coluna_nome="conquistador_nome", coluna_valor="total", top_n=5):
        # Ordena pelo valor
        df_sorted = df.sort_values(by=coluna_valor, ascending=False)
        
        # Pega os top_n
        top = df_sorted.head(top_n).copy()
        
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
    # Colunas dos gráficos
    # -------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Conquistas por Jogador")
        # Apenas para o gráfico
        df_jogador_grafico = top5_para_grafico(conquistas_por_jogador, "conquistador_nome", "total", top_n=5)
        fig1 = px.pie(df_jogador_grafico, values="total", names="conquistador_nome",
                    title="Distribuição de Conquistas por Jogador (Top 5)")
        st.plotly_chart(fig1, use_container_width=True)
        # Tabela completa
        st.dataframe(conquistas_por_jogador)

    with col2:
        st.subheader("🏅 Conquistas por Tribo")
        # Apenas para o gráfico
        df_tribo_grafico = top5_para_grafico(conquistas_por_tribo, "conquistador_tribo", "total", top_n=5)
        fig2 = px.pie(df_tribo_grafico, values="total", names="conquistador_tribo",
                    title="Distribuição de Conquistas por Tribo (Top 5)")
        st.plotly_chart(fig2, use_container_width=True)
        # Tabela completa
        st.dataframe(conquistas_por_tribo)





    # -------------------------
    # Conquistas de Jogadores por Tribo
    # -------------------------
    # Função para manter top N por grupo e somar o resto em "Outros"
    def topN_por_grupo(df, grupo_col, valor_col="total", top_n=5):
        resultado = []
        for grupo, sub_df in df.groupby(grupo_col):
            sub_sorted = sub_df.sort_values(by=valor_col, ascending=False)
            top = sub_sorted.head(top_n)
            outros = sub_sorted.iloc[top_n:][valor_col].sum()
            if outros > 0:
                outros_row = pd.DataFrame({
                    grupo_col: [grupo],
                    "conquistador_nome": ["Outros"],
                    valor_col: [outros]
                })
                top = pd.concat([top, outros_row], ignore_index=True)
            resultado.append(top)
        return pd.concat(resultado, ignore_index=True)

    # -------------------------
    # Conquistas de Jogadores por Tribo (top 5 por tribo + "Outros")
    # -------------------------
    st.subheader("👥 Conquistas de Jogadores por Tribo")
    conquistas_jogador_tribo = df.groupby(["conquistador_tribo", "conquistador_nome"]).size().reset_index(name="total")

    # Aplicar topN_por_grupo para limitar jogadores por tribo
    conquistas_jogador_tribo_plot = topN_por_grupo(conquistas_jogador_tribo, "conquistador_tribo", "total", top_n=5)

    #st.dataframe(conquistas_jogador_tribo_plot.sort_values(by=["conquistador_tribo", "total"], ascending=[True, False]))

    fig3 = px.sunburst(
        conquistas_jogador_tribo_plot,
        path=["conquistador_tribo", "conquistador_nome"],
        values="total",
        height=600
        #title="Hierarquia de Conquistas: Tribos → Jogadores"
    )
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
    # Ranking detalhado
    # -------------------------
    st.subheader("📋 Detalhamento")
    st.dataframe(df.sort_values(by="data", ascending=False))

except FileNotFoundError:
    st.error(f"Arquivo {CSV_PATH} não encontrado. Execute primeiro o script Node para gerar o CSV.")

