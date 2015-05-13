import os 
import amazonproduct

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Product, Alert, connect_to_db, db
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

amazon_api_config = {
	'access_key': os.environ['AMAZON_ACCESS_KEY'],
	'secret_key': os.environ['AMAZON_SECRET_KEY'],
	'associate_tag': os.environ['AMAZON_ASSOCIATE_TAG'],
	'locale': 'us'
}

api = amazonproduct.API(cfg=amazon_api_config)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/search-amazon', methods=['GET'])
def handle_search():
	
	category = request.args['category']
	user_input = request.args['user_input']

	search_results = api.item_search(category, Keywords=user_input, MerchantId='Amazon', 
									 ResponseGroup='Offers, ItemAttributes, Images')
	
	return render_template('search-results.html', user_input=user_input, search_results=search_results)

@app.route('/show-item', methods=['POST'])
def save_item():

	item_asin = request.form['item_asin']
	item_title = request.form['item_title']
	item_image_url = request.form['item_image_url']
	item_price = int(request.form['item_price'])
	item_price_f = request.form['item_price_f']
	item_url = request.form['item_url']


	return render_template('set-alert.html', item_asin=item_asin, item_title=item_title, item_image_url=item_image_url, 
							item_price=item_price, item_price_f=item_price_f, item_url=item_url)

@app.route('/set-alert', methods=['POST'])
def set_alert():
	
	date_entered = datetime.utcnow()

	alert_price = int(request.form['alert_price'])
	alert_num_days = int(request.form['alert_num_days'])
	expiration_date = date_entered.replace(day=date_entered.day+alert_num_days )

	item_asin = request.form['item_asin']
	item_title = request.form['item_title']
	item_price = int(request.form['item_price'])
	item_price_f = request.form['item_price_f']
	item_url = request.form['item_url']
	
	item = Product(title=item_title, asin=item_asin, price=item_price, date_entered=date_entered)
	db.session.add(item)
	db.session.commit()

	user = User.query.filter_by(user_id=1).one()
	product = Product.query.filter_by(asin=item_asin, date_entered=date_entered).one()
	
	alert = Alert(user_id=user.user_id, product_id=product.product_id, alert_price=alert_price, expiration_date=expiration_date)
	db.session.add(alert)
	db.session.commit()
	
	return render_template('confirmation.html')

if __name__ == "__main__":
 
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()