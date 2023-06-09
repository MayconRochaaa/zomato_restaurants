import os
import numpy                as np
import pandas               as pd
import streamlit            as st
import funcoes_zomato       as fz
import plotly.graph_objects as go

from PIL import Image

#==================================================== LEITURA DA FONTE DE DADOS =========================================================================
BASE_DIR = os.path.abspath('')                                           #Pasta onde se encontra o Home.py
DATASET = os.path.join(BASE_DIR,'data_set')                              #Pasta contendo os dados
IMAGES = os.path.join(BASE_DIR,'images')                                 #Pasta contendo as imagens
dforiginal =  pd.read_csv(os.path.join(DATASET,'zomato.csv'))            #Leitura dos dados
df = fz.limpeza_tratamento(dforiginal)                                   #Limpeza dos dados


#========================================================== VALORES FIXOS ===============================================================================
cidades_por_paisfix = fz.ope_df(df, ['country','city'], 'country', {'city': 'nunique'})
nota_mean_ppfix = fz.ope_df(df,['country','aggregate_rating'], 'country', {'aggregate_rating': 'mean'})
prato2_meanfix = fz.ope_df(df, ['country','average_cost_for_two'], 'country', {'average_cost_for_two': 'mean'})

#===================================================== ESPECIFICAÇÕES DA PÁGINA =========================================================================
st.set_page_config(page_title='Visão País', page_icon='🗾',layout='wide')

#========================================================== MENU LATERAL ================================================================================
with st.sidebar: #Semelhante à barra da página geral, porém agora a escolha do país é limitada a 1 e o usuario pode escolher as cidades

    image = Image.open(os.path.join(IMAGES,'Logo.png'))
    image2 = Image.open(os.path.join(IMAGES,'char.png'))

    st.image(image, width = 180)
    st.markdown('# Zomato Dashboard')
    st.markdown('## Informações sobre os restaurantes em todo globo')

    st.markdown('''---''')

    options_pais = st.selectbox('Selecione o(s) país(es) que deseja obter informações', #Opções de país limitada a 1
                                                df['country'].sort_values().unique())

    st.markdown('''---''')

    options_cidade = st.multiselect('Selecione a(s) cidade(s) do(s) país(es) que deseja obter informações', #Adicionado a opção de escolher as cidades
                                        np.append('Todas', df['city'][df['country']==options_pais].unique()),
                                        default = ['Todas']) 

    st.markdown('''---''')
    
    nota_slider = (st.slider('Nota minima:', 
                                    value = 0.0, 
                                    min_value = 0.0, 
                                    max_value = 5.0,
                                    step=0.5))

    values = st.slider('Selecione a faixa de preço', 0, 800, (0, 800))

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
    
#---------------------Filtra o dataframe de acordo com o país selecionado------------------------------------
df = df[df['country']==options_pais] 

#------------------------------APLICA ALTERAÇÃO DO FILTRO DE PAISES E CIDADES--------------------------------
if 'Todas' in options_cidade:
    df = df
else:
    cidades_selecionadas = df['city'].isin(options_cidade)
    df = df.loc[cidades_selecionadas,:]

if (len(options_cidade)<2 and options_cidade[0]!='Todas'): #Se o numero de cidades selecionadas for menor que 2 exibe mensagem de erro
    st.error('Selecione pelo menos duas cidades para comparar')
else:
    
