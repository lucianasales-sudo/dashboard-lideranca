import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Portal de Performance - 3 Corações", layout="wide")

# Estilo para esconder o menu padrão e centralizar elementos se necessário
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dados2_lideranca.csv', 
                         sep=';', 
                         encoding='latin-1', 
                         on_bad_lines='skip', 
                         engine='python')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

df = load_data()

# --- TELA INICIAL ---
# Logo da Três Corações (Certifique-se de ter o arquivo ou use uma URL oficial)
# Se tiver o arquivo na pasta, use: st.image("logo_3coracoes.png", width=200)
st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=150)

st.title("🚀 Portal de Resultados")
st.info("💡 Exemplo de preenchimento: Digite a matrícula com os zeros iniciais (ex: 001234).")

# Campo de entrada e Botão de Consultar
matricula_input = st.text_input("Digite a Matrícula do Supervisor:", placeholder="Ex: 000000")
botao_consultar = st.button("CONSULTAR")

st.markdown("---")

# --- LÓGICA DE CONSULTA ---
if botao_consultar or matricula_input:
    if df is not None:
        try:
            # Identificando colunas
            col_lider = [c for c in df.columns if 'LIDER' in c][0]
            col_nota = [c for c in df.columns if 'NOTA' in c][0]
            col_nome = [c for c in df.columns if 'NOME RH' in c or 'NOME INVOLVES' in c][0]

            # Tratamento da Nota
            df[col_nota] = df[col_nota].astype(str).str.replace(',', '.')
            df[col_nota] = pd.to_numeric(df[col_nota], errors='coerce').fillna(0)

            # Filtrando pela matrícula digitada
            # Nota: Convertendo ambos para string para garantir a comparação
            df_filtrado = df[df[col_lider].astype(str).str.strip() == matricula_input.strip()]

            if not df_filtrado.empty:
                # Pegar o nome do líder (supondo que haja uma coluna de nome ou usando a própria matrícula)
                nome_lider = df_filtrado[col_lider].iloc[0]
                
                # Exibir nome do líder no início
                st.header(f"👤 Supervisor: {nome_lider}")

                # Cards de Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric("Tamanho da Equipe", len(df_filtrado))
                c2.metric("Média de Notas LC", f"{df_filtrado[col_nota].mean():.1f}")
                
                # Gráfico
                fig = px.bar(df_filtrado, 
                             x=col_nome, 
                             y=col_nota, 
                             color=col_nota,
                             color_continuous_scale='Reds',
                             title="Desempenho por Promotor",
                             labels={col_nota: 'Nota LC', col_nome: 'Promotor'})
                st.plotly_chart(fig, use_container_width=True)

                # TABELA COM ORDEM ESPECÍFICA
                st.subheader("📋 Detalhamento da Equipe")
                colunas_desejadas = [
                    'LIDERANCA', 'MÊS', 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                    'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                    'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                    'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                    'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                    'PONTO NATURAL', 'RUPTURA', 'MPDV'
                ]
                
                # Filtra apenas as colunas que realmente existem no seu CSV para não dar erro
                colunas_finais = [c for c in colunas_desejadas if c in df_filtrado.columns]
                st.dataframe(df_filtrado[colunas_finais], use_container_width=True)

            else:
                st.warning(f"Matrícula '{matricula_input}' não encontrada na base de dados.")

        except Exception as e:
            st.error(f"Erro no processamento: {e}")
    else:
        st.error("Erro ao acessar a base de dados.")
