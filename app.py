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

        # Filtrando os dados
        df_filtrado = df[df[col_lider] == lider_selecionado]

        # Exibição de Métricas (Cards)
        c1, c2, c3 = st.columns(3)
        c1.metric("Tamanho da Equipe", len(df_filtrado))
        c2.metric("Média de Notas", f"{df_filtrado[col_nota].mean():.1f}")
        
        # Gráfico de Barras
        st.subheader(f"Performance da Equipe: {lider_selecionado}")
        fig = px.bar(df_filtrado, 
                     x=col_nome, 
                     y=col_nota, 
                     color=col_nota,
                     color_continuous_scale='Reds',
                     labels={col_nota: 'Nota', col_nome: 'Promotor'})
        
        st.plotly_chart(fig, use_container_width=True)

        # Tabela com os dados brutos
        with st.expander("Visualizar planilha da equipe"):
            st.write(df_filtrado)

    except Exception as e:
        st.error(f"Erro ao processar as colunas: {e}")
        st.info("Verifique se o arquivo 'dados2_lideranca.csv' está na mesma pasta do código.")
