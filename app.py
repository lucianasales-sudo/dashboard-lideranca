import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portal de Performance - 3 Corações", layout="wide")

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

st.image("https://www.3coracoes.com.br/wp-content/themes/tres-coracoes/assets/images/logo-3-coracoes.png", width=120)
st.title("📊 Portal de Resultados")

matricula_input = st.text_input("Digite a Matrícula do Supervisor:", placeholder="Ex: 1-49570").strip()
botao_consultar = st.button("CONSULTAR")

st.markdown("---")

if (botao_consultar or matricula_input) and df is not None:
    try:
        col_lider = 'LIDERANCA'
        col_mes = 'MÊS'
        col_nome_rh = 'NOME RH'
        col_total_receber = 'TOTAL A RECEBER'
        
        # Limpeza agressiva da coluna de valores
        df[col_total_receber] = df[col_total_receber].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
        df[col_total_receber] = pd.to_numeric(df[col_total_receber], errors='coerce').fillna(0)

        # BUSCA TOLERANTE: Procura a matrícula dentro da coluna LIDERANCA ignorando espaços
        # Isso resolve se na planilha estiver "1-49570 " ou "MATRICULA: 1-49570"
        mask = df[col_lider].astype(str).str.contains(matricula_input, na=False, case=False)
        df_lider = df[mask]

        if not df_lider.empty:
            nome_supervisor = df_lider[col_lider].iloc[0]
            st.header(f"👤 Supervisor: {nome_supervisor}")

            meses_disponiveis = sorted(df_lider[col_mes].unique())
            mes_selecionado = st.sidebar.selectbox("📅 Selecione o Mês", meses_disponiveis)
            
            df_final = df_lider[df_lider[col_mes] == mes_selecionado]

            c1, c2 = st.columns(2)
            c1.metric("Equipe no Mês", len(df_final))
            total_pagar = df_final[col_total_receber].sum()
            c2.metric("Total a Receber (Equipe)", f"R$ {total_pagar:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

            st.subheader(f"Distribuição de Premiação - {mes_selecionado}")
            
            # Gráfico com rótulos formatados em R$
            fig = px.bar(df_final, 
                         x=col_nome_rh, 
                         y=col_total_receber,
                         text=df_final[col_total_receber].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')),
                         color=col_total_receber,
                         color_continuous_scale='Reds',
                         labels={col_total_receber: 'Total a Receber (R$)', col_nome_rh: 'Promotor'})

            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Detalhamento")
            colunas_ordem = [
                'LIDERANCA', 'MÊS', 'ANO', 'REGIONAL', 'FILIAL', 'NOME RH', 
                'NOTA LOJA DO CORAÇÃO', 'MEDALHA LOJA DO CORAÇÃO', 'PREMIAÇÃO MEDALHA LC', 
                'META SELLOUT', 'REAL SELLOUT', 'AING SELLOUT %', 'PREMIAÇÃO SELLOUT', 
                'PRODUTIVIDADE ADERENCIA ROTEIRO', 'PREMIAÇÃO ADERENCIA ROTEIRO', 
                'TOTAL A RECEBER', 'OBSERVACOES GERAIS', 'PONTO EXTRA', 
                'PONTO NATURAL', 'RUPTURA', 'MPDV'
            ]
            
            colunas_exibir = [c for c in colunas_ordem if c in df_final.columns]
            st.dataframe(df_final[colunas_exibir], use_container_width=True)

        else:
            st.warning(f"Nenhum dado encontrado para a matrícula: {matricula_input}")
            # Dica para ajudar a depurar: mostra o que tem na planilha
            if st.checkbox("Mostrar lista de matrículas disponíveis (Ajuda)"):
                st.write(df[col_lider].unique())
            
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
