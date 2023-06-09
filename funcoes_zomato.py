#FUNÇÕES CRIADAS PARA ELABORAÇÃO DA PÁGINA
import inflection 

from datetime import date
from currency_converter import CurrencyConverter

#ALTERAÇÃO DO CÓDIGO DOS PAÍSES PELOS RESPECTIVOS NOMES
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
#Converte os códigos em paises
def country_name(country_id):
        
    country_id = [COUNTRIES[id] for id in country_id] 
 
    return country_id


#ALTERAÇÃO DOS CÓDIGOS DE CORES PELO NOME DAS RESPECTIVAS CORES
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_transform(color_code):
    
    color_name = [COLORS[color] for color in color_code]
    
    return color_name


#ALTERAÇÃO DO CÓDIGO DE PREÇO PELO RESPECTIVO NOME DA "CLASSE" DE PREÇO
def create_price_type(price_range):
    return ["cheap" if price == 1 else "normal" if price == 2 else "expensive" if price == 3 else "gourmet" for price in price_range]

#RENOMEIA AS COLUNAS DO DATAFRAME RETIRANDO ESPAÇOS, DEIXANDO TUDO MINUSCULO E SUBSTITUINDO OS ESPAÇOS POR _
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

#CONVERSÃO DO NOME DAS MOEDAS PARA SUA SIGLA
currency_mapping = {
    'Botswana Pula(P)': 'BWP',
    'Brazilian Real(R$)': 'BRL',
    'Dollar($)': 'USD',
    'Emirati Diram(AED)': 'AED',
    'Indian Rupees(Rs.)': 'INR',
    'Indonesian Rupiah(IDR)': 'IDR',
    'NewZealand($)': 'NZD',
    'Pounds(£)': 'GBP',
    'Qatari Rial(QR)': 'QAR',
    'Rand(R)': 'ZAR',
    'Sri Lankan Rupee(LKR)': 'LKR',
    'Turkish Lira(TL)': 'TRY'
}
def currencies_with_codes(currency_name):
    return [currency_mapping[currency] for currency in currency_name]

#CONVERSÃO DAS MOEDAS PARA DOLAR
def convert_to_dollar(amounts, from_currencies):
    c = CurrencyConverter()
    converted_amounts = []
    
    manual_conversions = {  #MOEDAS NÃO LISTADAS FORAM ADICIONADAS MANUALMENTE 
        'BWP': 0.091,   # Valor de conversão manual para Botswana Pula
        'AED': 0.27,    # Valor de conversão manual para Emirati Diram
        'QAR': 0.27,    # Valor de conversão manual para Qatari Rial
        'LKR': 0.0051   # Valor de conversão manual para Sri Lankan Rupee
    }
    
    for amount, from_currency in zip(amounts, from_currencies):
        if from_currency in c.currencies:
            converted_amount = c.convert(amount, from_currency, 'USD', date=date(2019, 4,10))
            converted_amounts.append(converted_amount)
        elif from_currency in manual_conversions:
            manual_conversion = manual_conversions[from_currency]
            converted_amount = amount * manual_conversion
            converted_amounts.append(converted_amount)
        else:
            converted_amounts.append(None)  # Adiciona None para indicar que a conversão não é suportada
    
    return converted_amounts

#LIMPEZA DO DATAFRAME
def limpeza_tratamento(dforiginal):
    df = dforiginal.drop_duplicates(keep='first', ignore_index=True).copy()


    df['Currency'] = currencies_with_codes(df['Currency'].to_list())
    df['Country'] = country_name(df['Country Code'].to_list()); df = df.drop('Country Code', axis=1)
    df['Rating_Color'] = color_transform(df['Rating color'].to_list()); df = df.drop('Rating color', axis=1)
    df['Price range'] = create_price_type(df['Price range'].to_list())
    df['Average Cost for two'] = convert_to_dollar(df['Average Cost for two'].to_list(),df['Currency'].to_list()); df['Currency'] = ['USD' for i in df['Currency'].to_list()]
    df = df[(df['Average Cost for two'] != 0) ]
    df = df[(df['Average Cost for two'] < 1000)]
    df = rename_columns(df)
    
    return df

#OPERAÇÕES DE AGRUPAMENTO
def ope_df(df, cols, group, dic):

    resultado = df.loc[:,cols].groupby(group).agg(dic).reset_index()

    return resultado

#EXPADIR O DATAFRAME DE UMA COLUNA QUE TEM LISTAS COMO VALORES
def explode_column(df,col,group):
    df_exp = df.loc[:,[group, col]]
    df_exp = df_exp[df_exp[col].notnull()]
    df_exp[col] = [x.split(sep=',') for x in df_exp[col]]
    df_exp = df_exp.explode(col,ignore_index=True)
    df_exp[col] = df_exp[col].str.strip().copy()
    return df_exp