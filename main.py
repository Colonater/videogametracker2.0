from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import sys

app = Flask(__name__)


def get_data(searchterm):
    url = f'https://www.ebay.ca/sch/i.html?_from=R40&_nkw={searchterm}&_sop=12&_sacat=0&LH_PrefLoc=3&LH_Sold=1&LH_Complete=1&rt=nc&LH_BIN=1'
    r = requests.get(url)

    # Print whether the request was successful or not
    if r.status_code == 200:
        print(f"Search for '{searchterm}' successful!")
    else:
        print(f"Search for '{searchterm}' failed. Status Code: {r.status_code}")

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

games = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global games
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'search':
            search_term = request.form.get('search_term')
            ebay_data = get_data(search_term)
            products_list = parse(ebay_data)

            # Calculate average price
            average_price = calculate_average_price(products_list)

            # Add the game to the games list
            game = {'name': search_term, 'average_price': average_price}
            games.append(game)

        elif action == 'delete':
            selected_games = request.form.getlist('delete_games[]')
            selected_games = [int(index) for index in selected_games]

            # Remove games in reverse order to avoid index errors
            for index in sorted(selected_games, reverse=True):
                if 0 <= index < len(games):
                    del games[index]

    total_price = calculate_total_price(games)
    return render_template('index.html', search_term="", games=games, total_price=total_price)

def calculate_average_price(products_list):
    if not products_list:
        return 0
    total_price = sum(product['soldprice'] for product in products_list)
    average_price = total_price / len(products_list)
    return average_price

def calculate_total_price(games):
    total_price = sum(game['average_price'] for game in games)
    return total_price

if __name__ == '__main__':
    app.run(debug=True)
