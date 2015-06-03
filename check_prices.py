import os
import amazonproduct
from model import User, Product, Alert, PriceReport, connect_to_db, db
from datetime import datetime
import threading 
from twilio.rest import TwilioRestClient 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URI = 'sqlite:///hbproj.db'
engine = create_engine(DB_URI, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


amazon_api_config = {
	'access_key': os.environ['AMAZON_ACCESS_KEY'],
	'secret_key': os.environ['AMAZON_SECRET_KEY'],
	'associate_tag': os.environ['AMAZON_ASSOCIATE_TAG'],
	'locale': 'us'
}

api = amazonproduct.API(cfg=amazon_api_config)


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID'] 
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 

def manipulated_product_check():
	"""manipulates price of alert to test text to user"""

	active_alerts = session.query(Alert).filter_by(active=1).all()

	for a in active_alerts[:1]:
		current_search = api.item_lookup(a.product.asin, MerchantId='Amazon', ResponseGroup='Offers, Images, ItemAttributes')
		
		if a.product.price <= current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount:
			a.product.price += 5
		
		if a.product.price  > current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount:
			title = a.product.title
			origninal_price = a.product.price
			new_price = current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount
			
			send_text(title, origninal_price, new_price)
		
		price_report = PriceReport(alert_id=a.alert_id, asin=str(a.product.asin),
							   price=int(current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount), 
							   date_checked=datetime.utcnow())
		
		print "added price_report"
		session.add(price_report)
		session.commit()


def check_prices():

	active_alerts = session.query(Alert).filter_by(active=1).all()

	for alert in active_alerts:
		current_search = api.item_lookup(alert.product.asin, MerchantId='Amazon', ResponseGroup='Offers, Images, ItemAttributes')

		if alert.product.price > current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount:
			title = alert.product.title
			origninal_price = alert.product.price
			new_price = current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount
			
			send_text(title, origninal_price, new_price)
		
		price_report = PriceReport(alert_id=alert.alert_id, asin=str(alert.product.asin),
								   price=int(current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount), 
								   date_checked=datetime.utcnow())
		print "added price_report"
		session.add(price_report)
		session.commit()

	return active_alerts

def send_text(title, origninal_price, new_price):

		text_body = "Price has lowered for " + title 

		client.messages.create(
		to="3153825951", 
		from_="+14159643618", 
		body=text_body,
		)


def do_every(interval, function, iterations):
	if iterations != 0:
		threading.Timer(interval, do_every, [interval, function, 0 if iterations == 0 else iterations-1]).start()
		function()

if __name__ == '__main__':
	# do_every(120, check_prices, 2)
	manipulated_product_check()
