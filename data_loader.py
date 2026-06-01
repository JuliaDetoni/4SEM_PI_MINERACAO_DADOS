# data_loader.py
import streamlit as st
import pandas as pd
from config import DATASETS

@st.cache_data(ttl=3600, show_spinner="Carregando datasets...")
def load_all_data():
    """
    Carrega todos os datasets do GitHub raw.
    Retorna dict com dataframes.
    """
    dfs = {}
    for name, url in DATASETS.items():
        dfs[name] = pd.read_csv(url)
    return dfs

@st.cache_data(ttl=3600)
def load_single_dataset(name: str):
    """Lazy load: carrega só um dataset sob demanda."""
    return pd.read_csv(DATASETS[name])
