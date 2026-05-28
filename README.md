# 📊 Análise de E-commerce da OLIST no Brasil (2016–2018)

> **Projeto Integrador — 4º Semestre**  
> **Disciplina:** Mineração de Dados  
> **Curso:** Tecnologia em Análise e Desenvolvimento de Sistemas  
> **Instituição:** SENAC EAD

---

## 👥 Integrantes do Grupo

| Nome | Função |
|---|---|
| **Douglas** Netizke da Silva | Análise & Documentação |
| **Ingrid** Couto Rosin | Análise Exploratória |
| **Juliano** Detoni | Estratégia de Negócio & Visualização |
| **Patrick** Jose Ranel Penna | Modelagem & Validação |

---

## 🎯 Objetivo do Projeto

Construir uma **prova de conceito de inteligência de negócio** que transforme dados brutos do marketplace Olist em **insights acionáveis para tomada de decisão**.

A persona adotada é a de um **Analista de Estratégia do Marketplace Olist**, cujo objetivo é aumentar a receita da plataforma, reter os melhores vendedores e reduzir atrito operacional.

---

## 🗂️ Fonte de Dados

Utilizamos o dataset público e anonimizado da **Olist**, disponível no Kaggle, que contém dados reais de e-commerce brasileiro entre 2016 e 2018.

