import os
import folium
import pandas           as pd
import streamlit        as st
import funcoes_zomato   as fz

from PIL                import Image
from folium.plugins     import MarkerCluster
from streamlit_folium   import folium_static


#==================================================== LEITURA DA FONTE DE DADOS =========================================================================
BASE_DIR = os.path.abspath('')                                  #Pasta onde se encontra o Home.py
DATASET = os.path.join(BASE_DIR,'data_set')                     #Pasta contendo os dados
IMAGES = os.path.join(BASE_DIR,'images')                        #Pasta contendo as imagens
dforiginal =  pd.read_csv(os.path.join(DATASET,'zomato.csv'))   #Leitura dos dados
df = fz.limpeza_tratamento(dforiginal)                          #Limpeza dos dados

#===================================================== ESPECIFICAÇÕES DA PÁGINA =========================================================================
st.set_page_config(page_title='Home',page_icon='📝', layout='wide')

#========================================================== MENU LATERAL ================================================================================
with st.sidebar:

    image = Image.open(os.path.join(IMAGES,'Logo.png'))         #Logo
    image2 = Image.open(os.path.join(IMAGES,'char.png'))        #Charmander no rodapé

    st.image(image, width = 180)
    st.markdown('# Zomato Dashboard')
    st.markdown('## Informações sobre os restaurantes cadastrados em todo o mundo')

    st.markdown('''---''')

    with st.container():
        col1, col2 = st.columns([3,1])
        
        with col1:
            st.markdown('### Criado por: Maycon Rocha')
        with col2:
            st.image(image2, width = 50, output_format='auto')
            
    st.caption('Alguma dúvida ou sugestão? Entre em contato: mayconrochads@gmail.com')

#=============================================================== HOME ====================================================================================

with st.container(): #TEXTOS
    st.title('Zomato Dashboard: Home')
    
    url = 'https://www.kaggle.com/datasets/akashram/zomato-restaurants-autoupdated-dataset'
    st.markdown('Um dashboard interativo criado após uma análise dos dados da empresa Zomato Restaurants, disponibilizados na plataforma Kaggle. Você ter acesso clicando [aqui](%s).' % url)

    st.markdown(
    """
        ### Como utilizar esses Dashboard?
        No menu você tem acesso às páginas que foram divididas em métricas gerais, por país e por cidade, onde as informações vão sendo afuniladas. A depender da página selecionada você terá acesso a diferentes filtros. As páginas contém as seguintes informações:
        
        - #### Métricas Gerais :
            Dados que englobam todos os países, como quantidade de cidades e restaurantes cadastrados, valores de um prato para 2, média de avaliações e as principais culinarias.
            Nessa página você pode aplicar filtros de nota e preço.
            
        - #### Métricas de Países:
            Dados de um único país selecionado, aqui você obtém informações gerais da distribuição de restaurantes nas cidades cadastradas no país. Nessa página, além dos filtros de nota e preço você pode selecionar as cidades de interesse e se elas oferecem serviços de entrega, reserva e pedidos online.
        - #### Métricas de Cidades :
            Dados de uma única cidade selecionada, aqui você obtém informações gerais da distribuição de restaurantes nos bairros das cidades cadastradas. Nessa página você pode selecionar os bairros da cidade.
            
        #### Abaixo um mapa mundi com a distribuição dos restaurantes cadastrados:    
            """ )

with st.container(): #IMPLEMENTAÇÃO DO MAPA COM O FOLIUM

    df_map = df.loc[:,["restaurant_name", "average_cost_for_two", "currency", "aggregate_rating", "votes", "rating_color", "latitude", "longitude"]]
    df_map['average_cost_for_two'] = round(df_map['average_cost_for_two'],2)
    
    
    f = folium.Figure(width=1920, height=1080)

    m = folium.Map(max_bounds=True).add_to(f)

    marker_cluster = MarkerCluster().add_to(m)

    for _, line in df_map.iterrows():

        name = line["restaurant_name"]
        price_for_two = line["average_cost_for_two"]
        rating = line["aggregate_rating"]
        currency = line["currency"]
        votes = line["votes"]
        color = f'{line["rating_color"]}'

        html = "<p><strong>Nome do restaurante:{}</strong></p>"
        html += "<p>Preço: {} ({}) para dois"
        html += "<br />Nota: {}/5.0"
        html += "<br />Número de avaliações: {}"
        html = html.format(name, price_for_two, currency, rating, votes)

        popup = folium.Popup(
            folium.Html(html, script=True),
            max_width=600,
        )

        folium.Marker(
            [line["latitude"], line["longitude"]],
            popup=popup,
            icon=folium.Icon(color=color),
        ).add_to(marker_cluster)
        
    with st.spinner('Aguarde um momento enquanto o mapa é carregado.'): #ÍCONE DE CARREGAMENTO DO MAPA
        folium_static(m, 900, 500)

    

