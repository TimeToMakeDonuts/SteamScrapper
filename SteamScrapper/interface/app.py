import requests
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime
from math import ceil
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Connection to MongoDB
client = MongoClient("mongodb://mongodb-service:27017/")
db = client["steam_scraper"]
collection = db["games"]

# Load category tags from the JSON file
with open('categories.json', 'r') as f:
    CATEGORY_TAGS = json.load(f)

def sort_results(results, sort_by, order):
    reverse = (order == 'desc')
    if sort_by == 'date':
        results = sorted(results, key=lambda x: parse_date(x[sort_by]), reverse=reverse)
    elif sort_by in ['price_before', 'price_after']:
        results = sorted(results, key=lambda x: float(x[sort_by].replace('zł', '').replace(',', '.')) if 'zł' in x[sort_by] else 0, reverse=reverse)
    elif sort_by == 'categories':
        results = sorted(results, key=lambda x: ', '.join(x['categories']) if 'categories' in x else '', reverse=reverse)
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category_names = request.form.get('categories', '').split(',')
        pages_per_category = int(request.form.get('pages', 5))  # Number of pages to scrape per category

        if not category_names:
            return render_template('index.html', error='Please enter at least one category.')

        invalid_categories = [category for category in category_names if category.strip().lower() not in CATEGORY_TAGS]
        if invalid_categories:
            return render_template('index.html', error=f'Invalid categories: {", ".join(invalid_categories)}')

        selected_categories = {CATEGORY_TAGS[category.strip().lower()]: category.strip().lower() for category in category_names if category.strip().lower() in CATEGORY_TAGS}
        base_url = 'https://store.steampowered.com/search/?category1=998&tags='

        # Make a POST request to the engine service to start scraping
        engine_url = 'http://engine-service:5001/scrape'  # Use the Kubernetes service name
        response = requests.post(engine_url, json={
            'base_url': base_url,
            'categories': selected_categories,
            'pages_per_category': pages_per_category
        })

        session['categories'] = list(selected_categories.values())
        return redirect(url_for('results', page=1, sort_by='name', order='asc'))

    return render_template('index.html', categories=CATEGORY_TAGS.keys())

@app.route('/results')
def results():
    categories = session.get('categories', [])
    if not categories:
        return redirect(url_for('index'))

    page_num = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')

    # Filter by categories
    selected_categories = request.args.getlist('categories')
    if not selected_categories:
        selected_categories = categories

    query = {"categories": {"$in": selected_categories}}
    results = list(collection.find(query))

    # Sorting the results
    results = sort_results(results, sort_by, order)

    start = (page_num - 1) * 10
    end = start + 10
    paginated_results = results[start:end]
    total_pages = ceil(len(results) / 10)

    # Pagination display logic
    display_pages = 5  # Number of pages to display at once
    start_page = max(1, page_num - display_pages // 2)
    end_page = min(total_pages, start_page + display_pages - 1)
    pagination_range = range(start_page, end_page + 1)

    return render_template('results.html', results=paginated_results, pages=pagination_range, current_page=page_num,
                           sort_by=sort_by, order=order, categories=categories, selected_categories=selected_categories,
                           total_pages=total_pages)

@app.route('/show_existing_data')
def show_existing_data():
    page_num = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')

    # Get distinct categories from the database
    distinct_categories = collection.distinct('categories')
    selected_categories = request.args.getlist('categories')

    query = {}  # Fetch all records
    if selected_categories:
        query = {"categories": {"$in": selected_categories}}

    results = list(collection.find(query))

    # Sorting the results
    results = sort_results(results, sort_by, order)

    start = (page_num - 1) * 10
    end = start + 10
    paginated_results = results[start:end]
    total_pages = ceil(len(results) / 10)

    # Pagination display logic
    display_pages = 5  # Number of pages to display at once
    start_page = max(1, page_num - display_pages // 2)
    end_page = min(total_pages, start_page + display_pages - 1)
    pagination_range = range(start_page, end_page + 1)

    return render_template('results.html', results=paginated_results, pages=pagination_range, current_page=page_num,
                           sort_by=sort_by, order=order, total_pages=total_pages, categories=distinct_categories, selected_categories=selected_categories)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

