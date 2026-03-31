import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Liderança 3 Corações", layout="wide")

@st.cache_data
def load_data():
    try:
        # Tenta ler o arquivo com o padrão do Excel (latin-1)
        # on_bad_lines='skip' pula a linha 93 que estava com erro
        df = pd.read_csv('dados2_lideranca.csv', 
                         sep=';', 
                         encoding='latin-1', 
                         on_bad_lines='skip', 
                         engine='python')
        
        # Limpa espaços e coloca nomes das colunas em MAIÚSCULO
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# Carregando os dados
df = load_data()

if df is not None:
    st.title("📊 Painel de Performance - Supervisores")
    st.markdown("---")

    try:
        # Identifica as colunas mesmo que tenham nomes levemente diferentes
        col_lider = [c for c in df.columns if 'LIDER' in c][0]
        col_nota = [c for c in df.columns if 'NOTA' in c][0]
        col_nome = [c for c in df.columns if 'NOME RH' in c or 'NOME INVOLVES' in c][0]

        # Limpa a coluna de Notas (transforma vírgula em ponto e vira número)
        df[col_nota] = df[col_nota].astype(str).str.replace(',', '.')
        df[col_nota] = pd.to_numeric(df[col_nota], errors='coerce').fillna(0)

        # Filtro na Barra Lateral
        st.sidebar.header("Filtros")
        lista_lideres = sorted(df[col_lider].unique())
        lider_selecionado = st.sidebar.selectbox("Escolha o Supervisor", lista_lideres)

        # Filtr
