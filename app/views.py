import re

from flask import render_template
from app import app

import feedparser


@app.template_filter('get_harga')
def get_harga(s):
    return re.search(re.compile(r"Harga : Rp (.*?) <br>"), s).group(1).replace('.', '')

@app.template_filter('get_image')
def get_image(s):
    return re.search(re.compile(r"img src=\"(.*?)\"" ), s).group(1).replace('100-square', '200-square')

@app.template_filter('get_lokasi')
def get_lokasi(s):
    return re.search(re.compile(r"Lokasi : (.*?) <br>"), s).group(1)

@app.template_filter('markup')
def markup(price):
    """return markuped price"""
    return "{:0,.0f}".format(int(int(price) * 2.0)).replace(",", ".")

@app.route("/")
def hello():
    url = "https://www.tokopedia.com/feed?sc=78"
    data = feedparser.parse(url)
    data = data['entries']
    return render_template("index.html", data=data)

@app.route("/about")
def kat_anak():
    return render_template("about.html")
