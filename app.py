import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página
st.set_page_config(page_title="Portal de Performance - 3 Corações", layout="wide")

@st.cache_data
def load_data():
    try:
        # Lê o arquivo tratando acentos e separador
        df = pd.read_csv('dados2_lideranca.csv', sep=';', encoding='latin-1', on_bad_lines='skip', engine='python')
        # Limpa nomes de colunas (remove espaços e coloca em maiúsculo)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

df = load_data()

# --- CABEÇALHO ---
st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=120)
st.title("📊 Portal de Resultados")

# Instrução de uso
st.info("💡 Digite a matrícula (ex: 1-38013) e clique em CONSULTAR.")

# Área de busca
col_b1, col_b2 = st.columns([3, 1])
with col_b1:
    matricula_input = st.text_input("Digite a Matrícula do Supervisor:", placeholder="Ex: 1-49570").strip()
with col_b2:
    st.write("##") # Alinhamento
    botao_consultar = st.button("CONSULTAR")

st.markdown("---")

if (botao_consultar or matricula_input) and df is not None:
    try:
        # --- MAPEAMENTO ROBUSTO DE COLUNAS ---
        # Procura colunas por palavras-chave para evitar erros de acentuação
        col_id = [c for c in df.columns if 'MATRICULA' in c and 'LIDER' in c][0]
        col_lider_nome = 'LIDERANCA' 
        # Mês é geralmente a primeira coluna (index 0) ou contém 'S' e 'M'
        col_mes = df.columns[0] 
        col_nome_rh = 'NOME RH'
        col_total_receber = 'TOTAL A RECEBER'

        # 1. Filtra pela matrícula digitada
        df_lider = df[df[col_id].astype(str).str.strip() == matricula_input].copy()

        if not df_lider.empty:
            # 2. Pega o nome real do Supervisor (Coluna LIDERANCA)
            nome_supervisor = str(df_lider[col_lider_nome].iloc[0])
            st.header(f"👤 Supervisor: {nome_supervisor}")

            # 3. Filtro de Mês na lateral
            meses_lista = sorted(df_lider[col_mes].unique())
            mes_sel = st.sidebar.selectbox("📅 Selecione o Mês", meses_lista)
            
            # Filtro Final
            df_final = df_lider[df_lider[col_mes] == mes_sel].copy()

            # 4. Limpeza e conversão do Valor 'TOTAL A RECEBER'
            def limpar_moeda(valor):
                v = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
                try:
                    return float(v)
                except:
                    return 0.0

            df_final[col_total_receber] = df_final[col_total_receber].apply(limpar_moeda)

            # 5. Cards de Resumo
            c1, c2 = st.columns(2)
            c1.metric("Equipe no Mês", len(df_final))
            total_valor = df_final[col_total_receber].sum()
            c2.metric("Total a Receber (Equipe)", f"R$ {total_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

            # 6. Gráfico de Barras com Rótulo R$
            st.subheader(f"Distribuição de Premiação - {mes_sel}")
            
            # Formata rótulos para o gráfico
            df_final['ROTULO'] = df_final[col_total_receber].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            fig = px.bar(
                df_final, 
                x=col_nome_rh, 
                y=col_total_receber,
                text='ROTULO',
                color=col_total_receber,
                color_continuous_scale='Reds',
                labels={col_total_receber: 'Valor (R$)', col_nome_rh: 'Promotor'}
            )
            
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            # 7. Tabela Detalhada (Ordem Solicitada)
            st.subheader("📋 Detalhamento da Equipe")
            ordem_colunas = [
                'LIDERANCA', col_mes, 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                'PONTO NATURAL', 'RUPTURA', 'MPDV'
            ]
            
            # Só mostra o que existir no DF
            colunas_finais = [c for c in ordem_colunas if c in df_final.columns]
            st.dataframe(df_final[colunas_finais], use_container_width=True)

        else:
            st.warning(f"Matrícula '{matricula_input}' não encontrada.")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")
        st.info("Verifique se o arquivo CSV está atualizado no GitHub.")
