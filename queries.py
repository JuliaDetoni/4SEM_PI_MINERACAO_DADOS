# queries.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# ==============================================================================
# HELPERS
# ==============================================================================

def _save_fig():
    plt.tight_layout()
    return plt.gcf()

# ==============================================================================
# Q1 — RECEITA POR CATEGORIA
# ==============================================================================

def q1_receita_por_categoria(df: pd.DataFrame):
    filtro = df[df['order_status'] == 'delivered']
    receita = filtro.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
    receita_total_top10 = receita.sum()
    receita_total_geral = filtro.groupby('product_category_name')['price'].sum().sum()
    
    fig, ax = plt.subplots()
    sns.barplot(x=receita.values, y=receita.index, palette='icefire', ax=ax)
    ax.set_title('Top 10 Categorias por Receita')
    ax.set_xlabel('Receita (R$)')
    
    metricas = {
        'receita_total_top10': receita_total_top10,
        'receita_total_geral': receita_total_geral,
        'pct_top10': (receita_total_top10 / receita_total_geral) * 100,
        'categorias_distintas': filtro['product_category_name'].nunique(),
        'pedidos_analisados': filtro['order_id'].nunique(),
    }
    return fig, metricas, receita.reset_index()

# ==============================================================================
# Q2 — CANCELAMENTO × TEMPO DE APROVAÇÃO
# ==============================================================================

