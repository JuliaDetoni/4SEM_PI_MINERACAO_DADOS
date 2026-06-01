# queries.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def q1_receita_por_categoria(df: pd.DataFrame):
    """Top 10 categorias por receita (pedidos delivered)."""
    filtro = df[df['order_status'] == 'delivered']
    receita = filtro.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=receita.values, y=receita.index, palette='icefire', ax=ax)
    ax.set_title('Top 10 Categorias por Receita')
    ax.set_xlabel('Receita (R$)')
    return fig, receita

def q3_recorrencia_clientes(df: pd.DataFrame):
    """Clientes recorrentes e tempo médio entre compras."""
    filtro = df[df['order_status'].isin(['delivered', 'shipped', 'processing', 'approved'])]
    filtro = filtro.sort_values(['customer_unique_id', 'order_purchase_timestamp'])
    
    compras = filtro.groupby('customer_unique_id').agg(
        total_compras=('order_id', 'nunique'),
        primeira=('order_purchase_timestamp', 'min'),
        ultima=('order_purchase_timestamp', 'max')
    ).reset_index()
    
    recorrentes = compras[compras['total_compras'] > 1]
    pct_rec = len(recorrentes) / len(compras) * 100
    
    # Tempo entre compras
    tempos = []
    for cid in recorrentes['customer_unique_id']:
        datas = filtro[filtro['customer_unique_id'] == cid]['order_purchase_timestamp'].sort_values()
        deltas = datas.diff().dropna().dt.days
        tempos.extend(deltas.tolist())
    
    tempo_medio = np.mean(tempos) if tempos else 0
    
    fig, ax = plt.subplots(figsize=(10, 6))
    dist = compras['total_compras'].value_counts().sort_index().head(10)
    sns.barplot(x=dist.index, y=dist.values, palette='mako', ax=ax)
    ax.set_yscale('log')
    ax.set_title('Distribuição de Compras por Cliente')
    ax.set_xlabel('Nº de Compras')
    ax.set_ylabel('Clientes (log)')
    
    return fig, {
        'total_clientes': len(compras),
        'recorrentes': len(recorrentes),
        'pct_recorrentes': pct_rec,
        'tempo_medio_dias': tempo_medio
    }
