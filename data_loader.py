# data_loader.py
import os
import streamlit as st
import pandas as pd
from config import DATASETS, BASE_URL

# Detecta se estamos no Streamlit Cloud (repo clonado) ou local
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

def _get_file_path(name: str) -> str:
    """
    Tenta caminho local primeiro (dataset/ na raiz do repo).
    Se não existir, retorna URL raw do GitHub.
    """
    local_path = os.path.join(REPO_ROOT, "dataset", f"olist_{name}_dataset.csv")
    if os.path.exists(local_path):
        return local_path
    return DATASETS[name]

@st.cache_data(ttl=3600, show_spinner="Carregando datasets...")
def load_all_data():
    dfs = {}
    for name in DATASETS.keys():
        path = _get_file_path(name)
        try:
            dfs[name] = pd.read_csv(path)
        except Exception as e:
            st.error(f"Erro ao carregar `{name}` de: {path}")
            raise e
    return dfs

@st.cache_data(ttl=3600)
def load_single_dataset(name: str):
    path = _get_file_path(name)
    return pd.read_csv(path)
