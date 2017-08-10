
# Build a dropship store using Tokopedia Data
- Markup the price
- Show Google Form when Visitor Click Buy
- Admin process the order from Vendor

# Purpose
- Get money from dropship price difference
- Get data about what product is currently HOT on market

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
- [x] remove phone number from description (with regex)
- [x] remove LINE from description
- [ ] full-text-search on title and description
- [ ] save hot product via stats
- [ ] save customer dbase
- [ ] generate fake review but fixed (separate collection,
  i.e. review)
- [ ] save image
- [ ] show related product
- [ ] fix pricing

### FRONT-END
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
