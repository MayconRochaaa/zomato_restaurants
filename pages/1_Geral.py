import os
import numpy                as np
import pandas               as pd
import streamlit            as st
import funcoes_zomato       as fz
import plotly.graph_objects as go

from PIL                import Image
from itertools          import cycle
from plotly.subplots    import make_subplots

#==================================================== LEITURA DA FONTE DE DADOS =========================================================================
BASE_DIR = os.path.abspath('')                                           #Pasta onde se encontra o Home.py
DATASET = os.path.join(BASE_DIR,'data_set')                              #Pasta contendo os dados
IMAGES = os.path.join(BASE_DIR,'images')                                 #Pasta contendo as imagens
dforiginal =  pd.read_csv(os.path.join(DATASET,'zomato.csv'))            #Leitura dos dados
df = fz.limpeza_tratamento(dforiginal)                                   #Limpeza dos dados

#========================================================== VALORES FIXOS ==============================================================================
unic_rest, unic_paises, unic_cidades, num_ava = (df.agg({'restaurant_id': 'nunique',
                                                          'country': 'nunique',
                                                          'city': 'nunique',
                                                          'votes': 'sum'})) #Variaveis que não serão modificadas pelos menus interativos

#===================================================== ESPECIFICAÇÕES DA PÁGINA =========================================================================
st.set_page_config(page_title='Visão Geral', page_icon='🌎', layout='wide')

#========================================================== MENU LATERAL ================================================================================
with st.sidebar:

    image = Image.open(os.path.join(IMAGES,'Logo.png'))
    image2 = Image.open(os.path.join(IMAGES,'char.png'))

    st.image(image, width = 180)
    st.markdown('# Zomato Dashboard')
    st.markdown('## Informações sobre os restaurantes em todo globo')

    st.markdown('''---''') 
    st.text('Filtros por país')
    options_pais = st.multiselect('Selecione o(s) país(es) que deseja comparar',
                                  np.append('Todos', df['country'].sort_values().unique()),
                                  default = ['Todos']) #Seleciona os países fornecidos pelo usuario para comparação. Por padrão é selecionado TODOS

    st.markdown('''---''')
    
    st.text('Filtros por nota e preço')
    nota_slider = (st.slider('Nota minima dos restaurantes:', 
                             value = 0.0, min_value = 0.0, max_value = 5.0, step=0.5)) #Seleciona a nota minima esperada dos restaurantes
    
    values = st.slider('Faixa de preço dos restaurantes',
                       0, 800, (0,800)) #Seleciona a faixa de preço para o preço médio para dois

    st.markdown('''---''')

    with st.container():
        col1, col2 = st.columns([3,1])
        
        with col1:
            st.markdown('### Criado por: Maycon Rocha')
        with col2:
            st.image(image2, width = 50, output_format='auto')
    st.caption('Alguma dúvida ou sugestão? Entre em contato: mayconrochads@gmail.com')
#=========================================================== INTERAÇÕES =================================================================================

#------------------------------APLICA ALTERAÇÃO DO FILTRO DE PAÍSES--------------------------------
if 'Todos' in options_pais: 
    df = df
else:
    paises_selecionados = df['country'].isin(options_pais)
    df = df.loc[paises_selecionados,:]

#-------------------------APLICA ALTERAÇÃO DO FILTRO DE PREÇOS E NOTA-------------------------------
linhas_selecionadas = df['aggregate_rating'] >= nota_slider; df = df.loc[linhas_selecionadas,:] 
range_selecionadosup = df['average_cost_for_two'] <= values[1]; df = df.loc[range_selecionadosup,:]
range_selecionadoinf = df['average_cost_for_two'] >= values[0]; df = df.loc[range_selecionadoinf,:]

#================================== Pagina Geral  ===============================================================

st.title('Visão Geral: ', help='No menu ao lado você pode comparar países e filtrar a nota e preço dos restaurantes.')

#CALCULA AS VARIAVEIS COM O DATAFRAME JÁ MODIFICADO PELOS FILTROS (fz.ope_df recebe, respectivamente, o dataframe,
#colunas de interesse, coluna a ser agrupado pelo .groupby e um dicionario que entra como argumento no .agg)

