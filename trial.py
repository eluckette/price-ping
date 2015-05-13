import amazonproduct
import os
# from lxml import objectify
# import codecs

config = {
	'access_key': os.environ['AMAZON_ACCESS_KEY'],
	'secret_key': os.environ['AMAZON_SECRET_KEY'],
	'associate_tag': os.environ['AMAZON_ASSOCIATE_TAG'],
	'locale': 'us'
}

api = amazonproduct.API(cfg=config)


# amazon_search = api.item_search('Toys', Keywords='Lego', MerchantId='Amazon', ResponseGroup='Offers, ItemAttributes, Images')

# for item in amazon_search:
# 	print "ASIN: ", item.ASIN
# 	print "Price: ", item.Offers.Offer.OfferListing.Price.FormattedPrice
# 	print "Link: ", item.ItemLinks.ItemLink.URL

# print '******************************************************************************'

legos = api.item_lookup('B00NHQFA1I', MerchantId='Amazon', ResponseGroup='Offers, Images, ItemAttributes')

print "ASIN: ", legos.Items.Item.ASIN
print "Parent ASIN: ", legos.Items.Item.ASIN
print "More offers URL: ", legos.Items.Item.Offers.MoreOffersUrl
print "Offer Listing ID: ", legos.Items.Item.Offers.Offer.OfferListing.OfferListingId
print "Amount: ", legos.Items.Item.Offers.Offer.OfferListing.Price.Amount
print "Formatted Price: ", legos.Items.Item.Offers.Offer.OfferListing.Price.FormattedPrice

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



	# <label>Phone Number:
	# 	<input type='tel' pattern='[0-9]{10}' 
	# 	title='Phone Number (Format: 19999999999)' name='phone_number' required>
	# </label>

