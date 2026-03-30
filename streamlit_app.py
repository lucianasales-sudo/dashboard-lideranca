import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Liderança", layout="wide")

@st.cache_data
def load_data():
    # Tenta ler o arquivo ignorando erros de caracteres especiais
    try:
        df = pd.read_csv('dados2_lideranca.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
        # Limpa os nomes das colunas (tira espaços e lixo)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro crítico na leitura do arquivo: {e}")
        return None

df = load_data()

if df is not None:
    st.title("📊 Painel de Resultados - 3 Corações")
    
    # Procura as colunas certas mesmo que o nome tenha mudado (ex: LIDERANÇA vs LIDERANCA)
    col_lider = [c for c in df.columns if 'LIDER' in c][0]
    col_nota = [c for c in df.columns if 'NOTA' in c][0]
    col_nome = [c for c in df.columns if 'NOME RH' in c or 'NOME INVOLVES' in c][0]

    # Ajusta a nota para número (trata a vírgula)
    df[col_nota] = df[col_nota].astype(str).str.replace(',', '.')
    df[col_nota] = pd.to_numeric(df[col_nota], errors='coerce').fillna(0)

    # Filtro de Supervisor
    lista_lideres = sorted(df[col_lider].unique())
    lider = st.sidebar.selectbox("Selecione o Supervisor", lista_lideres)
    
    df_filtrado = df[df[col_lider] == lider]

    # Exibição
    c1, c2 = st.columns(2)
    c1.metric("Equipe", len(df_filtrado))
    c2.metric("Média Nota", f"{df_filtrado[col_nota].mean():.1f}")

    fig = px.bar(df_filtrado, x=col_nome, y=col_nota, 
                 title=f"Desempenho da Equipe - {lider}",
                 color_discrete_sequence=['#FF4B4B'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### Dados Detalhados")
    st.dataframe(df_filtrado)
else:
    st.warning("Aguardando carregamento do ficheiro...")
