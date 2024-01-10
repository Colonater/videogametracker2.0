from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def get_data(searchterm):
    url = f'https://www.ebay.ca/sch/i.html?_from=R40&_nkw={searchterm}&_sop=12&_sacat=0&LH_PrefLoc=3&LH_Sold=1&LH_Complete=1&rt=nc&LH_BIN=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': "s-item__info"})[:50]
    for item in results:
        try:
            title_element = item.find('h3', {'class': 's-item__title'})
            title = title_element.text if title_element else 'N/A'
        except:
            title = 'N/A'
        try:
            solddate = item.find('span', {'class': 's-item__title--tagblock'}).find('span').text
        except:
            solddate = 'N/A'
        try:
            bids = item.find('span', {'class': 's-item__bids'}).text
        except:
            bids = 'N/A'
        soldprice_str = item.find('span', {'class': 's-item__price'}).text.replace('C', '').replace('$', '').strip()
        soldprice = float(re.findall(r'\d+\.\d+', soldprice_str)[0])
        products = {
            'title': title,
            'soldprice': soldprice,
            'solddate': solddate,
            'bids': bids,
            'link': item.find('a', {"class": 's-item__link'})['href'],
        }
        productslist.append(products)

    return productslist


@app.route('/')
def index():
    return render_template('index.html', search_term="")

@app.route('/result', methods=['POST'])
def result():
    search_term = request.form['search_term']
    ebay_data = get_data(search_term)
    products_list = parse(ebay_data)
    average_price = calculate_average_price(products_list)
    return render_template('result.html', products_list=products_list, search_term=search_term, average_price=average_price)

def calculate_average_price(products_list):
    if not products_list:
        return 0
    total_price = sum(product['soldprice'] for product in products_list)
    average_price = total_price / len(products_list)
    return average_price

if __name__ == '__main__':
    app.run(debug=True)
