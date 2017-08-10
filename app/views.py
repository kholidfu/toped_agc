import re

from flask import render_template
from app import app

from pymongo import MongoClient
import feedparser
import requests
from bs4 import BeautifulSoup as bs


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

@app.route("/product/<path:productpath>")
def detail(productpath):
    """Show item."""
    html = requests.get(productpath).content
    # import pdb; pdb.set_trace()
    soup = bs(html, "lxml")
    return soup.title.text

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
























