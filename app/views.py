import re

from flask import render_template
from app import app

from pymongo import MongoClient
import feedparser
import requests
from bs4 import BeautifulSoup as bs
import shortuuid


# build db connections
client = MongoClient()
db = client.toped

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
    price = price.replace(".", "")
    price = int(price)
    price = price * 2.0
    return "{:0,.0f}".format(price).replace(",", ".")

@app.template_filter('mongoinsert')
def mongoinsert(url):
    # import pdb; pdb.set_trace()
    item_exist = db.product.find_one(url)
    oid = shortuuid.uuid(name=url)
    if not item_exist:
        db.product.insert({'url': url, 'oid': oid})
    return oid

@app.route("/")
def index():
    """
    - Show latest item from feed.
    - URL target (tokped), masked with shortuuid.
    """
    url = "https://www.tokopedia.com/feed?sc=78"
    data = feedparser.parse(url)
    data = data['entries']
    return render_template("index.html", data=data)

@app.route("/product/<oid>")
def detail(oid):
    """Show item."""
    url = db.product.find_one({'oid': oid})['url']
    html = requests.get(url).content
    soup = bs(html, "lxml")
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
    # insert into db
    data = {'title': title, 'description': description, 'price': price, 'images': images}
    # render in template
    return render_template("detail.html", data=data)

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
