rest_por_pais = fz.ope_df(df, ['country','restaurant_id'], 'country', {'restaurant_id': 'count'})               #Restaurante por país
cidades_por_pais = fz.ope_df(df, ['country','city'], 'country', {'city': 'nunique'})                            #Cidades por país
num_ava_mean_pp = fz.ope_df(df, ['country','votes'], 'country', {'votes': 'sum'})                               # Numero de avaliações por país
prato2_mean = fz.ope_df(df, ['country','average_cost_for_two'], 'country', {'average_cost_for_two': 'mean'})    #Valor médio de um prato para dois por país
nota_mean_pp = fz.ope_df(df,['country','aggregate_rating'], 'country', {'aggregate_rating': 'mean'})            #Nota média dos restaurantes do país
rest_por_pais = rest_por_pais.sort_values(by='restaurant_id', ascending=False).reset_index()                    #Calcula os restaurantes por país
df_culi = fz.explode_column(df,'cuisines','country')

if ((len(options_pais)!=0)):    #Garante que o usuario selecionou ao menos um país, caso contrario é exibido uma mensagem de erro no else mais abaixo 
    
    with st.container():        #Informações das váriaveis fixas
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unic_rest = "{:,.0f}".format(unic_rest)
            st.metric(label = 'Restaurantes registrados:', value = unic_rest )
        
        with col2:
            st.metric(label = 'Paises registrados:', value = unic_paises )
        
        with col3:
            st.metric(label = 'Cidades registradas:', value = unic_cidades)

        with col4:
            num_ava = "{:,.0f}".format(num_ava)
            st.metric(label = 'Total de avaliações recebidas:', value = num_ava)

    st.markdown('''---''')
        
    with st.container():        #Gráfico borboleta que mostra a quantidade de cidades e restaurantes por paises selecionados
    
        fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=False,       #Cria uma figura que pode conter subplots
                            shared_yaxes=True, horizontal_spacing=0) 
        
        fig.append_trace(go.Bar(x=rest_por_pais['restaurant_id'],                       #Plota o gráfico de barras dos restaurantes por país no lado direito
                            y=rest_por_pais['country'],                                 
                            text=rest_por_pais["restaurant_id"].map('{:,.0f}'.format),
                            textposition='outside',
                            orientation='h', 
                            width=0.7, 
                            showlegend=False, 
                            marker_color='#ed7d31'), 
                            1, 2)

        fig.append_trace(go.Bar(x=cidades_por_pais['city'],                             #Plota o gráfico de barras dos restaurantes por país no lado esquerdo
                            y=cidades_por_pais['country'], 
                            text=cidades_por_pais["city"].map('{:,.0f}'.format),
                            textposition='outside',
                            orientation='h', 
                            width=0.7, 
                            showlegend=False, 
                            marker_color='#4472c4'), 
                            1, 1) 

        fig.update_xaxes(showticklabels=True,title_text="número de cidades", row=1, col=1, range=[cidades_por_pais['city'].max()*1.1,0]) #Alterações nos eixos e layout
        fig.update_xaxes(showticklabels=True,title_text="número de restaurantes", row=1, col=2, range=[0,rest_por_pais['restaurant_id'].max()*1.1])
        fig.update_layout(yaxis=dict(categoryarray=list(reversed(rest_por_pais['country']))),
                          xaxis=dict(side='top'),
                          title_text="Quantidade de cidades e restaurantes por país",
                          width=900, 
                          height=600,
                          title_x=0.40,
                          xaxis1={'side': 'bottom'},
                          xaxis2={'side': 'bottom'})
        
        st.plotly_chart(fig,use_container_width=True) #Plot do gráfico

    st.markdown('''---''')

    with st.container():        #Tabela com informações úteis de cada país
        dff = pd.DataFrame(); 
        dff['País'] = df['country'].sort_values().unique()                                                              #Nome do país
        dff['Média de preço para dois (USD)'] = prato2_mean.sort_values(by='country')['average_cost_for_two'].round(2)  #Média de preço para dois
        dff['Avaliação média'] = nota_mean_pp.sort_values(by='country')['aggregate_rating'].round(1)                    #Avaliação média dos restaurantes
        dff['Número de votos'] = num_ava_mean_pp.sort_values(by='country')['votes']                                     #Quantidade de avaliações
        
        st.markdown('Informações gerais de cada país:')
        st.dataframe(dff,use_container_width=True)
    
    st.markdown('''---''')
    
    with st.container(): #Grafico de barras empilhadas que diz a porcentagem das culinarias mais populares de cada país
        
