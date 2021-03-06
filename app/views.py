import re

from flask import render_template
from flask import request, redirect, url_for
from app import app

from pymongo import MongoClient
import feedparser
import requests
from bs4 import BeautifulSoup as bs
import shortuuid
import slugify
from flask_paginate import Pagination, get_page_parameter


# build db connections
client = MongoClient()
db = client.toped


CATEGORIES = {
    'sepatu-cowok': 'Sepatu Cowok',
    'sepatu-cewek': 'Sepatu Cewek',
    'tas': 'Tas',
    'setelan-cowok': 'Setelan Cowok',
    'setelan-cewek': 'Setelan Cewek',
    'kaos-cowok': 'Kaos Cowok',
    'kaos-cewek': 'Kaos Cewek',
    'legging': 'Legging',
    'piyama': 'Piyama',
    'rok': 'Rok',
    'jaket-cowok': 'Jaket Cowok',
    'jaket-cewek': 'Jaket Cewek',
}


@app.context_processor
def categories():
    """define categories, available in the whole template."""
    return {'categories': CATEGORIES}


@app.template_filter('get_harga')
def get_harga(s):
    """Return harga."""
    pattern = re.compile(r"Harga : Rp (.*?) <br>")
    return re.search(pattern, s).group(1).replace('.', '')

@app.template_filter('get_image')
def get_image(s):
    """Return image source URL."""
    pattern = re.compile(r"img src=\"(.*?)\"" )
    return re.search(pattern, s).group(1).replace('100-square', '200-square')

@app.template_filter('get_lokasi')
def get_lokasi(s):
    """Return location string."""
    pattern = re.compile(r"Lokasi : (.*?) <br>")
    return re.search(pattern, s).group(1)

@app.template_filter('markup')
def markup(price):
    """return markuped price"""
    return "{:0,.0f}".format(int(int(price) * 2.0)).replace(",", ".")

@app.template_filter('markup_price_for_detail_page')
def markup_price_for_detail_page(price):
    """return markuped price."""
    return "{:0,.0f}".format(price).replace(",", ".")

@app.template_filter('mongoinsert')
def mongoinsert(url):
    """insert url and oid data into mongodb."""
    item_exist = db.product.find_one({'url': url})
    oid = shortuuid.uuid(name=url)
    if not item_exist:
        db.product.insert({'url': url, 'oid': oid})
    return oid

@app.template_filter('squared')
def squared(url):
    """return squared image from toped link."""
    return url.replace('/300/', '/300-square/')


@app.route("/")
def index():
    """
    - Show latest item from feed.
    - URL target (tokped), masked with shortuuid.
    - Insert URL and OID into db, later will be updated by single page.
    """
    url = "https://www.tokopedia.com/feed?sc=78"
    data = feedparser.parse(url)
    data = data['entries']
    return render_template("index.html", data=data)

@app.route("/product/<oid>")
def detail(oid):
    """Steps:
    - Get HTML
    - Souped with BS4
    - Extract Needed Data
    - Update into DB using URL as OID identifier
    - Hit counter
    """
    item = db.product.find_one({'oid': oid})

    # HTTP Request
    url = item['url']
    html = requests.get(url).content
    soup = bs(html, "lxml")

    # EXTRACT NEEDED DATA
    title = soup.find('h1').text
    description = soup.find(itemprop='description')
    price = soup.find(itemprop='price').text
    
    # get images and replace thumbnail (100-square) with bigger one (300-square)
    raw_images = [i['src'] for i in soup.findAll(itemprop='image')]
    images = []
    for i in raw_images:
        if '100-square' in i:
            images.append(i.replace('100-square', '300-square'))
        else:
            images.append(i)

    # STRUCTURING DATA
    ## turn price into int
    price = int(price.replace('.', '')) * 2
    # convert into string
    description = str(description)
    # remove phone number from string ==> https://regex101.com/r/qtEg6H/4
    pattern = r"\(?(?:\+62|62|0)(?:\d{2,3})?\)?[ .-]?\d{2,4}[ .-]?\d{2,4}[ .-]?\d{2,4}"
    description = re.sub(pattern, "", description)
    # remove url from any given text string
    pattern = r"http\S+"
    description = re.sub(pattern, '', description)
    # remove LINE
    pattern = re.compile(r"LINE[ ]?:[ ]?", re.I)
    description = re.sub(pattern, "", description)

    ## newly scraped data
    scraped_data = {'title': title, 'description': description, 'price':
            price, 'images': images}
    
    # RETRIEVE/INSERT DATA INTO DB
    if item.get('title'):
        data = db.product.find_one({'url': url})
    else:
        db.product.update_one({'oid': oid}, {
            "$set": scraped_data}, upsert=True)
        data = db.product.find_one({'url': url})

    # Increment data
    db.product.update_one({'oid': oid}, {'$inc': {'hits': 1}})
        
    # RENDER DATA INTO TEMPLATE
    return render_template("detail.html", data=data)

@app.route("/category/<cat_name>")
def category(cat_name):
    """category page."""
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 3
    offset = (page - 1) * per_page

    data = db.product.find({'$text': {'$search': cat_name}}, {'score':
                                                             {'$meta':
                                                              'textScore'}}).sort([('score', {'$meta': 'textScore'})]).skip(offset).limit(per_page)
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=data.count(),
                            css_framework='bootstrap3',
                            search=False,
                            record_name='products')

    cat_name = cat_name.replace('-', ' ').title()
    return render_template("category.html", cat_name=cat_name,
                           data=data, pagination=pagination)

@app.route("/search")
def redirect_search():
    """Redirect search to search route."""
    keyword = request.args.get('keyword').replace(' ', '-')
    return redirect(url_for('search', keyword=keyword))

@app.route("/search/<keyword>")
def search(keyword):
    """Search page."""
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 3
    offset = (page - 1) * per_page
    data = db.product.find({'$text': {'$search': keyword}}, {'score':
                                                             {'$meta':
                                                              'textScore'}}).sort([('score', {'$meta': 'textScore'})]).skip(offset).limit(per_page)
    
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=data.count(),
                            css_framework='bootstrap3',
                            search=False,
                            record_name='products')
    
    keyword_title = keyword.replace('-', ' ').title()
    return render_template("search.html",
                           keyword_title=keyword_title,
                           data=data,
                           pagination=pagination
    )

@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    """Privacy policy page."""
    return render_template("privacy.html")

@app.route("/dmca")
def dmca():
    """DMCA Page."""
    return render_template("dmca.html")