def q2_cancelamento_tempo(df: pd.DataFrame):
    ped = df[['order_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'product_category_name']].drop_duplicates('order_id')
    ped['tempo_aprovacao_horas'] = (ped['order_approved_at'] - ped['order_purchase_timestamp']).dt.total_seconds() / 3600
    
    total = ped.groupby('product_category_name')['order_id'].nunique().reset_index(name='total_pedidos')
    cancel = ped[ped['order_status'] == 'canceled'].groupby('product_category_name')['order_id'].nunique().reset_index(name='cancelados')
    taxa = total.merge(cancel, on='product_category_name', how='left').fillna(0)
    taxa['taxa_cancelamento'] = taxa['cancelados'] / taxa['total_pedidos']
    taxa = taxa[taxa['total_pedidos'] >= 100].sort_values('taxa_cancelamento', ascending=False)
    
    tempo = ped[ped['order_status'] != 'canceled'].groupby('product_category_name')['tempo_aprovacao_horas'].mean().reset_index(name='tempo_aprovacao_medio')
    analise = taxa.merge(tempo, on='product_category_name', how='left').dropna()
    
    validos = analise.dropna(subset=['tempo_aprovacao_medio', 'taxa_cancelamento'])
    corr = np.corrcoef(validos['tempo_aprovacao_medio'].values, validos['taxa_cancelamento'].values)[0, 1] if len(validos) > 1 else 0
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    top10 = analise.head(10)
    sns.barplot(x='taxa_cancelamento', y='product_category_name', data=top10, palette='rocket', ax=axes[0])
    axes[0].set_title('Top 10 — Taxa de Cancelamento')
    axes[0].set_xlabel('Taxa de Cancelamento')
    
    sns.scatterplot(x='tempo_aprovacao_medio', y='taxa_cancelamento', data=analise, color='darkred', s=100, alpha=0.7, ax=axes[1])
    axes[1].set_title(f'Cancelamento vs Tempo de Aprovação (r={corr:.3f})')
    axes[1].set_xlabel('Tempo Médio Aprovação (h)')
    axes[1].set_ylabel('Taxa Cancelamento')
    axes[1].grid(True, linestyle='--', alpha=0.5)
    
    metricas = {
        'correlacao': corr,
        'categorias_analisadas': len(analise),
        'taxa_media_geral': analise['taxa_cancelamento'].mean() * 100,
        'tempo_medio_geral': validos['tempo_aprovacao_medio'].mean(),
    }
    return fig, metricas, analise

# ==============================================================================
# Q3 — RECORRÊNCIA DE CLIENTES
# ==============================================================================

def q3_recorrencia_clientes(df: pd.DataFrame):
    filtro = df[df['order_status'].isin(['delivered', 'shipped', 'processing', 'approved'])]
    filtro = filtro.sort_values(['customer_unique_id', 'order_purchase_timestamp'])
    
    compras = filtro.groupby('customer_unique_id').agg(
        total_compras=('order_id', 'nunique'),
        primeira=('order_purchase_timestamp', 'min'),
        ultima=('order_purchase_timestamp', 'max')
    ).reset_index()
    
    recorrentes = compras[compras['total_compras'] > 1]
    pct_rec = len(recorrentes) / len(compras) * 100 if len(compras) > 0 else 0
    
    tempos = []
    for cid in recorrentes['customer_unique_id']:
        datas = filtro[filtro['customer_unique_id'] == cid]['order_purchase_timestamp'].sort_values()
        deltas = datas.diff().dropna().dt.days
        tempos.extend(deltas.tolist())
    
    tempo_medio = np.mean(tempos) if tempos else 0
    tempo_mediana = np.median(tempos) if tempos else 0
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    dist = compras['total_compras'].value_counts().sort_index().head(10).reset_index()
    dist.columns = ['num_compras', 'qtd_clientes']
    sns.barplot(x='num_compras', y='qtd_clientes', data=dist, palette='mako', ax=axes[0])
    axes[0].set_yscale('log')
    axes[0].set_title('Distribuição de Compras por Cliente')
    axes[0].set_xlabel('Nº de Compras')
    axes[0].set_ylabel('Clientes (log)')
    
    if tempos:
        sns.histplot(tempos, bins=50, color='teal', kde=True, ax=axes[1])
        axes[1].axvline(tempo_medio, color='red', linestyle='--', label=f'Média: {tempo_medio:.1f}d')
        axes[1].axvline(tempo_mediana, color='orange', linestyle='--', label=f'Mediana: {tempo_mediana:.1f}d')
        axes[1].legend()
        axes[1].set_title('Tempo entre Compras — Recorrentes')
        axes[1].set_xlabel('Dias')
    
    metricas = {
        'total_clientes': len(compras),
        'recorrentes': len(recorrentes),
        'pct_recorrentes': pct_rec,
        'tempo_medio': tempo_medio,
        'tempo_mediana': tempo_mediana,
        'max_compras': int(compras['total_compras'].max()),
    }
    return fig, metricas, dist

# ==============================================================================
# Q4 — MIGRAÇÃO DE CATEGORIA
# ==============================================================================

def q4_migracao_categoria(df: pd.DataFrame):
    filtro = df[df['order_status'].isin(['delivered', 'shipped', 'processing', 'approved'])]
    filtro = filtro.sort_values(['customer_unique_id', 'order_purchase_timestamp'])
    
    primeira = filtro.groupby('customer_unique_id').first()[['product_category_name']].reset_index()
    primeira.columns = ['customer_unique_id', 'primeira_categoria']
    
    contagem = filtro.groupby('customer_unique_id')['order_id'].nunique().reset_index(name='total_compras')
    recorrentes = contagem[contagem['total_compras'] > 1]['customer_unique_id']
    
    df_rec = filtro[filtro['customer_unique_id'].isin(recorrentes)].merge(primeira, on='customer_unique_id')
    df_rec['migrou'] = df_rec['product_category_name'] != df_rec['primeira_categoria']
    
    migracao = df_rec.groupby('customer_unique_id')['migrou'].max().reset_index(name='migrou_de_categoria')
    migraram = migracao['migrou_de_categoria'].sum()
    ficaram = len(migracao) - migraram
    pct_migrou = (migraram / len(migracao)) * 100 if len(migracao) > 0 else 0
    
    # transições
    ultima = df_rec.groupby('customer_unique_id').last()[['primeira_categoria', 'product_category_name']].reset_index()
    ultima.columns = ['customer_unique_id', 'primeira_categoria', 'ultima_categoria']
    transicoes = ultima[ultima['primeira_categoria'] != ultima['ultima_categoria']]
    trans_top = transicoes.groupby(['primeira_categoria', 'ultima_categoria']).size().reset_index(name='contagem').sort_values('contagem', ascending=False).head(10)
    trans_top['transicao'] = trans_top['primeira_categoria'] + ' → ' + trans_top['ultima_categoria']
    
    # >>> AQUI: 2 linhas, 1 coluna — um abaixo do outro <<<
    fig, axes = plt.subplots(2, 1, figsize=(10, 14))
    
    colors = sns.color_palette("Set2", 2)
    axes[0].pie([ficaram, migraram], labels=['Fiéis', 'Migraram'], autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0].set_title('Fidelidade vs Migração de Categoria', fontsize=12, pad=20)
    
    if not trans_top.empty:
        sns.barplot(x='contagem', y='transicao', data=trans_top, palette='coolwarm', ax=axes[1])
        axes[1].set_title('Top 10 Transições de Categoria', fontsize=12, pad=20)
        axes[1].set_xlabel('Clientes')
        axes[1].set_ylabel('')
    else:
        axes[1].text(0.5, 0.5, 'Sem transições suficientes', ha='center', va='center', transform=axes[1].transAxes)
        axes[1].set_title('Top 10 Transições de Categoria')
    
    plt.tight_layout()
    
    metricas = {
        'clientes_recorrentes': len(migracao),
        'migraram': int(migraram),
        'ficaram': int(ficaram),
        'pct_migraram': pct_migrou,
        'top_transicao': trans_top.iloc[0]['transicao'] if not trans_top.empty else 'N/A',
    }
    return fig, metricas, trans_top

# ==============================================================================
# Q5 — FOTOS × PREÇO & VOLUME
# ==============================================================================

def q5_fotos_preco_volume(df: pd.DataFrame):
    df = df.dropna(subset=['product_photos_qty']).copy()
    df['product_photos_qty'] = df['product_photos_qty'].astype(int)
    
    analise = df.groupby('product_photos_qty').agg(
        preco_medio=('price', 'mean'),
        volume_vendas=('order_id', 'count'),
        produtos_distintos=('product_id', 'nunique')
    ).reset_index()
    analise = analise[analise['produtos_distintos'] >= 50]
    
    corr_preco = np.corrcoef(analise['product_photos_qty'].values, analise['preco_medio'].values)[0, 1]
    corr_vol = np.corrcoef(analise['product_photos_qty'].values, analise['volume_vendas'].values)[0, 1]
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    sns.barplot(x='product_photos_qty', y='preco_medio', data=analise, palette='viridis', ax=axes[0])
    axes[0].set_title('Preço Médio × Fotos')
    axes[0].set_xlabel('Qtd Fotos')
    
    sns.lineplot(x='product_photos_qty', y='volume_vendas', data=analise, marker='o', color='darkred', ax=axes[1])
    axes[1].set_title('Volume de Vendas × Fotos')
    axes[1].set_xlabel('Qtd Fotos')
    
    sns.scatterplot(x='product_photos_qty', y='preco_medio', size='volume_vendas', data=analise, sizes=(50, 500), ax=axes[2])
    axes[2].set_title('Preço vs Fotos (tamanho=volume)')
    
    metricas = {
        'corr_preco_fotos': corr_preco,
        'corr_volume_fotos': corr_vol,
        'faixa_fotos': f"{analise['product_photos_qty'].min()} a {analise['product_photos_qty'].max()}",
    }
    return fig, metricas, analise

# ==============================================================================
# Q6 — DISTRIBUIÇÃO DE ITENS POR PEDIDO
# ==============================================================================

def q6_itens_por_pedido(df: pd.DataFrame):
    itens = df[df['order_status'] == 'delivered']
    qtd = itens.groupby('order_id').size().reset_index(name='qtd_itens')
    
    total = len(qtd)
    pct_1 = (qtd['qtd_itens'] == 1).sum() / total * 100
    media = qtd['qtd_itens'].mean()
    mediana = qtd['qtd_itens'].median()
    
    fig, ax = plt.subplots()
    ax.hist(qtd['qtd_itens'], bins=range(1, 16), color='steelblue', edgecolor='black', alpha=0.8)
    ax.axvline(media, color='red', linestyle='--', label=f'Média: {media:.2f}')
    ax.set_title('Distribuição de Itens por Pedido')
    ax.set_xlabel('Qtd Itens')
    ax.set_ylabel('Pedidos')
    ax.legend()
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    metricas = {
        'total_pedidos': total,
        'pct_1_item': pct_1,
        'media_itens': media,
        'mediana_itens': mediana,
        'max_itens': int(qtd['qtd_itens'].max()),
    }
    return fig, metricas, qtd['qtd_itens'].value_counts().sort_index().reset_index()

# ==============================================================================
# Q7 — PREVER INSATISFAÇÃO (ML)
# ==============================================================================

def q7_prever_insatisfacao(df: pd.DataFrame):
    ped = df[df['order_delivered_customer_date'].notna()][[
        'order_id', 'customer_id', 'order_purchase_timestamp',
        'order_delivered_customer_date', 'order_estimated_delivery_date', 'review_score'
    ]].drop_duplicates('order_id')
    
    ped['tempo_entrega_dias'] = (ped['order_delivered_customer_date'] - ped['order_purchase_timestamp']).dt.days
    ped['atraso_dias'] = (ped['order_delivered_customer_date'] - ped['order_estimated_delivery_date']).dt.days
    
    base = ped.merge(df[['order_id', 'price', 'freight_value', 'product_id']].groupby('order_id').agg(
        preco_total=('price', 'sum'),
        frete_total=('freight_value', 'sum'),
        qtd_itens=('product_id', 'count')
    ).reset_index(), on='order_id')
    
    base = base.merge(df[['order_id', 'product_photos_qty']].groupby('order_id').mean().reset_index(), on='order_id', how='left')
    base = base.merge(df[['order_id', 'payment_installments']].drop_duplicates('order_id'), on='order_id', how='left')
    base = base.merge(df[['order_id', 'product_category_name']].drop_duplicates('order_id'), on='order_id', how='left')
    base = base.merge(df[['order_id', 'payment_type']].drop_duplicates('order_id'), on='order_id', how='left')
    
    base['insatisfeito'] = (base['review_score'] <= 2).astype(int)
    base['frete_ratio'] = base['frete_total'] / base['preco_total']
    base['frete_ratio'] = base['frete_ratio'].replace([np.inf, -np.inf], np.nan).fillna(0)
    base['parcelas'] = base['payment_installments'].fillna(1)
    base['payment_type'] = base['payment_type'].fillna('desconhecido')
    base['categoria'] = base['product_category_name'].fillna('sem_categoria')
    
    le_cat = LabelEncoder()
    le_pay = LabelEncoder()
    base['categoria_enc'] = le_cat.fit_transform(base['categoria'])
    base['payment_enc'] = le_pay.fit_transform(base['payment_type'])
    
    features = ['tempo_entrega_dias', 'atraso_dias', 'preco_total', 'frete_total',
                'frete_ratio', 'qtd_itens', 'product_photos_qty', 'parcelas',
                'categoria_enc', 'payment_enc']
    X = base[features].fillna(0)
    y = base['insatisfeito']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, max_depth=10)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    importancias = pd.DataFrame({'feature': features, 'importancia': rf.feature_importances_}).sort_values('importancia', ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.barplot(x='importancia', y='feature', data=importancias, palette='viridis', ax=axes[0])
    axes[0].set_title('Importância das Features — Random Forest')
    
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],
                xticklabels=['Satisfeito', 'Insatisfeito'],
                yticklabels=['Satisfeito', 'Insatisfeito'])
    axes[1].set_title('Matriz de Confusão')
    axes[1].set_ylabel('Real')
    axes[1].set_xlabel('Predito')
    
    prob = rf.predict_proba(X_test)[:, 1]
    
    metricas = {
        'acuracia': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'risco_alto_70': int((prob > 0.70).sum()),
        'top_feature': importancias.iloc[0]['feature'],
        'top_importancia': importancias.iloc[0]['importancia'],
    }
    return fig, metricas, importancias

