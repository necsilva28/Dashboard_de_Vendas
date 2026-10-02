import time
import streamlit as st
import pandas as pd
import requests 


regioes = {
    "Sudeste": ["SP", "RJ", "MG", "ES"],
    "Sul": ["RS", "SC", "PR"],
    "Nordeste": ["BA", "PE", "CE", "MA", "PB", "RN", "AL", "SE", "PI"],
    "Norte": ["AM", "PA", "AC", "RO", "RR", "AP", "TO"],
    "Centro-Oeste": ["GO", "MT", "MS", "DF"]
}

@st.cache_data
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Download concluído com sucesso!', icon="✅")
    time.sleep(2)
    sucesso.empty()

st.title('Dados Brutos' )

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
   colunas = st.multiselect('Selecione as colunas que deseja visualizar', dados.columns.tolist(),dados.columns.tolist())

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os produtos que deseja visualizar', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Data da Compra'):
    data = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Local da Compra'):
    local = st.multiselect('Selecione o local', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())
#with st.sidebar.expander('Região'):    
# regiao_selecionada = st.selectbox(
#    "Região",
#    list(regioes.keys())
#)

#estados_regiao = regioes[regiao_selecionada]

data_inicio = pd.Timestamp(data[0])
data_fim = pd.Timestamp(data[1]) + pd.Timedelta(days=1)

query = "`Produto` in @produtos and @preco[0] <= `Preço` <= @preco[1] and @data_inicio <= `Data da Compra` < @data_fim and `Categoria do Produto` in @categoria and `Local da compra` in @local and `Vendedor` in @vendedor" 

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]


st.dataframe(dados_filtrados)

st.markdown(f'A tabela posssui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')

st.markdown('escreva um nome para o arquivo de download')
coluna1 , coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo = nome_arquivo + '.csv'
with coluna2:
    st.download_button(
        label='Download CSV',
        data=converte_csv(dados_filtrados),
        file_name=nome_arquivo,
        mime='text/csv',
        on_click=mensagem_sucesso
    )
