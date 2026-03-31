import streamlit as st
import pandas as pd

# 1. Configuração da página e Estilo CSS para design profissional
st.set_page_config(page_title="Portal de Resultados | 3 Corações", layout="wide")

st.markdown("""
    <style>
    /* Cor de destaque da 3 Corações e fontes */
    .main { background-color: #f8f9fa; }
    h1 { color: #c30c15; font-weight: 800; }
    .stButton>button { 
        background-color: #c30c15; 
        color: white; 
        font-weight: bold; 
        border-radius: 8px;
        height: 3em;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #9d0a11; border: none; }
    /* Estilização das métricas */
    [data-testid="stMetricValue"] { color: #c30c15; font-size: 32px; }
    [data-testid="stMetricLabel"] { font-size: 16px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dados2_lideranca.csv', sep=';', encoding='latin-1', on_bad_lines='skip', engine='python')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return None

df = load_data()

# --- CABEÇALHO COM LOGO AO LADO DO TÍTULO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Logo oficial da 3 Corações
    st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=120)
with col_titulo:
    st.write("##") # Ajuste de altura
    st.title("Portal de Resultados e Performance")

st.markdown("---")

# --- ÁREA DE CONSULTA ---
# Usando a matrícula fictícia como exemplo no placeholder
col_input, col_btn = st.columns([3, 1])
with col_input:
    matricula_input = st.text_input(
        "Identificação do Supervisor", 
        placeholder="Exemplo: 1-38013", 
        help="Insira a matrícula completa para visualizar os indicadores da equipe."
    ).strip()

with col_btn:
    st.write("##") # Alinhamento vertical
    botao_consultar = st.button("CONSULTAR RESULTADOS")

# --- LÓGICA DE EXIBIÇÃO ---
if (botao_consultar or matricula_input) and df is not None:
    try:
        # Mapeamento de colunas
        col_id = [c for c in df.columns if 'MATRICULA' in c and 'LIDER' in c][0]
        col_lider_nome = 'LIDERANCA' 
        col_mes = df.columns[0] # Primeira coluna da planilha
        col_total_receber = 'TOTAL A RECEBER'

        # Filtro
        df_lider = df[df[col_id].astype(str).str.strip() == matricula_input].copy()

        if not df_lider.empty:
            nome_supervisor = str(df_lider[col_lider_nome].iloc[0])
            
            # Cabeçalho do Resultado
            st.subheader(f"👤 Supervisor(a): {nome_supervisor}")
            
            # Filtro de Mês na Sidebar
            meses_lista = sorted(df_lider[col_mes].unique())
            mes_sel = st.sidebar.selectbox("📅 Selecione o Período", meses_lista)
            
            df_final = df_lider[df_lider[col_mes] == mes_sel].copy()

            # Tratamento de Moeda
            def format_money(valor):
                v = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
                try: return float(v)
                except: return 0.0

            df_final[col_total_receber] = df_final[col_total_receber].apply(format_money)

            # --- MÉTRICAS EM CARDS ---
            st.markdown("### Resumo de Performance")
            m1, m2, m3 = st.columns(3)
            
            total_equipe = len(df_final)
            valor_total = df_final[col_total_receber].sum()
            media_lc = pd.to_numeric(df_final['NOTA LOJA DO CORAÇÃO'].str.replace(',', '.'), errors='coerce').mean()

            m1.metric("Total da Equipe", f"{total_equipe} Promotores")
            m2.metric("Média Nota LC", f"{media_lc:.1f}")
            # Formatação manual para Real (R$)
            m3.metric("Total a Receber", f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

            # --- TABELA DETALHADA (SEM GRÁFICO) ---
            st.markdown("---")
            st.markdown(f"### 📋 Detalhamento Geral - Equipe {nome_supervisor} ({mes_sel})")
            
            ordem_solicitada = [
                'LIDERANCA', col_mes, 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                'PONTO NATURAL', 'RUPTURA', 'MPDV'
            ]
            
            colunas_finais = [c for c in ordem_solicitada if c in df_final.columns]
            
            # Estilização da tabela para ocupar a largura total
            st.dataframe(df_final[colunas_finais], use_container_width=True, hide_index=True)

        else:
            st.error(f"❌ Matrícula '{matricula_input}' não localizada na base de dados atual.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {e}")
