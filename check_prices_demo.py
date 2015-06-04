import os
import amazonproduct
import threading 
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

    active_alerts = session.query(Alert).filter_by(active=1).all()

    for a in active_alerts[:1]:
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
        print "added price_report for product #: ", a.product.asin


def send_text(title, link):

        url = str(link)
        shortener = Shortener('TinyurlShortener')
        text_link = format(shortener.short(url))

        text_body = "Price has lowered for " + title + " " + text_link

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
    do_every(120, manipulated_product_check, 2)
    # manipulated_product_check()