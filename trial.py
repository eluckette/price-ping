import amazonproduct
import os
import json
# from lxml import objectify
# import codecs

config = {
	'access_key': os.environ['AMAZON_ACCESS_KEY'],
	'secret_key': os.environ['AMAZON_SECRET_KEY'],
	'associate_tag': os.environ['AMAZON_ASSOCIATE_TAG'],
	'locale': 'us'
}

api = amazonproduct.API(cfg=config)


amazon_search = api.item_search('Toys', Keywords='Lego', MerchantId='Amazon', ResponseGroup='Offers, ItemAttributes, Images')

# json_string = {}

# for item in amazon_search:
# 	json_string['Link'] = item.ItemLinks.ItemLink.URL


search_dict = {}

for item in amazon_search:
	search_dict[str(item.ASIN)] = [str(item.ItemAttributes.Title),
							       str(item.Offers.Offer.OfferListing.Price.FormattedPrice), 
							       str(item.Offers.Offer.OfferListing.Price.Amount), 
							       str(item.ItemLinks.ItemLink.URL)]

print type(search_dict)
jsonarray = json.dumps(search_dict)





# print type(amazon_search)
# print amazon_search.results;
# print amazon_search.pages;

# print '\n\n\n This is the amazon search page 4', amazon_search.page(4)


# print '*****************'
# for item in amazon_search.page(4):
# 	print item.Items.Item.ASIN
# 	print type(item.Items)
# restrict = 0
# for item in amazon_search:
# 	while restrict < 20:
# 		print "ASIN: ", item.ASIN
# 		restrict = restrict + 1




# limit = 20
# for i in range(limit):
# 	print tyamazon_search[i].ASIN

# for item in amazon_search:
# 	if restrict >= 20:
# 		break
# 	else:
# 		print "ASIN: ", item.ASIN
# 		restrict = restrict + 1

# amazon_results = {}
# restrict = 0
# for item in amazon_search:
# 	if restrict >= 20:
# 		break
# 	else:
# 		amazon_results[item.ASIN] = item.ItemLinks.ItemLink.URL

# print amazon_results
# 	print dir(item.ItemAttributes)
# 	print "ASIN: ", item.ASIN
# 	print "Price: ", item.Offers.Offer.OfferListing.Price.FormattedPrice
# 	print "Link: ", item.ItemLinks.ItemLink.URL


# legos = api.item_lookup('B00NHQFA1I', MerchantId='Amazon', ResponseGroup='Offers, Images, ItemAttributes')

# print "ASIN: ", legos.Items.Item.ASIN
# print "Parent ASIN: ", legos.Items.Item.ASIN
# print "More offers URL: ", legos.Items.Item.Offers.MoreOffersUrl
# print "Offer Listing ID: ", legos.Items.Item.Offers.Offer.OfferListing.OfferListingId
# print "Amount: ", legos.Items.Item.Offers.Offer.OfferListing.Price.Amount
# print "Formatted Price: ", legos.Items.Item.Offers.Offer.OfferListing.Price.FormattedPrice

# Image: http://ecx.images-amazon.com/images/I/51wH8x4c-hL._SL160_.jpg
# ASIN: B00NHQFA1I
# Title: LEGO Classic Medium Creative Brick Box
# Price: 2550
# Price: $25.50

# No Image
# LINK http://www.amazon.com/LEGO-Classic-Medium-Creative-Brick/dp/tech-data/B00NHQFA1I%3FSubscriptionId%3DAKIAJ7MJZ5JUEYMH5ZLQ%26tag%3Dhawkeye049-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB00NHQFA1I
# TITLE:  LEGO Classic Medium Creative Brick Box
# FORMATTED AMOUNT:  $25.50
# FEATURES: None

# import ipdb; ipdb.set_trace()

