# app.py
import streamlit as st
from data_loader import load_all_data
from etl import apply_global_etl, merge_core
from queries import q1_receita_por_categoria, q3_recorrencia_clientes

st.set_page_config(page_title="OLIST BI", layout="wide")
st.title("📊 Análise de E-commerce — OLIST (2016-2018)")

# Sidebar
st.sidebar.header("Configurações")
modo = st.sidebar.radio("Modo de carga:", ["Carregar tudo", "Lazy (sob demanda)"])

# Carga de dados
with st.spinner("Baixando datasets do GitHub..."):
    dfs = load_all_data()

with st.spinner("Aplicando ETL..."):
    dfs = apply_global_etl(dfs)

# Navegação
aba = st.sidebar.selectbox("Selecione a análise:", [
    "Visão Geral", "Q1 — Receita por Categoria", "Q3 — Recorrência de Clientes"
])

if aba == "Visão Geral":
    st.metric("Total de Pedidos", f"{dfs['orders']['order_id'].nunique():,}")
    st.metric("Clientes Únicos", f"{dfs['customers']['customer_unique_id'].nunique():,}")
    st.metric("Sellers", f"{dfs['sellers']['seller_id'].nunique():,}")

elif aba == "Q1 — Receita por Categoria":
    df_core = merge_core(dfs)
    fig, dados = q1_receita_por_categoria(df_core)
    st.pyplot(fig)
    with st.expander("Ver dados"):
        st.dataframe(dados.reset_index())

elif aba == "Q3 — Recorrência de Clientes":
    df_core = merge_core(dfs)
    fig, metricas = q3_recorrencia_clientes(df_core)
    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes Únicos", f"{metricas['total_clientes']:,}")
    col2.metric("Recorrentes", f"{metricas['recorrentes']:,}")
    col3.metric("% Recorrência", f"{metricas['pct_recorrentes']:.2f}%")
    st.pyplot(fig)
    st.info(f"Tempo médio entre compras: **{metricas['tempo_medio_dias']:.1f} dias**")
