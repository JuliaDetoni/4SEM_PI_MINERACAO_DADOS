# etl.py
import pandas as pd
import numpy as np

def apply_global_etl(dfs: dict) -> dict:
    """
    Aplica o ETL do PI nos datasets.
    Retorna o dict modificado (zero perda de linhas).
    """
    # --- PRODUTOS ---
    prd = dfs['products'].copy()
    prd['product_photos_qty'] = prd['product_photos_qty'].fillna(0)
    prd['product_category_name'] = prd['product_category_name'].fillna('sem_categoria')
    
    dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
    for col in dim_cols:
        prd[col] = prd[col].fillna(prd[col].median())
    
    for col in ['product_name_lenght', 'product_description_lenght']:
        prd[col] = prd[col].fillna(0)
    
    dfs['products'] = prd

    # --- PAGAMENTOS ---
    pg = dfs['payments'].copy()
    pg['payment_installments'] = pg['payment_installments'].fillna(1)
    dfs['payments'] = pg

    # --- PEDIDOS (datas NÃO imputadas, só convertidas) ---
    ped = dfs['orders'].copy()
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
    for col in date_cols:
        ped[col] = pd.to_datetime(ped[col], errors='coerce')
    dfs['orders'] = ped

    return dfs

def merge_core(dfs: dict) -> pd.DataFrame:
    """
    Cria o DataFrame mestre com joins essenciais.
    Usado nas queries que precisam de tudo junto.
    """
    df = dfs['orders'].merge(dfs['customers'][['customer_id', 'customer_unique_id']], on='customer_id')
    df = df.merge(dfs['order_items'], on='order_id')
    df = df.merge(dfs['products'][['product_id', 'product_category_name', 'product_photos_qty']], on='product_id')
    df = df.merge(dfs['payments'][['order_id', 'payment_installments', 'payment_type']], on='order_id', how='left')
    df = df.merge(dfs['reviews'][['order_id', 'review_score']], on='order_id', how='left')
    df = df.merge(dfs['sellers'][['seller_id', 'seller_city', 'seller_state']], on='seller_id', how='left')
    return df
