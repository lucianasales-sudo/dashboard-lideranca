import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portal de Performance - 3 Corações", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dados2_lideranca.csv', sep=';', encoding='latin-1', on_bad_lines='skip', engine='python')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

df = load_data()

st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=120)
st.title("📊 Portal de Resultados")

matricula_input = st.text_input("Digite a Matrícula do Supervisor:", placeholder="Ex: 1-38013").strip()
botao_consultar = st.button("CONSULTAR")

st.markdown("---")

if (botao_consultar or matricula_input) and df is not None:
    try:
        # --- IDENTIFICAÇÃO INTELIGENTE DE COLUNAS ---
        # Procura colunas que contenham essas palavras-chave para evitar erros de acento
        col_id = [c for c in df.columns if 'MATRICULA' in c and 'LIDER' in c][0]
        col_lider = 'LIDERANCA' 
        col_mes = [c for c in df.columns if 'MÊS' in c or 'MES' in c][0]
        col_nome_rh = 'NOME RH'
        col_total_receber = 'TOTAL A RECEBER'

        # 1. Filtro pela matrícula
        df_lider = df[df[col_id].astype(str).str.strip() == matricula_input].copy()

        if not df_lider.empty:
            # 2. Nome do Supervisor no topo
            nome_supervisor = df_lider[col_lider].iloc[0]
            st.header(f"👤 Supervisor: {nome_supervisor}")

            # 3. Filtro de Mês na lateral
            meses_lista = sorted(df_lider[col_mes].unique())
            mes_sel = st.sidebar.selectbox("📅 Selecione o Mês", meses_lista)
            df_final = df_lider[df_lider[col_mes] == mes_sel].copy()

            # 4. Limpeza do Valor R$ (Tratando como número)
            df_final[col_total_receber] = (
                df_final[col_total_receber]
                .astype(str)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
            )
            df_final[col_total_receber] = pd.to_numeric(df_final[col_total_receber], errors='coerce').fillna(0)

            # 5. Métricas em destaque
            c1, c2 = st.columns(2)
            c1.metric("Equipe no Mês", len(df_final))
            total_equipe = df_final[col_total_receber].sum()
            c2.metric("Total a Receber (Equipe)", f"R$ {total_equipe:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

            # 6. Gráfico com R$ em cima das barras
            st.subheader(f"Distribuição de Premiação - {mes_sel}")
            fig = px.bar(
                df_final, 
                x=col_nome_rh, 
                y=col_total_receber,
                text=df_final[col_total_receber].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')),
                color=col_total_receber, 
                color_continuous_scale='Reds',
                labels={col_total_receber: 'Valor (R$)', col_nome_rh: 'Promotor'}
            )
            
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            # 7. Tabela Detalhada Ordenada
            st.subheader("📋 Detalhamento")
            ordem = ['LIDERANCA', col_mes, 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 'NOTA LOJA DO CORAÇÃO', 
                     'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 'META SELLOUT', 'REAL SELLOUT', 
                     'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 'PRODUTIVIDADE ADERENCIA ROTEIRO', 
                     'PREMIAÇÃO ADERENCIA ROTEIRO', 'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 
                     'PONTO EXTRA', 'PONTO NATURAL', 'RUPTURA', 'MPDV']
            
            # Filtra colunas que realmente existem para evitar novo KeyError
            colunas_existentes = [c for c in ordem if c in df_final.columns]
            st.dataframe(df_final[colunas_existentes], use_container_width=True)

        else:
            st.warning(f"Matrícula {matricula_input} não encontrada.")

    except Exception as e:
        st.error(f"Ocorreu um erro no processamento: {e}")
        st.info("Dica: Verifique se a planilha tem as colunas 'MATRICULA LIDERANCA' e 'TOTAL A RECEBER'.")