# ==============================================================================
# Q8 — MATRIZ DE INTERVENÇÃO PRESCRITIVA (SELLERS)
# ==============================================================================

def q8_intervencao_sellers(df: pd.DataFrame):
    reviews_neg = df[df['review_score'].isin([1, 2])]
    seller_reviews = reviews_neg.groupby('seller_id')['review_score'].count().reset_index(name='bad_reviews')
    
    all_reviews = df.groupby('seller_id')['review_score'].mean().reset_index(name='nota_media')
    receita = df.groupby('seller_id')['price'].sum().reset_index(name='receita')
    
    frete = df.groupby('seller_id').apply(
        lambda x: (x['freight_value'].sum() / x['price'].sum()) if x['price'].sum() > 0 else 0
    ).reset_index(name='avg_frete_ratio')
    
    metrics = seller_reviews.merge(all_reviews, on='seller_id', how='outer').fillna({'bad_reviews': 0})
    metrics = metrics.merge(receita, on='seller_id', how='left').fillna({'receita': 0})
    metrics = metrics.merge(frete, on='seller_id', how='left').fillna({'avg_frete_ratio': 0})
    metrics['avg_frete_ratio'] = metrics['avg_frete_ratio'].replace([np.inf, -np.inf], 0)
    
    VOLUME_MIN = 5
    def acao(row):
        if row['bad_reviews'] >= VOLUME_MIN and row['avg_frete_ratio'] > 0.3 and row['nota_media'] < 3.0:
            return 'TREINAMENTO + SUSPENSÃO DESTAQUE'
        elif row['bad_reviews'] >= VOLUME_MIN and row['avg_frete_ratio'] > 0.3:
            return 'TREINAMENTO LOGÍSTICA'
        elif row['bad_reviews'] >= VOLUME_MIN and row['nota_media'] < 3.0:
            return 'SUSPENSÃO TEMPORÁRIA DESTAQUE'
        elif row['bad_reviews'] >= 10 and row['receita'] < 50 and row['nota_media'] < 2.5:
            return 'OFFBOARDING SUGERIDO'
        else:
            return 'MONITORAMENTO'
    
    metrics['acao_prescrita'] = metrics.apply(acao, axis=1)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    acao_counts = metrics['acao_prescrita'].value_counts().reset_index()
    acao_counts.columns = ['acao', 'qtd']
    cores = {'MONITORAMENTO': '#95A5A6', 'TREINAMENTO LOGÍSTICA': '#E67E22',
             'TREINAMENTO + SUSPENSÃO DESTAQUE': '#E74C3C', 'SUSPENSÃO TEMPORÁRIA DESTAQUE': '#F39C12',
             'OFFBOARDING SUGERIDO': '#8E44AD'}
    palette = [cores.get(a, '#3498DB') for a in acao_counts['acao']]
    sns.barplot(x='qtd', y='acao', data=acao_counts, palette=palette, ax=axes[0])
    axes[0].set_title('Distribuição de Sellers por Ação Prescrita')
    axes[0].set_xlabel('Qtd Sellers')
    
    criticos = metrics[metrics['acao_prescrita'] != 'MONITORAMENTO']
    if not criticos.empty:
        sns.scatterplot(data=criticos, x='avg_frete_ratio', y='nota_media',
                        hue='acao_prescrita', size='bad_reviews', sizes=(50, 400),
                        palette='deep', alpha=0.8, ax=axes[1])
        axes[1].axhline(3.0, color='red', linestyle='--', alpha=0.5)
        axes[1].axvline(0.3, color='orange', linestyle='--', alpha=0.5)
        axes[1].set_title('Sellers Críticos: Frete Ratio × Nota Média')
        axes[1].set_xlabel('Frete / Preço')
        axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    metricas = {
        'total_sellers': len(metrics),
        'com_acao_ativa': len(criticos),
        'pct_ativos': len(criticos) / len(metrics) * 100,
        'top_acao': acao_counts.iloc[0]['acao'],
    }
    return fig, metricas, metrics

