import os
import amazonproduct
import threading 
import random
from model import Alert, PriceReport
from datetime import datetime
from twilio.rest import TwilioRestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pyshorteners.shorteners import Shortener

DB_URI = 'sqlite:///priceping.db'
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
    choose_from = [3, 11, 21, 28, 32, 53, 72, 92, 94, 101]
    rand_id = random.sample(choose_from, 1)
    rand_id = int(rand_id[0])

    active_alerts = session.query(Alert).filter_by(alert_id=rand_id).all()

    for a in active_alerts:

        current_search = api.item_lookup(a.product.asin, MerchantId='Amazon',
                                         ResponseGroup='Offers, Images, ItemAttributes')

        if a.product.price <= current_search\
                .Items.Item.Offers.Offer.OfferListing.Price.Amount:
            a.product.price += 5

        if a.product.price > current_search\
                .Items.Item.Offers.Offer.OfferListing.Price.Amount:
            send_text(a.product.title,
                      current_search.Items.Item.ItemLinks.ItemLink.URL)

        price_report = PriceReport(alert_id=a.alert_id,
                                   asin=str(a.product.asin),
                                   price=int(current_search.Items.Item.Offers.Offer.OfferListing.Price.Amount),
                                   date_checked=datetime.utcnow())

        session.add(price_report)
        session.commit()
        print "Added price_report for product #:", a.product.asin


def send_text(title, link):

        url = str(link)
        shortener = Shortener('TinyurlShortener') 
        print "My short url is {}".format(shortener.short(url))
        text_link = format(shortener.short(url))

        text_body = "Price has lowered for " + title + " " + text_link

        client.messages.create(
            to="3153825951",
            from_="+14159643618",
            body=text_body,
        )

        print "Sent text"




if __name__ == '__main__':
    manipulated_product_check()
