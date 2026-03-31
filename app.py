import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Portal de Performance - 3 Corações", layout="wide")

# Estilo CSS para melhorar o visual
st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #FF4B4B; color: white; border-radius: 5px; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Carregamento com tratamento de erros de encoding e linhas ruins
        df = pd.read_csv('dados2_lideranca.csv', 
                         sep=';', 
                         encoding='latin-1', 
                         on_bad_lines='skip', 
                         engine='python')
        # Limpa espaços e padroniza para maiúsculas
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

df = load_data()

# --- CABEÇALHO ---
st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=120)
st.title("📊 Portal de Resultados")

# --- ÁREA DE BUSCA ---
col_busca1, col_busca2 = st.columns([3, 1])
with col_busca1:
    matricula_input = st.text_input("Digite a Matrícula do Supervisor:", placeholder="Ex: 1-38013")
with col_busca2:
    st.write("##") # Espaçador
    botao_consultar = st.button("CONSULTAR")

st.markdown("---")

if (botao_consultar or matricula_input) and df is not None:
    # 1. Identificar colunas dinamicamente
    try:
        col_lider = 'LIDERANCA'
        col_mes = 'MÊS'
        col_nome_rh = 'NOME RH'
        col_total_receber = 'TOTAL A RECEBER'
        
        # Tratamento da coluna de valores (Total a Receber)
        df[col_total_receber] = df[col_total_receber].astype(str).str.replace('R$', '').str.replace('.', '').str.replace(',', '.')
        df[col_total_receber] = pd.to_numeric(df[col_total_receber], errors='coerce').fillna(0)

        # 2. Filtrar pela Matrícula
        # Aqui comparamos a entrada com a coluna LIDERANCA
        df_lider = df[df[col_lider].astype(str).str.contains(matricula_input.strip(), na=False)]

        if not df_lider.empty:
            # Pegamos o nome do Supervisor (ajuste o índice se o nome estiver em outra coluna)
            # Se a coluna LIDERANCA já contém o nome (ex: "1-38013 - NOME"), ele aparecerá completo
            nome_supervisor = df_lider[col_lider].iloc[0]
            
            st.header(f"👤 Supervisor: {nome_supervisor}")

            # 3. Filtro de Mês na Barra Lateral
            meses_disponiveis = sorted(df_lider[col_mes].unique())
            mes_selecionado = st.sidebar.selectbox("📅 Selecione o Mês", meses_disponiveis)
            
            # Filtro Final (Matrícula + Mês)
            df_final = df_lider[df_lider[col_mes] == mes_selecionado]

            # 4. Métricas
            c1, c2 = st.columns(2)
            c1.metric("Equipe no Mês", len(df_final))
            total_pagar = df_final[col_total_receber].sum()
            c2.metric("Total a Receber (Equipe)", f"R$ {total_pagar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

            # 5. Gráfico de Barras - TOTAL A RECEBER
            st.subheader(f"Distribuição de Premiação - {mes_selecionado}")
            
            fig = px.bar(df_final, 
                         x=col_nome_rh, 
                         y=col_total_receber,
                         text=col_total_receber, # Adiciona o rótulo de dados
                         color=col_total_receber,
                         color_continuous_scale='Reds',
                         labels={col_total_receber: 'Total a Receber (R$)', col_nome_rh: 'Promotor'})

            # Formatação do rótulo de dados para R$ no gráfico
            fig.update_traces(texttemplate='R$ %{text:.2s}', textposition='outside')
            fig.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f')
            
            st.plotly_chart(fig, use_container_width=True)

            # 6. Tabela Detalhada (Ordem Solicitada)
            st.subheader("📋 Detalhamento")
            colunas_ordem = [
                'LIDERANCA', 'MÊS', 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                'PONTO NATURAL', 'RUPTURA', 'MPDV'
            ]
            
            # Garante que só exibe colunas que existem no arquivo
            colunas_exibir = [c for c in colunas_ordem if c in df_final.columns]
            st.dataframe(df_final[colunas_exibir], use_container_width=True)

        else:
            st.warning(f"Nenhum dado encontrado para a matrícula: {matricula_input}")
            
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        st.info("Verifique se as colunas 'LIDERANCA' e 'TOTAL A RECEBER' existem no arquivo.")
