import os
import amazonproduct

import json
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Product, Alert, UserSearch, connect_to_db, db
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

    return render_template('index.html', session=session)


@app.route('/login', methods=['POST'])
def login_user():

    user = User.query.filter_by(email=request.form['email']).first()

    if not user:
        flash('Invalid login')
        return render_template('index.html')
    else:
        if user and (user.password == request.form['password']):
            session['username'] = user.user_id
            flash('Login successful')
            return redirect('/')
        else:
            flash('Invalid password')
            return render_template('index.html')


@app.route('/register', methods=['POST'])
def register_user():

    if request.form['password'] != request.form['passwordConfirm']:
        flash('Passwords do not match')
        return redirect('/')
    else:
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        user = User(email=email, password=password, phone_number=phone)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.user_id

        flash('Registration successful')

        return redirect('/')


@app.route('/logout')
def log_out():

    session.pop('username')
    return render_template('index.html', session=session)


@app.route('/user-account')
def show_account():

    return render_template('user-account.html')


@app.route('/get-current-alerts')
def get_current_alerts():

    user = User.query.filter_by(user_id=session['username']).one()
    user_alerts = Alert.query.filter_by(user_id=session['username']).all()
    json_obj = make_alert_json(user_alerts)
    return jsonify(json_obj)


@app.route('/get-user-searches')
def get_user_searches():

    user = User.query.filter_by(user_id=session['username']).one()
    user_searches = UserSearch.query.filter_by(user_id=session['username']).all()
    json_obj = make_searches_json(user_searches)
    return jsonify(json_obj)

@app.route('/search-results', methods=['GET'])
def show_results():


    category = request.args.get('category')
    user_input = request.args.get('user_input')

    search_results = api.item_search(category, Keywords=user_input,
                                     MerchantId='Amazon',
                                     ResponseGroup='Offers, ItemAttributes, Images')

    json_string = make_json(search_results)

    user = User.query.filter_by(user_id=1).one()
    user_search = UserSearch(user_id=user.user_id,
                             category=category,
                             user_input=user_input,
                             search_results=json_string)
    db.session.add(user_search)
    db.session.commit()

    session['search_id'] = user_search.user_search_id

    return render_template('search-results.html', pages=5, session=session, user_input=user_input)


@app.route('/paginate-search/<int:page_number>', methods=['GET'])
def show_page(page_number):

    search_results = UserSearch.query.filter_by(
        user_search_id=session['search_id']).first()
    search = search_results.search_results
    search = json.loads(search)

    for items in search:
        if page_number == 1:
            search[items] = search[items][:20]
        if page_number == 2:
            search[items] = search[items][20:40]
        if page_number == 3:
            search[items] = search[items][40:60]
        if page_number == 4:
            search[items] = search[items][60:80]
        if page_number == 5:
            search[items] = search[items][80:100]

    return jsonify(search)


@app.route('/alert-data', methods=['POST'])
def alert_data():

    asin = request.form['asin']
    title = request.form['title']
    price = request.form['price']

    alert_price = int(request.form['alert_price'])
    alert_length = int(request.form['alert_length'])

    date_entered = datetime.utcnow()
    expiration_date = date_entered.replace(day=date_entered.day+alert_length)

    item = Product(asin=asin,
                   title=title,
                   price=price,
                   date_entered=date_entered)
    db.session.add(item)
    db.session.commit()

    user = User.query.filter_by(user_id=1).one()

    product = Product.query.filter_by(asin=asin,
                                      date_entered=date_entered).one()
    
    alert = Alert(user_id=user.user_id,
                  product_id=product.product_id,
                  alert_price=alert_price,
                  expiration_date=expiration_date,
                  status=1)

    db.session.add(alert)
    db.session.commit()

    return "ok"

@app.route('/delete-alert', methods=['POST'])
def delete_item():

    alert_id = int(request.form['alert_id'])
    alert = Alert.query.filter_by(alert_id=alert_id).one()
    
    print alert.status
    alert.status = 0
    print alert.status
    
    return "ok"


# used in @app.route('/search-results')
def make_json(search_results):

    search_results_list = []
    for item in search_results:
        search_results_list.append({"ASIN": str(item.ASIN),
                                    "Title": str(item.ItemAttributes.Title),
                                    "Image_URL": str(item.ImageSets.ImageSet.MediumImage.URL),
                                    "Price_f": str(item.Offers.Offer.OfferListing.Price.FormattedPrice),
                                    "Price": str(item.Offers.Offer.OfferListing.Price.Amount),
                                    "Link": str(item.ItemLinks.ItemLink.URL)})
    search_results_dict = {}
    search_results_dict["items"] = search_results_list
    json_string = json.dumps(search_results_dict)
    return json_string


def make_alert_json(alerts):

    current_alerts = []
    for alert in alerts:
        current_alerts.append({"Alert_id": alert.alert_id,
                               "Title": alert.product.title,
                               "Alert_price": alert.alert_price,
                               "Expiration_date": str(alert.expiration_date)})
    current_alerts_obj = {}
    current_alerts_obj["alerts"] = current_alerts
    json_obj = current_alerts_obj
    return json_obj

def make_searches_json(searches):
    
    user_searches = []
    for search in searches:
        user_searches.append({"Category": search.category,
                              "User_input": search.user_input})
    user_searches_obj = {}
    user_searches_obj["searches"] = user_searches
    json_obj = user_searches_obj
    return json_obj


if __name__ == "__main__":

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()
