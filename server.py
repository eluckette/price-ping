import os
import amazonproduct
import json
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Product, Alert, UserSearch, connect_to_db, db
from datetime import datetime
import random
import codecs

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

    session['username'] = 1
    return render_template('index.html', session=session)


@app.route('/login', methods=['POST'])
def login_user():

    user = User.query.filter_by(email=request.form['email']).first()

    if not user:
        flash('Invalid e-mail')
        return render_template('index.html')
    else:
        if user and (user.password == request.form['password']):
            session['username'] = user.user_id
            flash('Login successful')
            return render_template('index.html')
        else:
            flash('Invalid password')
            return render_template('index.html')


@app.route('/register', methods=['POST'])
def register_user():

    if request.form['password'] != request.form['password_check']:
        flash('Passwords do not match')
        return render_template('index.html')
    
    if User.query.filter_by(email=request.form['email']).first():
        flash('User already exists, please sign-in or register with a new e-mail')
        return render_template('index.html')
    
    else:
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone_number']

        user = User(email=email, password=password, phone_number=phone)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.user_id
        flash('Registration successful')

        return render_template('index.html')


@app.route('/logout')
def log_out():

    session['username'] = 1
    return render_template('index.html', session=session)

@app.route('/get-other-alerts')
def get_popular_alerts():

    list_search_id = [random.randint(0, UserSearch.query.count()) for x in range(5)]
    other_searches = [Alert.query.filter_by(alert_id=x).first() for x in list_search_id]
    json_obj = make_alert_json(other_searches)
    return jsonify(json_obj)


@app.route('/user-account')
def show_account():

    return render_template('user-account.html')


@app.route('/get-current-alerts')
def get_current_alerts():

    user_alerts = Alert.query.filter_by(user_id=session['username']).filter_by(status=1).all()
    json_obj = make_alert_json(user_alerts)
    return jsonify(json_obj)


@app.route('/get-user-searches')
def get_user_searches():

    user_searches = Alert.query.filter_by(user_id=session['username'], status=0).all()
    json_obj = make_alert_json(user_searches)
    return jsonify(json_obj)

@app.route('/get-random-search')
def get_random_search():

    random_id = random.randint(0, UserSearch.quert.count())
    random_search = UserSearch.query.filter_by(user_search_id=random_id).one()
    return (random_search.category, random_search.user_input);

@app.route('/search-results', methods=['GET', 'POST'])
def show_results():

    if session['username'] == 1:
        user = User.query.filter_by(user_id=1).one()

    else: 
        user = UserSearch.query.filter_by(user_id=session['username'].one())

    if request.method == 'GET':
        category = request.args.get('category')
        user_input = request.args.get('user_input')
    else:
        category = request.form['category']
        user_input = request.form['user_input']

    search_results = api.item_search(category, Keywords=user_input,
                                     MerchantId='Amazon',
                                     ResponseGroup='Offers, ItemAttributes, Images')


    json_string = make_json(search_results)

    # user = User.query.filter_by(user_id=session['username']).one()
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

    search_results = UserSearch.query.filter_by(user_search_id=session['search_id']).first()
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


@app.route('/set-alert', methods=['POST'])
def set_alert():

    asin = request.form['asin']
    title = request.form['title']
    price = request.form['price']
    image_url = request.form['image_url']
    alert_price = 0
    alert_length = datetime.utcnow()
    date_entered = datetime.utcnow()

    looking_for = Product.query.filter_by(asin=asin, user_id=session['username']).first()

    if looking_for == None:
        item = Product(user_id=session['username'],
                       asin=asin,
                       title=title,
                       price=price,
                       image_url=image_url,
                       date_entered=date_entered)

        db.session.add(item)
        db.session.commit() 

    user = User.query.filter_by(user_id=session['username']).one()
    product = Product.query.filter_by(asin=asin, user_id=session['username']).first()

    alert = Alert(user_id=user.user_id, 
                  product_id=product.product_id,
                  status=0)

    db.session.add(alert)
    db.session.commit()


@app.route('/update-alert', methods=['POST'])
def update_alert():

    asin = request.form['asin']
    title = request.form['title']
    alert_price = float(request.form['alert_price'])
    alert_length = int(request.form['alert_length'])

    date_entered = datetime.utcnow()
    expiration_date = date_entered.replace(day=date_entered.day+alert_length)

    user = User.query.filter_by(user_id=session['username']).one()
    product = Product.query.filter_by(asin=asin,
                                      title=title).one()
    
    alert = Alert.query.filter_by(user_id=user.user_id,
                                  product_id=product.product_id,
                                  status=0).first()

    alert.alert_price = alert_price
    alert.expiration_date = expiration_date
    alert.status = 1

    db.session.add(alert)
    db.session.commit()


@app.route('/delete-alert', methods=['POST'])
def delete_item():

    alert_id = int(request.form['alert_id'])
    alert = Alert.query.filter_by(alert_id=alert_id).one()    
    alert.status = 0

    db.session.add(alert)
    db.session.commit()


def make_json(search_results):

    search_results_list = []
    for item in search_results:
        
        search_results_list.append({"ASIN": unicode(item.ASIN),
                                    "Title": unicode(item.ItemAttributes.Title),
                                    "Image_URL": unicode(item.ImageSets.ImageSet.MediumImage.URL),
                                    "Price_f": unicode(item.Offers.Offer.OfferListing.Price.FormattedPrice),
                                    "Price": unicode(item.Offers.Offer.OfferListing.Price.Amount),
                                    "Link": unicode(item.ItemLinks.ItemLink.URL)})
    search_results_dict = {}
    search_results_dict["items"] = search_results_list
    json_string = json.dumps(search_results_dict)
    return json_string


def make_alert_json(alerts):

    current_alerts = []
    for alert in alerts:

        if alert.expiration_date == None:
            expiration_date = "";
        else:
            expiration_date = unicode(alert.expiration_date.month)+"/"+unicode(alert.expiration_date.day)+"/"+unicode(alert.expiration_date.year)

        current_alerts.append({"Alert_id": alert.alert_id,
                               "Title": alert.product.title,
                               "Alert_price": alert.alert_price,
                               "Expiration_date": expiration_date,
                               "Image_URL": alert.product.image_url})
    current_alerts_obj = {}
    current_alerts_obj["alerts"] = current_alerts
    json_obj = current_alerts_obj
    return json_obj


if __name__ == "__main__":

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)

    app.run()