#================================== Visão Pais =====================================================================================
    st.title('Visão país: ', help='No menu ao lado você pode comparar cidades e filtrar a nota e preço dos restaurantes.')
        
    cidades_por_pais = fz.ope_df(df, ['country','city'], 'country', {'city': 'nunique'})
    nota_cidades = fz.ope_df(df,['city', 'restaurant_name', 'aggregate_rating'],['city', 'restaurant_name'],{'aggregate_rating': 'mean'})
    df_culi = fz.explode_column(df,'cuisines','country')
    
    with st.container(): #Dados do país
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label = 'País:', value = options_pais)   

        with col2:
            st.metric(label = 'Total de cidades cadastradas:', value = cidades_por_paisfix[cidades_por_paisfix['country']==options_pais]['city'] )
        
        with col3:
            aux=round(nota_mean_ppfix[nota_mean_ppfix['country']==options_pais]['aggregate_rating'],1)
            st.metric(label = 'Avaliação média dos restaurantes no país:', value = f'{aux.iloc[0]}/5.0')
            
        with col4:
            aux = round(prato2_meanfix[prato2_meanfix['country']==options_pais]['average_cost_for_two'],2)
            st.metric(label = 'Custo médio de uma refeição no país:', value = f'${aux.iloc[0]}')

    st.markdown('''---''')

    with st.container():
        

        genre = st.radio("Comparar entre os restaurantes que:", #Da opção ao usuario de comparar os restaurantes que entregam, ou fazem reserva ou aceitam pedidos online
                        ('Entregam', 'Fazem reserva', 'Aceitam pedidos online'),
                        horizontal=True,
                        help='Ao selecionar um tipo de comparação os gráficos de barra passam a ser empilhados separando os tipos de serviços selecionados') #alterar ente os que entregam e os que fazem reserv
        
        if genre == 'Entregam': #Define condições de acordo com a opção selecionada anteriormente. 
            k=0
        elif genre == 'Fazem reserva':
            k=1
        elif genre == 'Aceitam pedidos online':
            k=2
            
        opcoes = ['is_delivering_now', 'has_table_booking', 'has_online_delivery'] 
        cond = ['Entregam', 'Reservam', 'Aceitam pedidos online']; leg = [cond[k],f'Não {cond[k]}']
        col_escolhida = opcoes[k] #De acordo com a opção escolhida alteramos as variaveis de acordo com as listas escritas acima
        
        num_res_ent_cidad = (df.loc[:,['city',col_escolhida]] #Calcula o numero de restaurantes por cidade. Sim ou Não é representado nas colunas como 0 e 1, respectivamente
                                    .groupby('city')[col_escolhida]
                                    .agg(['count', 'sum'])
                                    .sort_values(by=['count', 'sum'],ascending=[False, True]) #Faz operações de contagem e soma na coluna escolhida
                                    .reset_index())
        
        fig = go.Figure(data=[
        go.Bar(name=leg[0], x=num_res_ent_cidad['city'], 
            y=num_res_ent_cidad['count']-num_res_ent_cidad['sum'], #sum retorna a quantidade de restaurante que não realizam tal serviço selecionado, portanto
            marker_color='#4472c4',                                # count - sum retorna a quantidade que praticam tal serviço.
            textposition='outside',
            orientation='v'),
        
        go.Bar(name=leg[1], x=num_res_ent_cidad['city'],
            y=num_res_ent_cidad['sum'],
            marker_color='#ed7d31',
            textposition='outside',
            orientation='v')])


        fig.update_layout(barmode='stack', #Modificações no layout
                        xaxis_title='Cidade', 
                        yaxis_title='Quantidade de Restaurantes',  
                        title='Quantidade de Restaurantes por Cidade',
                        legend=dict(x=-0.01, y=1.2, orientation='h'))   

        st.plotly_chart(fig,use_container_width=True)
    
    st.markdown('''---''')    
    
    with st.container():
    
        st.markdown('Avaliação média de cada cidade, comparando por serviço selecionado:')
        
        #Separação dos casos
        caso = ['is_delivering_now', 'has_table_booking', 'has_online_delivery']
        text = ['Entregam', 'Reservam', 'Aceitam pedidos online']
        casoi = k
        
        dfau = df.loc[:,['city', caso[casoi], 'aggregate_rating']]

        realiza = dfau[dfau[caso[casoi]]==0].loc[:,['city', 'aggregate_rating']].sort_values(by='city').reset_index()
        nao_realiza = dfau[dfau[caso[casoi]]==1].loc[:,['city', 'aggregate_rating']].sort_values(by='city').reset_index()

        realiza = realiza.groupby('city').mean().sort_values(by='aggregate_rating',ascending=False).reset_index()
        nao_realiza = nao_realiza.groupby('city').mean().sort_values(by='aggregate_rating',ascending=False).reset_index()

        #Se existe algum restaurante que não realiza o serviço selecionado é plotado o gráfico borboleta
        if nao_realiza['aggregate_rating'].sum() != 0:
            fig = go.Figure(data=[go.Bar(name = text[casoi], x=realiza['city'], y=nao_realiza['aggregate_rating'],marker_color='#ed7d31'),
                                    go.Bar(name = f'Não {text[casoi]}', x=nao_realiza['city'], y = nao_realiza['aggregate_rating'],marker_color='#4472c4')])
            fig.update_layout(barmode='group', legend=dict(x=-0.005, y=1.2, orientation='h'),
                                yaxis_title='Nota média',
                                xaxis_title='Cidade')
 
        else: #Caso todos os restaurantes realizaem o serviço selecionado é plotado um gráfico de barras convencional
            fig = go.Figure(); fig.add_trace(go.Bar(name = text[casoi],y=realiza['aggregate_rating'],
                                                    x=realiza['city'], 
                                                    orientation='v', 
                                                    width=0.7, 
                                                    showlegend=True, 
                                                    marker_color='#ed7d31'), ); 

            fig.update_layout(title_text=f"Avaliação média dos restaurantes das cidades (Todos {text[casoi]})")
            
            
            
        st.plotly_chart(fig,use_container_width=True) 
          
    with st.container():
        #Gráfico de barras empilhadas da coluna de culinarias
        df_count = df_culi.groupby(['country', 'cuisines']).size().reset_index(name='count').copy()
        dfauaux =  df_count.loc[:,['country', 'count']].groupby('country').sum().reset_index()
        df_top_5_pc = df_count
        df_top_5_pc['count'] = [df_top_5_pc.loc[i][2]/dfauaux['count'][dfauaux['country']==country]
                                .to_list()[0] for i, country in zip(range(len(df_top_5_pc)), df_top_5_pc['country'])]

        # Ordenar o dataframe por país e porcentagem
        df_top_5_pc = df_top_5_pc.sort_values(['country', 'count'], ascending=[True, False])

        # Criar uma coluna numerando os tipos de culinária em cada país
        df_top_5_pc['culinary_rank'] = df_top_5_pc.groupby('country').cumcount() + 1

        st.markdown('Informações sobre as culinarias oferecida pelos restaurantes do país:')
        passo = (st.slider('Quantidade de tipos de culinaria que deseja ter informações:', 
                                value = 3, 
                                min_value = 1, 
                                max_value = 20,
                                step=1,
                                key=1))
        passo = passo+1
        
        # Filtrar apenas os quatro primeiros tipos de culinária e o tipo "outros"
        df_filtered = df_top_5_pc[df_top_5_pc['culinary_rank'] <= passo-1].copy()
        df_others = df_top_5_pc[df_top_5_pc['culinary_rank'] > passo-1].copy()

        # Agrupar os tipos de culinária restantes como "outros"
        df_others = df_others.groupby('country').sum().reset_index()
        df_others['cuisines'] = 'Outros'
        df_others['culinary_rank'] = passo

        # Concatenar os dataframes filtrados
        df_final = pd.concat([df_filtered, df_others], ignore_index=True)

        # Remover a coluna de ranking temporária
        df_final.drop('culinary_rank', axis=1, inplace=True)


        df_final = df_final.sort_values(['country', 'count'],ascending=False).reset_index()
        
        nomes = [f'{j+1}º Mais popular' for j in range(passo)]
        
        #Essa e a linha abaixo retiram o 'outros'
        df_final = df_final[df_final['cuisines']!='Outros'].reset_index() 
        passo = passo -1
        
        #Plot
        fig = go.Figure()
        fig.add_trace(go.Bar(x = df_final['count'], y = df_final['cuisines'], orientation = 'h', marker_color='#4472c4'))
        fig.update_traces(textposition='outside')
        fig.update_xaxes(showgrid=True)
        fig.update_layout(xaxis=dict(tickformat=f'.2%'),
                          yaxis_title='Tipo de culinaria',
                          height=600)

        st.plotly_chart(fig,use_container_width=True)
        
        st.markdown('''---''')
 
    
                
                
            