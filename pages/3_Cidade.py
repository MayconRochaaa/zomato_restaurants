import os
import numpy                as np
import pandas               as pd
import streamlit            as st
import funcoes_zomato       as fz
import plotly.graph_objects as go

from PIL             import Image
from plotly.subplots import make_subplots


#==================================================== LEITURA DA FONTE DE DADOS =========================================================================
BASE_DIR = os.path.abspath('')                                           #Pasta onde se encontra o Home.py
DATASET = os.path.join(BASE_DIR,'data_set')                              #Pasta contendo os dados
IMAGES = os.path.join(BASE_DIR,'images')                                 #Pasta contendo as imagens
dforiginal =  pd.read_csv(os.path.join(DATASET,'zomato.csv'))            #Leitura dos dados
df = fz.limpeza_tratamento(dforiginal)                                   #Limpeza dos dados


#========================================================== VALORES FIXOS ===============================================================================
restau_por_cidadesfix = fz.ope_df(df, ['city','restaurant_id'], 'city', {'restaurant_id': 'count'})
nota_mean_pcfix = fz.ope_df(df,['city','aggregate_rating'], 'city', {'aggregate_rating': 'mean'})
prato2c_meanfix = fz.ope_df(df, ['city','average_cost_for_two'], 'city', {'average_cost_for_two': 'mean'})

#===================================================== ESPECIFICAÇÕES DA PÁGINA =========================================================================
st.set_page_config(page_title='Visão Cidade', page_icon='🏙️',layout='wide')

#========================================================== MENU LATERAL ================================================================================
with st.sidebar:   #Agora o usuario é limitado a escolher uma cidade por vez.

    image = Image.open(os.path.join(IMAGES,'Logo.png'))
    image2 = Image.open(os.path.join(IMAGES,'char.png'))

    st.image(image, width = 180)
    st.markdown('# Zomato Dashboard')
    st.markdown('## Informações sobre os restaurantes em todo globo')

    st.markdown('''---''')
    options_pais = st.selectbox('Selecione o(s) país(es) que deseja obter informações',
                                                df['country'].sort_values().unique())

    st.markdown('''---''')

    options_cidade = st.selectbox('Selecione a(s) cidade(s) do(s) país(es) que deseja obter informações', #Limita ao usuario escolher apenas uma cidade
                                            df['city'][df['country']==options_pais].unique())

    st.markdown('''---''')
    st.text('Filtros por nota e preço')
    nota_slider = (st.slider('Nota minima dos restaurantes:', value = 0.0, min_value = 0.0, max_value = 5.0, step=0.5))
    values = st.slider('Faixa de preço dos restaurantes',0,800,(0,800))

    st.markdown('''---''')

    with st.container():
        col1, col2 = st.columns([3,1])
        
        with col1:
            st.markdown('### Criado por: Maycon Rocha')
        with col2:
            st.image(image2, width = 50, output_format='auto')
            
    st.caption('Alguma dúvida ou sugestão? Entre em contato: mayconrochads@gmail.com')

#=========================================================== INTERAÇÕES =================================================================================

#-------------------------APLICA ALTERAÇÃO DO FILTRO DE PREÇOS E NOTA----------------------------------------
linhas_selecionadas = df['aggregate_rating'] >= nota_slider; df = df.loc[linhas_selecionadas,:]
range_selecionadosup = df['average_cost_for_two'] <= values[1]; df = df.loc[range_selecionadosup,:]
range_selecionadoinf = df['average_cost_for_two'] >= values[0]; df = df.loc[range_selecionadoinf,:]

#--------------------Filtra o dataframe de acordo com o país e a cidade selecionada--------------------------
df = df[df['country'] == options_pais]
df = df[df['city'] == options_cidade]


#================================== Visão Cidade ==================================================================
st.title('Visão cidade: ', help='No menu ao lado você pode filtrar a nota e preço dos restaurantes.')

