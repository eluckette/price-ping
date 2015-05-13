import os
import amazonproduct
from model import User, Product, Alert, connect_to_db, db
from datetime import datetime

amazon_api_config = {
	'access_key': os.environ['AMAZON_ACCESS_KEY'],
	'secret_key': os.environ['AMAZON_SECRET_KEY'],
	'associate_tag': os.environ['AMAZON_ASSOCIATE_TAG'],
	'locale': 'us'
}

api = amazonproduct.API(cfg=amazon_api_config)

def find_active_alerts():
	


if __name__ == '__main__':
	find_active_alerts()