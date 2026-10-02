import streamlit as st
import pandas as pd
import requests 
import plotly.express as px

st.set_page_config(layout='wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor < 1000.0:
            return f"{prefixo}{valor:.2f}{unidade}"
        valor /= 1000.0
    return f"{prefixo}{valor:.2f}M"

st.title('DASHBOARD DE VENDAS :shopping_cart:' )

url = 'https://labdados.com/produtos'
regioes = ['Brasil','Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Selecione a região', regioes)

if regiao == 'Brasil':
   regiao = ''

todos_anos = st.sidebar.checkbox('Todos os anos', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.number_input('Selecione o ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Filtrar por vendedor', dados ['Vendedor'].unique())
if filtro_vendedores:  
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## tabelas

##tabela de receitas
receita_estado = dados.groupby('Local da compra')['Preço'].sum()
receita_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat','lon']].merge(receita_estado, left_on='Local da compra', right_index=True).sort_values(by='Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index().sort_values(by='Data da Compra', ascending=True)
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(by='Preço', ascending=False)

##tabelas de quantidade de produtos
dados_por_produto = dados.groupby('Produto').agg(
    Preço=('Preço', 'sum'),
    Quantidade_Vendas=('Produto', 'size')
).reset_index()

qtd_de_vendas_por_estado = dados.groupby('Local da compra')['Produto'].sum()
qtd_de_vendas_por_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat','lon']].merge(qtd_de_vendas_por_estado, left_on='Local da compra', right_index=True).sort_values(by='Produto', ascending=False)    

qtd_de_vendas_mensal =pd.DataFrame(
    dados.set_index('Data da Compra')
    .groupby([pd.Grouper(freq='ME'), 'Produto'])['Produto']
    .count()
    .reset_index(name='Quantidade de Vendas')
)
qtd_de_vendas_mensal['Ano'] = qtd_de_vendas_mensal['Data da Compra'].dt.year
qtd_de_vendas_mensal['Mes'] = qtd_de_vendas_mensal['Data da Compra'].dt.month_name()


##tabela vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


##graficos
fig_mapa_receita = px.scatter_geo(receita_estado, 
                                  lat='lat', 
                                  lon='lon',
                                  scope='south america', 
                                  size='Preço', 
                                  template = 'seaborn',
                                  color='Preço', 
                                  hover_name='Local da compra', 
                                  hover_data={'lat':False, 'lon':False, 'Preço':True},    
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=[0, receita_mensal['Preço'].max()],
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')

fig_receita_mensal.update_layout(xaxis_title='Mês', yaxis_title='Receita')

fig_receita_estado = px.bar(receita_estado.head(5), 
                            x='Local da compra', 
                            y='Preço', 
                            text_auto=True,
                            title='Top 5 estados por receita')

fig_receita_estado.update_layout(xaxis_title='Estado', yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categoria,  
                               text_auto=True,
                               title='Categorias por receita')

fig_receita_categoria.update_layout(yaxis_title='Receita')

fig_quantidade_vendas = px.bar(dados_por_produto.sort_values(by='Quantidade_Vendas', ascending=False).head(10),
                               x='Produto',
                               y='Quantidade_Vendas',
                               text_auto=True,
                               title='Top 10 produtos por quantidade de vendas')

fig_quantidade_vendas.update_layout(yaxis_title='Quantidade de Vendas')

fig_qtd_vendas_por_estado = px.scatter_geo(qtd_de_vendas_por_estado,
                                          lat='lat',
                                          lon='lon',
                                          scope='south america',
                                          title='Quantidade de Vendas por Estado')


fig_qtd_de_vendas_mensal = px.line(qtd_de_vendas_mensal, 
              x = 'Mes',
              y='Produto',
              markers = True, 
              range_y = (0,qtd_de_vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_qtd_de_vendas_mensal.update_layout(yaxis_title='Quantidade de Vendas')

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de produtos', 'Vendedores'])

with aba1:  
   coluna1, coluna2 = st.columns(2)
   with coluna1:
      st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$ '))
      st.plotly_chart(fig_mapa_receita, use_container_width=True)
      st.plotly_chart(fig_receita_estado, use_container_width=True)
   with coluna2:
     st.metric('Quantidade de produtos', formata_numero(dados.shape[0]))
     st.plotly_chart(fig_receita_mensal, use_container_width=True)
     st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Quantidade de produtos', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_quantidade_vendas, use_container_width=True)
        st.plotly_chart(fig_qtd_vendas_por_estado, use_container_width=True)
    with coluna2:
      st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$ '))
      st.plotly_chart(fig_qtd_de_vendas_mensal, use_container_width=True)
with aba3:
    quantidade_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Quantidade de produtos', formata_numero(dados.shape[0]))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(quantidade_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(quantidade_vendedores).index,
                                        text_auto=True,
                                        orientation='h',
                                        title=f'Top {quantidade_vendedores} vendedores por receita')
        st.plotly_chart(fig_receita_vendedores, width='stretch', use_container_width=True)
      
    with coluna2:
      st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$ '))
      fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(quantidade_vendedores),
                                                x='count',
                                                y=vendedores[['count']].sort_values('count', ascending=False).head(quantidade_vendedores).index,
                                                text_auto=True,
                                                orientation='h',
                                                title=f'Top {quantidade_vendedores} vendedores por qtd de vendas')
      
      st.plotly_chart(fig_vendas_vendedores, width='stretch', use_container_width=True)
