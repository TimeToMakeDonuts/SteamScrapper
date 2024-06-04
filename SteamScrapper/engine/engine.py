from flask import Flask, request, jsonify
import asyncio
import aiohttp
import json
from math import ceil
from datetime import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Połączenie z MongoDB
client = MongoClient("mongodb://mongodb-service:27017/")
db = client["steam_scraper"]
collection = db["games"]

def parse_html(html, category_name):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.search_result_row')  # Selector for the game items in search results
    results = []
    for item in items:
        name_elem = item.select_one('.title')
        link_elem = item['href']
        thumbnail_elem = item.select_one('.search_capsule img')['src']
        price_before_elem = item.select_one('.discount_original_price')
        price_after_elem = item.select_one('.discount_final_price')
        date_elem = item.select_one('.search_released')

        name = name_elem.text.strip() if name_elem else 'Brak danych'
        link = link_elem.strip() if link_elem else '#'
        thumbnail = thumbnail_elem.strip() if thumbnail_elem else '#'
        price_before = price_before_elem.text.strip() if price_before_elem else 'No discount'
        price_after = price_after_elem.text.strip() if price_after_elem else 'Brak danych'
        date = date_elem.text.strip() if date_elem else 'Brak danych'

        results.append({
            'name': name,
            'link': link,
            'thumbnail': thumbnail,
            'price_before': price_before,
            'price_after': price_after,
            'date': date,
            'category': category_name
        })
    return results


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def generate_urls(base_url, categories, pages_per_category):
    urls = []
    for category in categories:
        for page in range(1, pages_per_category + 1):
            urls.append(f'{base_url}{category}&page={page}')
    return urls

async def scrape_data(base_url, categories, pages_per_category):
    async with aiohttp.ClientSession() as session:
        all_results = []
        for category, category_name in categories.items():
            urls = generate_urls(base_url, [category], pages_per_category)
            tasks = [fetch(session, url) for url in urls]
            pages = await asyncio.gather(*tasks)

            for html in pages:
                results = parse_html(html, category_name)
                all_results.extend(results)

        return all_results

def upsert_to_mongo(results):
    for result in results:
        existing = collection.find_one({'name': result['name']})
        if existing:
            # Update the existing document with the new category if it's not already there
            if 'categories' not in existing:
                existing['categories'] = []
            if result['category'] not in existing['categories']:
                collection.update_one(
                    {'_id': existing['_id']},
                    {'$addToSet': {'categories': result['category']}, '$set': {'link': result['link'], 'thumbnail': result['thumbnail']}}
                )
        else:
            # Insert the new document with the category in an array
            result['categories'] = [result['category']]
            del result['category']
            collection.insert_one(result)


def sort_results(results, sort_by, order):
    reverse = (order == 'desc')
    if sort_by == 'date':
        results = sorted(results, key=lambda x: parse_date(x[sort_by]), reverse=reverse)
    elif sort_by in ['price_before', 'price_after']:
        results = sorted(results, key=lambda x: float(x[sort_by].replace('zł', '').replace(',', '.')) if 'zł' in x[sort_by] else 0, reverse=reverse)
    else:
        results = sorted(results, key=lambda x: x[sort_by], reverse=reverse)
    return results
    
def parse_date(date_str):
    if date_str == 'Brak danych':
        return datetime.min
    try:
        return datetime.strptime(date_str, '%d %b, %Y')
    except ValueError:
        return datetime.strptime('01 ' + date_str, '%d %b %Y')
        
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    base_url = data.get('base_url')
    categories = data.get('categories')
    pages_per_category = data.get('pages_per_category')

    results = asyncio.run(scrape_data(base_url, categories, pages_per_category))
    upsert_to_mongo(results)
    return jsonify({'status': 'success', 'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

