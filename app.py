import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnóstico de Dados", layout="wide")

@st.cache_data
def load_data():
    # Testamos os dois separadores mais comuns: ponto e vírgula e vírgula
    for sep in [';', ',']:
        try:
            df = pd.read_csv('dados2_lideranca.csv', sep=sep, encoding='latin-1', on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]
            if 'LIDERANCA' in df.columns or 'LIDERANÇA' in df.columns:
                return df
        except:
            continue
    return None

df = load_data()

st.title("🔍 Diagnóstico de Matrículas")

if df is not None:
    # 1. Ajuste automático de nome de coluna
    col_lider = 'LIDERANCA' if 'LIDERANCA' in df.columns else 'LIDERANÇA'
    
    st.write("### 1. Como as matrículas aparecem no seu arquivo:")
    # Mostra as primeiras 10 matrículas reais que ele achou
    lista_exemplo = df[col_lider].unique()[:15]
    st.info(f"O Python encontrou estas matrículas: {list(lista_exemplo)}")

    st.write("---")
    
    # 2. Área de Busca
    matricula_input = st.text_input("Digite a matrícula exatamente como aparece na lista acima:").strip()
    
    if matricula_input:
        # Busca exata e busca parcial
        resultado = df[df[col_lider].astype(str).str.contains(matricula_input, na=False)]
        
        if not resultado.empty:
            st.success(f"✅ Encontrado! {len(resultado)} linhas para esta matrícula.")
            st.write(resultado.head())
        else:
            st.error("❌ Ainda não encontrado. Verifique se há pontos, traços ou espaços diferentes.")
            
    st.write("### 2. Visualização das primeiras linhas da sua planilha:")
    st.dataframe(df.head(10))
else:
    st.error("Não consegui ler o arquivo 'dados2_lideranca.csv'. Verifique o nome do arquivo no GitHub.")
