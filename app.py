# app.py
# app.py
import streamlit as st
import numpy as np
import pandas as pd          # <-- adicionar esta linha
from data_loader import load_all_data
from etl import apply_global_etl, merge_core
import queries as q

st.set_page_config(page_title="OLIST BI — Mineração de Dados", layout="wide", page_icon="📊")
st.title("📊 Análise de E-commerce — OLIST (2016–2018)")
st.caption("Projeto Integrador — 4º Semestre | Mineração de Dados com Python, Pandas, Scikit-Learn & Streamlit")

# ==============================================================================
# FUNÇÃO AUXILIAR (definida ANTES da cadeia if/elif)
# ==============================================================================
def render_pergunta(titulo, descricao, func, df):
    st.header(titulo)
    st.markdown(descricao)
    
    with st.spinner("Executando análise..."):
        fig, metricas, detalhe = func(df)
    
    cols = st.columns(len(metricas))
    for col, (k, v) in zip(cols, metricas.items()):
        label = k.replace('_', ' ').title()
        if isinstance(v, float):
            col.metric(label, f"{v:.2f}")
        else:
            col.metric(label, f"{v:,}" if isinstance(v, (int, np.integer)) else str(v))
    
    st.pyplot(fig)
    
    with st.expander("📄 Relatório de Dados Completo"):
        st.dataframe(detalhe, use_container_width=True, hide_index=True)
        st.download_button(
            label="⬇️ Baixar CSV",
            data=detalhe.to_csv(index=False).encode('utf-8'),
            file_name=f"{titulo.split('—')[0].strip().replace(' ', '_')}.csv",
            mime='text/csv'
        )

# ==============================================================================
# CARGA DE DADOS
# ==============================================================================
with st.spinner("Executando ETL e merges..."):
    dfs = load_all_data()
    dfs = apply_global_etl(dfs)
    df_core = merge_core(dfs)

# ==============================================================================
# SIDEBAR — NAVEGAÇÃO
# ==============================================================================
st.sidebar.header("🔎 Navegação")
menu = st.sidebar.radio("Selecione a seção:", [
    "📋 Visão Geral",
    "🔧 Auditoria ETL",
    "Q1 — Receita por Categoria",
    "Q2 — Cancelamento × Tempo",
    "Q3 — Recorrência de Clientes",
    "Q4 — Migração de Categoria",
    "Q5 — Fotos × Preço & Volume",
    "Q6 — Itens por Pedido",
    "Q7 — Prever Insatisfação (ML)",
    "Q8 — Intervenção em Sellers",
    "Q9 — Risco-Receita",
])

# ==============================================================================
# VISÃO GERAL
# ==============================================================================
if menu == "📋 Visão Geral":
    st.header("Visão Geral dos Datasets")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pedidos", f"{dfs['orders']['order_id'].nunique():,}")
    col2.metric("Clientes Únicos", f"{dfs['customers']['customer_unique_id'].nunique():,}")
    col3.metric("Sellers", f"{dfs['sellers']['seller_id'].nunique():,}")
    col4.metric("Produtos", f"{dfs['products']['product_id'].nunique():,}")
    
    st.divider()
    st.subheader("Amostras dos Datasets (ETL aplicado)")
    tabs = st.tabs(list(dfs.keys()))
    for tab, (nome, df) in zip(tabs, dfs.items()):
        with tab:
            st.write(f"**{nome}** — {len(df):,} registros × {len(df.columns)} colunas")
            st.dataframe(df.head(5), use_container_width=True)

