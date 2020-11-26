import requests
from bs4 import BeautifulSoup as bs
import re
import numpy as np
import pandas as pd


def get_content(url):
    headers = {'User Agent': 'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    r = requests.get(url, headers=headers)
    return bs(r.content)


def translate_color(colors):
    color_names = {
        'juoda' : 'black',
        'mėlyna' : 'blue',
        'pilka' : 'grey',
        'balta' : 'white',
        'raudona': 'red',
        'žalia' : 'green',
        'sidabro':'silver',
        'aukso':'gold',
        'violetinė':'purple',
        'oranžinė':'orange',
        'rožinė':'pink',
        'geltona':'yellow',
        'ruda':'brown',
        'smėlio':'sand',
        'įvairių spalvų':'multi-color',
        'samanų': 'moss'
    }
    if type(colors) == str and colors != 'nan':
        colors = colors.lower()
        result = []
        multic = colors.split(',')
        if len(multic) > 1:
            for c in multic:
                result.append(color_names[c.strip()])
            return result
        else: 
            return color_names[colors]


pages_list = []
for x in range(1, 16):
    pages_list.append('https://www.egzample-web.com/lol/2ps?page={}'.format(x))


url_list = []
main_url = 'https://www.egzample-web.com'
for page in pages_list:
    soup = get_content(page)
    page_urls = soup.find_all('div', {'class': 'catalog-taxons-product__hover'})
    for item in page_urls:
        url_list.append(main_url + item.find('a', {'class': 'catalog-taxons-product__name'})['href'])


raw_data = []
for index, url in enumerate(url_list):
    try:
        temp_dict = {}
        soap = get_content(url)
        table = soap.find('table', {'class': 'info-table'})
        row = table.select('tr')
        for items in row:
            row_values = items.select('td')
            if len(row_values) > 1:
                row_name = items.find('td').text.split('\n\n\n\n')[0].replace('\n', '')
                row_value = items.select('td')[1].text.replace('\n', '')
                temp_dict[row_name] = row_value
                price_span = soap.find('div', {'class': 'product-price-details__block'})
                temp_dict['Price'] = price_span.text.replace('\n', '').split('€')[0].replace(' ', '').replace(',', '.')
        raw_data.append(temp_dict)
        if index % 100 == 0:
            print(f'{index} completed')
    except Exception as e:
        print(e)


raw_df = pd.DataFrame(raw_data)
df = pd.DataFrame()

df['Product_Name'] = raw_df['Modelis'] 
df['Brand'] = raw_df['Prekės ženklas']
df['Price'] = raw_df['Price']
df['Memory_GB'] = raw_df['Atminties talpa']
df['Color'] = raw_df['Spalva']


df.Color = df.Color.apply(lambda x: translate_color(x))

df.to_csv('retailer_B_data', index=False)