# OLIST BI — Mineração de Dados & Análise Prescritiva
---
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](COLOQUE_AQUI_O_LINK_DO_SEU_APP)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


> **Projeto Integrador — 4º Semestre**  
> Mineração de Dados com Python, Pandas, Scikit-Learn & Streamlit  
> Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
> Colab: [PI_4SEM_T01](PI_4SEM_T01)

## Integrantes

| Nome | Função |
|------|--------|
| **Douglas Netizke da Silva** | 
| **Ingrid Couto Rosin** |
| **Juliano Detoni** | 
| **Patrick Jose Rangel Penna** |


---

## Acesse a aplicação

🔗 **[Clique aqui para abrir o dashboard interativo](COLOQUE_AQUI_O_LINK_DO_SEU_APP)**

O BI foi construído em **Streamlit** e reflete fielmente a análise executada no Jupyter Notebook, com:
- ETL documentado e auditável (zero perda de registros)
- 9 perguntas de negócio respondidas com visualizações interativas
- Modelo de Machine Learning (Random Forest) para previsão de insatisfação
- Matriz prescritiva de intervenção em sellers
- Relatórios de dados expansíveis e download de CSVs

---

## Sumário

- [Contexto & Objetivo](#-contexto--objetivo)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Tecnologias](#-tecnologias)
- [ETL & Governança de Dados](#-etl--governança-de-dados)
- [Perguntas de Negócio](#-perguntas-de-negócio)
- [Como executar localmente](#-como-executar-localmente)
- [Deploy no Streamlit Cloud](#-deploy-no-streamlit-cloud)
- [Equipe](#-equipe)
- [Licença](#-licença)

---

## Contexto & Objetivo

**Persona:** Analista de Estratégia do Marketplace Olist  
**Objetivo:** Ajudar a empresa a aumentar a receita, retendo os melhores vendedores e reduzindo a insatisfação do cliente.

A partir de dados públicos e anonimizados de e-commerce brasileiro (2016–2018), este projeto aplica técnicas de **mineração de dados descritiva, diagnóstica, preditiva e prescritiva** para subsidiar decisões operacionais e estratégicas.

---

## Arquitetura do Projeto

```
olist-bi-streamlit/
├── app.py                 # Interface Streamlit (navegação, layout, widgets)
├── config.py              # URLs dos datasets (GitHub raw / caminho local)
├── data_loader.py         # Carregamento com @st.cache_data (local-first)
├── etl.py                 # Transformações globais, merges e feature engineering
├── queries.py             # 9 funções de análise (Q1–Q9) + modelos ML
├── requirements.txt       # Dependências Python
├── dataset/               # 9 arquivos CSV do Olist (não versionados no GitHub se >100MB)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_sellers_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   └── olist_closed_deals_dataset.csv  (se aplicável)
└── README.md              # Este arquivo
```

---

## Tecnologias

| Camada | Stack |
|--------|-------|
| **Linguagem** | Python 3.10+ |
| **Processamento** | Pandas, NumPy |
| **Visualização** | Matplotlib, Seaborn |
| **Machine Learning** | Scikit-Learn (Random Forest, Logistic Regression) |
| **Dashboard** | Streamlit |
| **Deploy** | Streamlit Community Cloud (free tier) |
| **Versionamento** | Git + GitHub |

---

## ETL & Governança de Dados

O pipeline segue quatro princípios rigorosos:

| Princípio | Aplicação |
|-----------|-----------|
| **Zero-Loss** | Nenhuma linha removida do dataset original (~100k pedidos preservados) |
| **Semântica** | Valores imputados refletem o estado real de negócio (ex: sem foto = 0 fotos; à vista = 1 parcela) |
| **Transparência** | Todo campo alterado é reportado em log de auditoria |
| **Datas preservadas** | Nulos em datas de entrega significam "pedido não entregue" — não são imputados para não distorcer KPIs logísticos |

**Transformações principais:**
- `product_photos_qty`: NaN → `0`
- `product_category_name`: NaN → `"sem_categoria"`
- `product_weight_g` / dimensões: NaN → mediana da categoria
- `payment_installments`: NaN → `1` (à vista)
- Conversão de timestamps para `datetime64` (sem imputação)

---

## Perguntas de Negócio

| # | Pergunta | Tipo de Análise | Técnicas | Justificativa da Técnica / Apoio à Decisão |
|---|----------|-----------------|----------|------------------------------------------|
| **Q1** | Quais categorias geram mais receita? | Descritiva | GroupBy, barras horizontais | Barras horizontais ordenadas por magnitude permitem identificar, em um único olhar, a concentração de faturamento e a dependência de nichos. Subsidiar decisões de alocação de recursos de aquisição de sellers. |
| **Q2** | Quais categorias têm maior taxa de cancelamento? Correlaciona com tempo de aprovação? | Diagnóstica | Correlação de Pearson, scatter plot | O scatter plot testa hipóteses de causalidade visualmente: se o tempo de processamento de pagamento for fator de desistência, a empresa pode priorizar a revisão operacional do checkout nessas verticais. |
| **Q3** | Quantos clientes compram mais de uma vez? Qual o tempo médio entre compras? | Descritiva | Recorrência, distribuição log, histograma | A escala logarítmica revela a raridade da recorrência; o histograma de intervalos expõe a bimodalidade do comportamento (impulso vs. relembrança), definindo a janela temporal para disparo de remarketing. |
| **Q4** | Clientes recorrentes migram de categoria ou ficam fiéis? | Comportamental | Transições de estado, pizza, barras | A pizza sintetiza o comportamento geral; as barras detalham o caminho mais frequente entre verticais. Orienta se o algoritmo de recomendação deve priorizar profundidade no nicho ou diversificação sequencial (cross-sell). |
| **Q5** | Produtos com mais fotos têm preço médio maior ou menor volume? | Diagnóstica | Correlação, dual-axis, scatter | Três visualizações simultâneas revelam duas correlações divergentes: preço positivo com fotos, volume negativo. Compreende se o investimento em fotografia sustenta valor percebido ou impulsa giro de vendas, orientando programa de capacitação de sellers. |
| **Q6** | Qual a distribuição de itens por pedido? | Descritiva | Histograma, estatísticas de cauda longa | A forma assimétrica positiva com moda em 1 revela a predominância de pedidos unitários e a cauda longa de compras múltiplas. Quantifica o gap de cross-selling na plataforma e estima o potencial de aumento de ticket médio via mecanismos de recomendação no checkout. |
| **Q7** | É possível prever insatisfação antes da avaliação? | **Preditiva** | Random Forest, Logistic Regression, matriz de confusão | Random Forest captura relações não-lineares entre variáveis operacionais (tempo de entrega, frete, parcelas) e insatisfação. A matriz de confusão quantifica o erro do modelo, avaliando se a precisão é suficiente para operacionalização como sistema de alerta preemptivo. |
| **Q8** | Qual ação operacional para sellers com alto volume de avaliações negativas? | **Prescritiva** | Regras de negócio, matriz de intervenção, quadrantes | A matriz de intervenção classifica sellers automaticamente por prioridade (treinamento, suspensão de destaque, offboarding) com base em thresholds de frete desproporcional e nota média. Automatiza decisões operacionais sem análise manual caso a caso. |
| **Q9** | Quanto da receita está concentrada em sellers tóxicos? | **Prescritiva** | Scatter log, quadrantes risco-receita, Pareto | A escala log acomoda a cauda longa da receita; os quadrantes separam players estratégicos de descartáveis. Quantifica o impacto financeiro de intervenções punitivas, evitando decisões que comprometam o P&L da plataforma. |

---

## Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/JuliaDetoni/4SEM_PI_MINERACAO_DADOS.git
cd 4SEM_PI_MINERACAO_DADOS
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o Streamlit

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`.

> **Nota sobre os dados:**  
> Os 9 arquivos CSV do Olist devem estar na pasta `dataset/` na raiz do projeto.  
> Se estiverem no GitHub, o `data_loader.py` detecta automaticamente e faz fallback para download via URL raw.

---

## Deploy no Streamlit Cloud

1. Faça push do código para o GitHub (incluindo `requirements.txt` e `app.py`)
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e selecione o branch `main`
4. Aponte o arquivo principal: `app.py`
5. Clique em **Deploy**

**Dicas de performance:**
- O Streamlit Cloud free tier oferece ~1GB de RAM
- Os datasets (~190MB de CSV) são lidos do disco local (repo clonado), não via internet
- O cache `@st.cache_data` evita reprocessamento a cada interação do usuário

---



## Licença

Este projeto é acadêmico e utiliza dados públicos do Olist sob licença aberta.  
Código-fonte disponível sob [MIT License](LICENSE).

---

> *"Dados sem contexto são apenas números. Mineração de dados é dar voz aos números."*  
> — Projeto Integrador, 4º Semestre.
