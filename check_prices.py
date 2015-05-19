import os
import amazonproduct
from model import User, Product, Alert, PriceReport, connect_to_db, db
from datetime import datetime
import threading 

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

def check_prices():

	date_now = datetime.utcnow()
	active_alerts = session.query(Alert).filter(date_now < Alert.expiration_date).all()

	for alert in active_alerts:
		current_search = api.item_lookup(alert.product.asin, MerchantId='Amazon', ResponseGroup='Offers, Images, ItemAttributes')

		if alert.product.price > current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount:
			print 'Send notification for: ',alert.product.title
			print 'Original price: ',alert.product.price
			print 'New price: ', current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount
		
		else:
			price_report = PriceReport(alert_id=alert.alert_id, asin=str(alert.product.asin),
									   price=int(current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount), 
									   date_checked=datetime.utcnow())

			session.add(price_report)
			session.commit()

def do_every(interval, function, iterations):
	if iterations != 0:
		threading.Timer(interval, do_every, [interval, function, 0 if iterations == 0 else iterations-1]).start()
		function()

if __name__ == '__main__':
	do_every(120, check_prices, 2)