#--------------------------------------------------------------------------------------------------------------------

        df_count = df_culi.groupby(['country', 'cuisines']).size().reset_index(name='count').copy() #Conta aquantidade de tipos de culinaria por país
        dfauaux =  df_count.loc[:,['country', 'count']].groupby('country').sum().reset_index() #Tabela auxiliar para o calculo dos valores percentuais
        df_top_x = df_count; df_top_x['count'] = [df_top_x.loc[i][2]/dfauaux['count'][dfauaux['country']==country] #df_top_x irá armazenar os top 'x' valores
                                                        .to_list()[0] for i, country in zip(range(len(df_top_x)), df_top_x['country'])]

        df_top_x = df_top_x.sort_values(['country', 'count'], ascending=[True, False]) # Ordenar o dataframe por país e porcentagem

        df_top_x['culinary_rank'] = df_top_x.groupby('country').cumcount() + 1         # Criar uma coluna numerando os tipos de culinária em cada país

        st.markdown('Informações sobre as culinarias de cada país:',
                    help='selecionar muitos países ou culinarias pode piorar a visualização. Na aba País essa informação pode ser consultada novamente com mais detalhes.')
        
        
        passo = (st.slider('Quantidade de tipos de culinaria que deseja ter informações:',  #passo vai selecionar a quantidade de culinarias mostradas no gráfico
                                value = 3, 
                                min_value = 1, 
                                max_value = 7,
                                step=1))
        passo = passo+1 #É somado mais 1 para além das 'x' selecionadas considerar o 'outros' na tabela. É importante para o laço
        
        # Filtrar apenas os 'x' primeiros tipos de culinária e o tipo "outros"
        df_filtered = df_top_x[df_top_x['culinary_rank'] <= passo-1].copy()
        df_others = df_top_x[df_top_x['culinary_rank'] > passo-1].copy()

        # Tendo o top 'x' as culinárias restantes são definidas como "outros"
        df_others = df_others.groupby('country').sum().reset_index()
        df_others['cuisines'] = 'Outros'
        df_others['culinary_rank'] = passo

        # Concatena os dataframes filtrados
        df_final = pd.concat([df_filtered, df_others], ignore_index=True)

        # Remove a coluna de ranking temporária
        df_final.drop('culinary_rank', axis=1, inplace=True)

        #Ordena o dataframe por país e quantidade de cada tipo de culinaria
        df_final = df_final.sort_values(['country', 'count'],ascending=False).reset_index()

        fig = go.Figure() #Cria a figura
        
        nomes = ['Outros' if j==0 else f'{j}º Mais popular' for j in range(passo)] #Define a legenda "x mais popular"

        
        #palette = cycle(px.colors.sequential.Plasma)
        paleta_cores = [
            "#003f5c",
            "#2f4b7c",
            "#665191",
            "#a05195",
            "#d45087",
            "#f95d6a",
            "#ff7c43",
            "#ffa600"
        ]
        palette = cycle(paleta_cores)
        
        for i in range(passo): #Realiza o plot do gŕafico de barras empilhada
            fig.add_trace(go.Bar(
                y=df_final['country'].unique(),
                x=df_final.loc[i:len(df_final):passo]['count'],
                text=df_final.loc[i:len(df_final):passo]['cuisines'].to_list(),
                name = nomes[i],
                orientation='h',
                legendgroup=str(i+1),
                marker_color=next(palette)
            ))


        
        fig.update_traces(textposition='inside')#Ajustes no gráfico
        fig.update_layout(barmode='stack',
                          xaxis=dict(tickformat=f'.2%'),
                          width=1000, 
                          height=600,
                          legend=dict(x=-0.01, y=1.2, orientation='h'))
        st.plotly_chart(fig,use_container_width=True)

else: st.error('Selecione pelo menos um país e uma cidade na barra lateral', icon="🚨")  # Se o usuario não selecionou nenhum país esse erro é mostrado