# ==============================================================================
# Q9 — CONCENTRAÇÃO DE RISCO-RECEITA
# ==============================================================================

def q9_risco_receita(df: pd.DataFrame):
    receita_total = df['price'].sum()
    receita_seller = df.groupby('seller_id')['price'].sum().reset_index(name='receita')
    
    reviews_neg = df[df['review_score'].isin([1, 2])]
    bad = reviews_neg.groupby('seller_id')['review_score'].count().reset_index(name='bad_reviews')
    
    seller_risco = receita_seller.merge(bad, on='seller_id', how='outer').fillna(0)
    seller_risco['pct_receita'] = (seller_risco['receita'] / receita_total) * 100
    
    thresh_rev = seller_risco['bad_reviews'].quantile(0.90)
    thresh_rec = seller_risco['receita'].quantile(0.90)
    
    def quad(row):
        ar = row['bad_reviews'] >= thresh_rev
        af = row['receita'] >= thresh_rec
        if ar and af: return 'ALTO RISCO + ALTO FAT'
        elif ar and not af: return 'ALTO RISCO + BAIXO FAT'
        elif not ar and af: return 'BAIXO RISCO + ALTO FAT'
        else: return 'BAIXO RISCO + BAIXO FAT'
    
    seller_risco['quadrante'] = seller_risco.apply(quad, axis=1)
    
    palette_quad = {
        'ALTO RISCO + ALTO FAT': '#E74C3C', 'ALTO RISCO + BAIXO FAT': '#E67E22',
        'BAIXO RISCO + ALTO FAT': '#27AE60', 'BAIXO RISCO + BAIXO FAT': '#95A5A6'
    }
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    plot_data = seller_risco[seller_risco['bad_reviews'] > 0]
    sns.scatterplot(data=plot_data, x='bad_reviews', y='receita', hue='quadrante',
                    palette=palette_quad, size='receita', sizes=(30, 300),
                    alpha=0.75, edgecolor='black', linewidth=0.3, ax=axes[0])
    axes[0].axvline(thresh_rev, color='red', linestyle='--', alpha=0.5)
    axes[0].axhline(thresh_rec, color='green', linestyle='--', alpha=0.5)
    axes[0].set_title('Matriz de Risco: Sellers Tóxicos × Receita')
    axes[0].set_xlabel('Reviews Negativas')
    axes[0].set_ylabel('Receita (R$)')
    axes[0].set_yscale('log')
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    quad_counts = seller_risco['quadrante'].value_counts().reset_index()
    quad_counts.columns = ['quadrante', 'qtd']
    pal = [palette_quad[q] for q in quad_counts['quadrante']]
    sns.barplot(x='qtd', y='quadrante', data=quad_counts, palette=pal, ax=axes[1])
    axes[1].set_title('Sellers por Quadrante de Risco')
    axes[1].set_xlabel('Qtd Sellers')
    
    top10 = seller_risco[seller_risco['bad_reviews'] > 0].nlargest(10, 'bad_reviews')
    receita_top10 = top10['receita'].sum()
    
    metricas = {
        'receita_total': receita_total,
        'receita_top10_toxicos': receita_top10,
        'pct_top10_do_total': (receita_top10 / receita_total) * 100,
        'sellers_alto_risco_alto_fat': len(seller_risco[seller_risco['quadrante'] == 'ALTO RISCO + ALTO FAT']),
    }
    return fig, metricas, seller_risco
