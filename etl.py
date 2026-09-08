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

    IMPORTANTE — payments e reviews podem ter mais de uma linha por order_id:
      • payments: pagamento dividido entre métodos (ex: voucher + cartão)
      • reviews: review reenviada pelo cliente após resposta do seller
    Se juntadas direto contra order_items (nível-item) via left join, cada
    linha extra de payments/reviews duplica os itens daquele pedido inteiro,
    inflando receita, contagem de itens e reviews negativas em toda a base.
    Por isso agregamos as duas a 1 linha por order_id ANTES do merge.
    """
    # payments → 1 linha por pedido: parcelas = maior plano usado,
    # tipo de pagamento = método do maior valor pago
    pay = dfs['payments'].sort_values('payment_value', ascending=False)
    payments_agg = pay.groupby('order_id').agg(
        payment_installments=('payment_installments', 'max'),
        payment_type=('payment_type', 'first'),
    ).reset_index()

    # reviews → 1 linha por pedido: fica com a mais recente em caso de reenvio
    rev = dfs['reviews'].copy()
    if 'review_answer_timestamp' in rev.columns:
        rev['review_answer_timestamp'] = pd.to_datetime(rev['review_answer_timestamp'], errors='coerce')
        rev = rev.sort_values('review_answer_timestamp')
    reviews_dedup = rev.drop_duplicates('order_id', keep='last')[['order_id', 'review_score']]

    df = dfs['orders'].merge(dfs['customers'][['customer_id', 'customer_unique_id']], on='customer_id')
    df = df.merge(dfs['order_items'], on='order_id')
    df = df.merge(dfs['products'][['product_id', 'product_category_name', 'product_photos_qty']], on='product_id')
    df = df.merge(payments_agg, on='order_id', how='left')
    df = df.merge(reviews_dedup, on='order_id', how='left')
    df = df.merge(dfs['sellers'][['seller_id', 'seller_city', 'seller_state']], on='seller_id', how='left')
    return df