rest_bairro = fz.ope_df(df,['country','city','locality','restaurant_name', 'average_cost_for_two'],['country','city','locality'],{'restaurant_name': 'count', 'average_cost_for_two': 'mean'})
rest_bairro = rest_bairro.sort_values(by='average_cost_for_two', ascending=False).reset_index()


if((len(options_pais) == 0) or (len(options_cidade)==0)): #Se nenhum país ou cidade for selecionada retorna uma mensagem de erro
    st.error('Selecione apenas um país e uma cidade na barra lateral', icon='🚨')
else:
    with st.container(): #Valores fixos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label = 'Cidade:', value = options_cidade)   
        
        with col2:
            st.metric(label = 'Total de restaurantes cadastrados:', value = restau_por_cidadesfix[restau_por_cidadesfix['city']==options_cidade]['restaurant_id'] )
        
        with col3:
            aux=round(nota_mean_pcfix[nota_mean_pcfix["city"]==options_cidade]["aggregate_rating"],1)
            st.metric(label = 'Avaliação média dos restaurantes na cidade:', value = f'{aux.iloc[0]}/5.0')
            
        with col4:
            aux = round(prato2c_meanfix[prato2c_meanfix["city"]==options_cidade]["average_cost_for_two"],2)
            st.metric(label = 'Custo médio de uma refeição no país:', value = f'${aux.iloc[0]}')
    
    st.markdown('''---''')
    
    with st.container(): #Gráfico borboleta
        
        st.markdown('Informações da preferência de culinarias da cidade de acordo com os bairros selecionados:')

        #Seleção de bairros para comparação
        bairro = st.multiselect('Selecione um ou mais bairros', np.append('Todos', df['locality'][df['city']==options_cidade].unique()),
                                default = ['Todos'])

        if len(bairro)==0:
            st.error('Selcione ao menos um bairro')
        elif (('Todos' in bairro) and (len(bairro)==1)):
            df = df
        else:
            Bairros = df['locality'].isin(bairro)
            df = df.loc[Bairros,:]

        #Calcula o dataframe de culunarias levando em consideração os bairros
        df_culi = fz.explode_column(df,'cuisines','city')
        
        fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=False,
        shared_yaxes=True, horizontal_spacing=0)
        
        fig.append_trace(go.Bar(y=rest_bairro['locality'], 
                                x=rest_bairro['restaurant_name'],
                                text=rest_bairro["restaurant_name"].map('{:,.0f}'.format),
                                textposition='outside',
                                marker_color='#ed7d31',
                                showlegend=False,
                                orientation='h'),1,2)

        fig .append_trace(go.Bar(y=rest_bairro['locality'], 
                                x=rest_bairro['average_cost_for_two'],
                                text=rest_bairro["average_cost_for_two"].map('{:,.0f}'.format),
                                textposition='outside',
                                marker_color='#4472c4',
                                showlegend=False,
                                orientation='h'),1,1)
        
        fig.update_xaxes(showticklabels=True,title_text="Preço médio para dois", row=1, col=1,range=[rest_bairro['average_cost_for_two'].max()*1.1,0])
        fig.update_xaxes(showticklabels=True,title_text="Quantidade de restaurantes", row=1, col=2, range=[0,rest_bairro['restaurant_name'].max()*1.1])
        fig.update_layout(yaxis=dict(categoryarray=list(reversed(rest_bairro['locality']))),xaxis=dict(side='top'))
        fig.update_layout(title_text="Comparação entre a quantidade de restaurantes e o preço médio para dois por bairro", 
                        width=1000, 
                        height=500,
                        title_x=0.10,
                        xaxis1={'side': 'bottom'},
                        xaxis2={'side': 'bottom'},)

        st.plotly_chart(fig,use_container_width=True) 

    st.markdown('''---''')
    with st.container(): 
        
    #--------------------------------------------------------------------------------------------------------------------

        df_count = df_culi.groupby(['city', 'cuisines']).size().reset_index(name='count').copy()
        dfauaux =  df_count.loc[:,['city', 'count']].groupby('city').sum().reset_index()
        df_top_5_pc = df_count
        df_top_5_pc['count'] = [df_top_5_pc.loc[i][2]/dfauaux['count'][dfauaux['city']==city]
                                .to_list()[0] for i, city in zip(range(len(df_top_5_pc)), df_top_5_pc['city'])]


        # Ordenar o dataframe por país e porcentagem
        df_top_5_pc = df_top_5_pc.sort_values(['city', 'count'], ascending=[True, False])

        # Criar uma coluna numerando os tipos de culinária em cada país
        df_top_5_pc['culinary_rank'] = df_top_5_pc.groupby('city').cumcount() + 1
        
        passo = (st.slider('Quantidade de tipos de culinaria que deseja ter informações:', 
                                value = 3, 
                                min_value = 1, 
                                max_value = 20,
                                step=1,
                                key=3))
        passo = passo+1
        
        
        # Filtrar apenas os quatro primeiros tipos de culinária e o tipo "outros"
        df_filtered = df_top_5_pc[df_top_5_pc['culinary_rank'] <= passo-1].copy()
        df_others = df_top_5_pc[df_top_5_pc['culinary_rank'] > passo-1].copy()

        # Agrupar os tipos de culinária restantes como "outros"
        df_others = df_others.groupby('city').sum().reset_index()
        df_others['cuisines'] = 'Outros'
        df_others['culinary_rank'] = passo

        # Concatenar os dataframes filtrados
        df_final = pd.concat([df_filtered, df_others], ignore_index=True)

        # Remover a coluna de ranking temporária
        df_final.drop('culinary_rank', axis=1, inplace=True)
        df_final = df_final.sort_values(['city', 'count'],ascending=False).reset_index()

        fig = go.Figure()
        
        nomes = [f'{j+1}º Mais popular' for j in range(passo)]
        
        df_final = df_final[df_final['cuisines']!='Outros'].reset_index() # essa e a linha abaixo retiram o 'outros'
        passo = passo -1
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x = df_final['count'], y = df_final['cuisines'], orientation = 'h', marker_color='#4472c4'))
        fig.update_traces(textposition='outside', textfont=dict(size=28), insidetextfont=dict(size=28))  # Aumenta o tamanho da fonte do texto dentro das barras
        fig.update_layout( xaxis=dict(tickformat=f'.2%'), yaxis_title='Tipo de culinaria')

        st.plotly_chart(fig,use_container_width=True)

        st.markdown('''---''')
        with st.container():
            #Tabela com informações gerais da cidade
            st.markdown('Informações gerais dos restaurantes da cidade de acordo com os bairros selecionados.')
            
            table_rest = (df.loc[:,['restaurant_name','cuisines', 'average_cost_for_two', 'has_table_booking', 'is_delivering_now', 'has_online_delivery', 'aggregate_rating','votes']]
                            .sort_values(by=['aggregate_rating', 'votes'], ascending = [False, False])
                            .reset_index(drop = True))
            
            table_rest['is_delivering_now'] = ['Sim' if i == 0 else 'Não' for i in table_rest['is_delivering_now'].to_list()]
            table_rest['has_table_booking'] = ['Sim' if i == 0 else 'Não' for i in table_rest['has_table_booking'].to_list()]
            table_rest['has_online_delivery'] = ['Sim' if i == 0 else 'Não' for i in table_rest['has_online_delivery'].to_list()]


            table_rest = table_rest.rename(columns={'restaurant_name': 'Nome do restaurante',
                                                    'cuisines': 'Culinarias oferecidas',
                                                    'average_cost_for_two': 'Custo para duas pessoas (USD)',
                                                    'has_table_booking': 'Reservam',
                                                    'is_delivering_now': 'Fazem entrega?',
                                                    'has_online_delivery': 'Aceitam pedidos online?',
                                                    'aggregate_rating': 'Avaliação média',
                                                    'votes': 'Quantidade de avaliações'})
            
            
            st.dataframe(table_rest,use_container_width=True)
    

