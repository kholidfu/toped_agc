
# Build a dropship store using Tokopedia Data
- Markup the price
- Show Google Form when Visitor Click Buy
- Admin process the order from Vendor

# Purpose
- Get money from dropship price difference
- Get data about what product is currently HOT on market

# Dependencies

## 3rd party lib
   ```
   pip install -r requirements.txt
   ```
## mongo 3.4
   ```
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
   echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
   sudo apt-get update && sudo apt-get install -y mongodb-org
   ```

## Setup Mongo Full-Text Search
   ```
   db.product.createIndex( { title: "text", description: "text" } )
   ```

### Example query

    db.product.find( { $text: { $search: "sepatu" } } )

or in python way
	
	db.product.find({'$text': {'$search': 'sepatu'}})
	
search and sort based on text score (this is I used)

	db.product.find({'$text': {'$search': keyword}}, {'score': {'$meta': 'textScore'}}).sort([('score', {'$meta': 'textScore'})])

### Drop Index

change index name according to your index name, if default, it's named
like below

	db.product.dropIndex("title_text_description_text")

### Re-create Index with weight and name it "TextIndex"

	db.product.createIndex( { title: "text", description: "text" }, {weights: {title: 10, description: 5}, name: "TextIndex"} )

# Run
## mongodb
   ```
   sudo service mongod start
   ```
## Flask
   ```
   FLASK_APP=app/views FLASK_DEBUG=1 flask run
   ```

## Detail View
- Price (markup)
- Product Description
- Image[s] (hotlink)
- Location
- Seller
  - Reputation
  - Name
- <Buy Now Button> --> Goes to google form :) or redirect to original
  page.

## PRICING
- If price < 50.000: price * 2
- If price 50.000 - 100.000: price * 1.5
- If price 100.000 - 150.000: price * 1.3
- If price 150.000 - 200.000: price * 1.25
- If price > 200.000: price * 1.2

## TODO

So much work todo, easy brad... Do it one by one...

### BACKEND
#### MUST
- [x] remove phone number from description (with regex)
- [x] remove LINE from description
- [x] generate fake review but fixed (separate collection,
  i.e. review) --> /app/resources/review.txt
- [x] full-text-search on title and description
- [x] add hit counter (masih ada bug, incr by 2?)
- [x] add simple search feature
- [x] remove all kind of links from description, kadang kecantol link
  ke tokopedia
- [ ] add more weight to title in search results
- [ ] search pagination
- [ ] save customer data
- [ ] save image
- [ ] show related product
- [ ] fix pricing

#### OPTIONAL
- [ ] filter only from good reputation seller

### FRONT-END
- [x] banner on front-page
- [x] better font other than default bootstrap
- [ ] fix image carousel on detail page
- [ ] show buy button
- [ ] show form for order
- [ ] show fake review (more is better)
- [ ] show related product
- [ ] better template to ensure customers
- [ ] only show images if it exists
- [ ] show price range

### SEO
#### ONPAGE
- [ ] h1, h2, h3
- [ ] title, meta desc, feed url
- [ ] show latest product in single page
- [ ] breadcrumb
- [ ] feed
- [ ] sitemap
- [ ] pinger