- **🔗 Kaggle Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **📁 Repositório de Dados:** [4SEM_PI_MINERACAO_DADOS](https://github.com/JuliaDetoni/4SEM_PI_MINERACAO_DADOS)
- **💻 Notebook Colab:** [PI_4SEM_T01](https://colab.research.google.com/drive/1uYfbpZn7FhmI3rKJBVb5sHORElcIq1uR)

O dataset é composto por **9 tabelas relacionais**:

| Tabela | Descrição |
|---|---|
| `olist_customers_dataset.csv` | Dados dos clientes |
| `olist_geolocation_dataset.csv` | Coordenadas geográficas |
| `olist_order_items_dataset.csv` | Itens de cada pedido |
| `olist_order_payments_dataset.csv` | Formas e parcelas de pagamento |
| `olist_order_reviews_dataset.csv` | Avaliações e notas de review |
| `olist_orders_dataset.csv` | Pedidos, status e datas |
| `olist_products_dataset.csv` | Categorias e atributos dos produtos |
| `olist_sellers_dataset.csv` | Dados dos vendedores |
| `product_category_name_translation.csv` | Tradução EN → PT das categorias |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3** — linguagem principal
- **Pandas** — manipulação e análise de dados
- **NumPy** — computação numérica e estatísticas
- **Matplotlib** — visualizações base (exigência da rubrica)
- **Seaborn** — visualizações estilizadas e apresentáveis
- **Google Colab** — ambiente de execução em nuvem
- **GitHub** — versionamento e compartilhamento de dados

---

## 🔍 Perguntas de Negócio & Visualizações

Foram desenvolvidas **6 análises estratégicas**, cada uma com **versão Seaborn** (apresentação) e **versão Matplotlib puro** (conformidade com rubrica).

### 1. Top 10 Categorias por Receita *(Barras Horizontais)*
**Pergunta:** Quais categorias de produtos geram mais receita?  
**Decisão:** Alocar orçamento de marketing digital e esforços de aquisição de sellers para as categorias mais rentáveis, em vez de distribuir igualmente.

---

### 2. Taxa de Cancelamento por Categoria × Tempo de Aprovação *(Barras + Scatter)*
**Pergunta:** Quais categorias têm maior taxa de cancelamento? Isso correlaciona com o tempo entre compra e aprovação do pagamento?  
**Decisão:** Priorizar revisão do processo de antifraude e meios de pagamento para categorias com alta taxa de cancelamento + tempo de aprovação longo. O cliente pode estar desistindo enquanto espera confirmação.

---

### 3. Recorrência de Clientes *(Barras + Histograma)*
**Pergunta:** Quantos clientes compram mais de uma vez? Qual o tempo médio entre compras?  
**Decisão:** Calibrar o CRM para disparar remarketing no momento exato antes da próxima compra esperada. No e-commerce brasileiro, recorrência é rara — saber o intervalo médio define o orçamento de retenção vs. aquisição.

---

### 4. Migração de Categoria por Clientes Recorrentes *(Pizza + Barras)*
**Pergunta:** Clientes recorrentes migram de categoria (ex: primeiro compra moda, depois eletro) ou ficam fiéis à mesma?  
**Decisão:** Se migram, montar jornadas de cross-sell sequenciais. Se ficam fiéis, investir em upsell e fidelização dentro do nicho. Isso define se o algoritmo de recomendação deve explorar diversidade ou profundidade.

---

### 5. Fotos do Produto × Preço & Volume *(Barras + Linha + Scatter)*
**Pergunta:** Produtos com mais fotos (`product_photos_qty`) têm preço médio maior ou menor volume de vendas?  
**Decisão:** Criar programa de capacitação em fotografia para sellers e incentivar produtos com 3+ fotos via destaque no ranking. Fotos são o principal ativo de conversão em e-commerce.

---

### 6. Distribuição de Itens por Pedido *(Histograma)*
**Pergunta:** Qual a distribuição de itens mais vendidos por pedido?  
**Decisão:** Desenvolver pop-up de "quem comprou isto também comprou" no checkout. A maioria dos pedidos tem apenas 1 item, indicando cross-selling subutilizado.

---

## 📁 Estrutura do Repositório

```
4SEM_PI_MINERACAO_DADOS/
├── dataset/
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
├── pi_4sem_t01.py          # Notebook principal (Python script)
└── README.md               # Este arquivo
```

---

## 🚀 Como Executar

### Opção 1: Google Colab (Recomendado)
1. Acesse o notebook: [PI_4SEM_T01 no Colab](https://colab.research.google.com/drive/1uYfbpZn7FhmI3rKJBVb5sHORElcIq1uR)
2. O script clona automaticamente este repositório e carrega os datasets.
3. Execute célula por célula (`Runtime > Run all` ou `Ctrl+F9`).

### Opção 2: Ambiente Local (Jupyter Notebook)
```bash
# 1. Clone o repositório
git clone https://github.com/JuliaDetoni/4SEM_PI_MINERACAO_DADOS.git
cd 4SEM_PI_MINERACAO_DADOS

# 2. Instale as dependências
pip install pandas numpy matplotlib seaborn

# 3. Abra no Jupyter
jupyter notebook pi_4sem_t01.py
```

---

## 📈 Principais Insights

| Insight | Impacto de Negócio |
|---|---|
| A maioria dos pedidos contém apenas **1 item** | Oportunidade de cross-selling no checkout |
| **Taxa de cancelamento** varia drasticamente por categoria | Necessidade de ajustar antifraude por vertical |
| **Recorrência de clientes** é baixa no e-commerce brasileiro | Foco em retenção via CRM automatizado |
| **Clientes recorrentes tendem a migrar** de categoria | Algoritmo de recomendação deve priorizar diversidade |
| **Produtos com mais fotos** apresentam maior volume de vendas | Incentivo a sellers para melhorar qualidade visual |

---

## 📚 Referências

- Olist. *Brazilian E-Commerce Public Dataset*. Kaggle, 2018. Disponível em: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- SENAC EAD. *Projeto Integrador — Mineração de Dados*. 4º Semestre, TADS.
- McKinsey & Company. *The value of data-driven decision making*. 2021.

---

## 📝 Licença

Este projeto é de caráter acadêmico. Os dados utilizados são públicos e anonimizados, disponibilizados pela Olist sob licença aberta no Kaggle.

---

<p align="center">
  <strong>Desenvolvido com 💜 pelo Grupo Olist Analytics — SENAC EAD 2026</strong>
</p>