# ==============================================================================
# AUDITORIA ETL
# ==============================================================================
elif menu == "🔧 Auditoria ETL":
    st.header("Auditoria do Processo ETL")
    st.markdown("""
    **Princípios aplicados:**
    - **Zero-Loss:** nenhuma linha removida.
    - **Semântica:** imputação reflete estado real de negócio.
    - **Transparência:** todo campo alterado é reportado.
    - **Datas preservadas:** nulos em datas de entrega significam "não entregue".
    """)
    
    log = []
    prd = dfs['products']
    if 'product_photos_qty' in prd.columns:
        log.append(("prd", "product_photos_qty", "fillna", 0, "Fotos não cadastradas = 0"))
    if 'product_category_name' in prd.columns:
        log.append(("prd", "product_category_name", "fillna", "sem_categoria", "Categoria não informada"))
    
    pg = dfs['payments']
    if 'payment_installments' in pg.columns:
        log.append(("pgpd", "payment_installments", "fillna", 1, "À vista = 1 parcela"))
    
    st.subheader("Log de Transformações")
    log_df = pd.DataFrame(log, columns=["Dataset", "Campo", "Ação", "Valor Imputado", "Justificativa"])
    st.dataframe(log_df, use_container_width=True, hide_index=True)
    
    st.subheader("Tamanho dos Datasets (linhas preservadas)")
    sizes = {k: len(v) for k, v in dfs.items()}
    st.bar_chart(pd.Series(sizes))

# ==============================================================================
# PERGUNTAS
# ==============================================================================
elif menu == "Q1 — Receita por Categoria":
    render_pergunta(
        "Q1 — Quais categorias geram mais receita?",
        "> **Visualização:** barras horizontais ordenadas por receita decrescente. "
        "Permite identificar concentração de faturamento e dependência de nicho.",
        q.q1_receita_por_categoria, df_core
    )

elif menu == "Q2 — Cancelamento × Tempo":
    render_pergunta(
        "Q2 — Cancelamento correlaciona com tempo de aprovação?",
        "> **Visualização:** ranking de cancelamento + scatter de correlação. "
        "Detecta verticais com atrito no checkout e se tempo de processamento é fator de desistência.",
        q.q2_cancelamento_tempo, df_core
    )

elif menu == "Q3 — Recorrência de Clientes":
    render_pergunta(
        "Q3 — Quantos clientes compram mais de uma vez? Tempo médio entre compras?",
        "> **Visualização:** distribuição logarítmica de compras + histograma de intervalos. "
        "Quantifica saúde da base em retenção e janela para remarketing.",
        q.q3_recorrencia_clientes, df_core
    )

elif menu == "Q4 — Migração de Categoria":
    render_pergunta(
        "Q4 — Clientes recorrentes migram de categoria ou ficam fiéis?",
        "> **Visualização:** pizza de fidelidade + top transições. "
        "Orienta se o algoritmo de recomendação deve priorizar profundidade ou diversificação.",
        q.q4_migracao_categoria, df_core
    )

elif menu == "Q5 — Fotos × Preço & Volume":
    render_pergunta(
        "Q5 — Produtos com mais fotos têm preço maior ou menor volume?",
        "> **Visualização:** preço, volume e scatter combinado. "
        "Compreende se investimento em fotografia sustenta valor percebido ou impulsa giro.",
        q.q5_fotos_preco_volume, df_core
    )

elif menu == "Q6 — Itens por Pedido":
    render_pergunta(
        "Q6 — Qual a distribuição de itens por pedido?",
        "> **Visualização:** histograma com bins unitários. "
        "Quantifica gap de cross-selling e potencial de aumento de ticket médio.",
        q.q6_itens_por_pedido, df_core
    )

elif menu == "Q7 — Prever Insatisfação (ML)":
    render_pergunta(
        "Q7 — É possível prever insatisfação antes da avaliação?",
        "> **Modelos:** Random Forest + Regressão Logística. "
        "Identifica determinantes operacionais de insatisfação para sistema de alerta.",
        q.q7_prever_insatisfacao, df_core
    )

elif menu == "Q8 — Intervenção em Sellers":
    render_pergunta(
        "Q8 — Qual ação operacional para sellers tóxicos?",
        "> **Análise prescritiva:** matriz de intervenção com thresholds de frete e nota. "
        "Automatiza classificação de prioridade sem análise manual caso a caso.",
        q.q8_intervencao_sellers, df_core
    )

elif menu == "Q9 — Risco-Receita":
    render_pergunta(
        "Q9 — Quanto da receita está em sellers tóxicos?",
        "> **Visualização:** scatter em escala log com quadrantes de risco-receita. "
        "Quantifica impacto financeiro de intervenções para evitar decisões punitivas que comprometam P&L.",
        q.q9_risco_receita, df_core
    )
