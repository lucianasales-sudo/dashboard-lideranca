import streamlit as st
import pandas as pd

# 1. Configuração de Estilo e Página
st.set_page_config(page_title="Portal de Gestão | 3 Corações", layout="wide", page_icon="☕")

# CSS PREMIUM (Fontes Inter, Cores Slate/Coffee e Design Responsivo)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* Cabeçalho */
    .header-container {
        display: flex; flex-direction: column; align-items: center;
        text-align: center; padding: 10px 0px 20px 0px; width: 100%;
    }
    .logo-img { width: 60px; height: auto; margin-bottom: 10px; }
    
    .main-title { 
        color: #1e293b !important; font-size: 18px; font-weight: 800; 
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    
    .sub-header { color: #64748b !important; font-size: 13px; margin-top: 4px; }

    /* Cards de Resumo */
    .metric-card {
        background-color: #ffffff !important; 
        border: 1px solid #f1f5f9 !important;
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        text-align: center;
    }
    .metric-label { color: #64748b !important; font-size: 12px; text-transform: uppercase; font-weight: 600; }
    .metric-value { color: #8B4513 !important; font-size: 24px; font-weight: 800; display: block; margin-top: 5px; }

    /* Tabela customizada */
    .stDataFrame { border: 1px solid #f1f5f9 !important; border-radius: 12px !important; }

    /* Botão e Input */
    .stButton>button {
        width: 100% !important; border-radius: 8px !important; 
        background-color: #8B4513 !important; color: white !important;
        border: none !important; padding: 12px !important; font-weight: 600 !important;
    }
    input { border-radius: 8px !important; border: 1px solid #e2e8f0 !important; }

    @media (max-width: 640px) { .block-container { padding: 1rem !important; } }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE LIMPEZA ---
def limpar_valor(v):
    if pd.isna(v) or str(v).strip() in ['0','0,00','-','R$ -']: return 0.0
    val = str(v).replace('R','').replace('$','').replace('.','').replace(',','.').strip()
    try: return float(val)
    except: return 0.0

def f_rs(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def load():
    try:
        df = pd.read_csv("dados2_lideranca.csv", sep=';', encoding='latin-1', on_bad_lines='skip', engine='python')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except: return None

df = load()

# --- INTERFACE ---
st.markdown(f"""
    <div class="header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/63/Logo_grupo_3_cora%C3%A7%C3%B5es.png" class="logo-img">
        <div class="main-title">GESTÃO DE RESULTADOS</div>
        <p class="sub-header">Painel Administrativo para Supervisores</p>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    # Área de Busca Centralizada
    _, col_busca, _ = st.columns([0.1, 0.8, 0.1])
    with col_busca:
        matricula_input = st.text_input("Matrícula do Supervisor:", placeholder="Ex: 1-38013").strip()
        consultar = st.button("ACESSAR EQUIPE")

    if (consultar or matricula_input) and matricula_input:
        # Mapeamento de Colunas (IDs e Nomes)
        col_id = [c for c in df.columns if 'MATRICULA' in c and 'LIDER' in c][0]
        col_lider_nome = 'LIDERANCA' 
        col_mes = df.columns[0] # Assume a primeira coluna como Mês
        col_total = 'TOTAL A RECEBER'
        col_nota = [c for c in df.columns if 'NOTA' in c and 'CORA' in c][0]

        # Filtro Inicial
        df_lider = df[df[col_id].astype(str).str.strip() == matricula_input].copy()

        if not df_lider.empty:
            nome_sup = str(df_lider[col_lider_nome].iloc[0])
            st.markdown(f"### 👤 Supervisor: **{nome_sup}**")

            # Filtro de Mês na Sidebar
            meses = sorted(df_lider[col_mes].unique())
            mes_sel = st.sidebar.selectbox("📅 Selecione o Mês", meses)
            
            df_final = df_lider[df_lider[col_mes] == mes_sel].copy()

            # Processamento de Valores
            df_final[col_total] = df_final[col_total].apply(limpar_valor)
            df_final['NOTA_NUM'] = pd.to_numeric(df_final[col_nota].astype(str).str.replace(',','.'), errors='coerce').fillna(0)

            # --- MÉTRICAS EM CARDS ---
            st.write("")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <span class="metric-label">Equipe</span>
                    <span class="metric-value">{len(df_final)}</span>
                </div>""", unsafe_allow_html=True)
            
            with c2:
                media_lc = df_final['NOTA_NUM'].mean()
                st.markdown(f"""<div class="metric-card">
                    <span class="metric-label">Média Nota LC</span>
                    <span class="metric-value">{media_lc:.1f}</span>
                </div>""", unsafe_allow_html=True)
            
            with c3:
                soma_total = df_final[col_total].sum()
                st.markdown(f"""<div class="metric-card">
                    <span class="metric-label">Total Premiação</span>
                    <span class="metric-value">{f_rs(soma_total)}</span>
                </div>""", unsafe_allow_html=True)

            # --- TABELA DE EQUIPE (O CORAÇÃO DO DASHBOARD) ---
            st.write("")
            st.markdown(f"#### 📋 Detalhamento da Equipe - {mes_sel}")
            
            # Ordem das 21 colunas solicitadas
            ordem = [
                'LIDERANCA', col_mes, 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                'PONTO NATURAL', 'RUPTURA', 'MPDV'
            ]
            
            colunas_finais = [c for c in ordem if c in df_final.columns]
            
            # Exibição da Tabela Profissional
            st.dataframe(
                df_final[colunas_finais], 
                use_container_width=True, 
                hide_index=True
            )

        else:
            st.error("Matrícula não localizada na base de dados.")
else:
    st.error("Erro ao carregar o arquivo 'dados2_lideranca.csv'.")
