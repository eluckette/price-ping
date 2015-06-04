import os
import amazonproduct
import json
from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Product, Alert, UserSearch, connect_to_db, db
from datetime import datetime
import random

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

    if not session['username']:
        session['username'] = 1

    return render_template('index.html')


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
        flash('User already exists,' +
              'please sign-in or register with a new e-mail')
        return render_template('index.html')

    else:
        user = User(email=request.form['email'],
                    password=request.form['password'],
                    phone_number=request.form['phone_number'])
        db.session.add(user)
        db.session.commit()

        session['username'] = user.user_id
        flash('Registration successful')

        return render_template('index.html')


@app.route('/logout')
def log_out():

    session['username'] = 1
    return render_template('index.html')


@app.route('/get-other-alerts')
def get_popular_alerts():

    list_search_id = random.sample(range(1, Alert.query.count()), 5)
    other_searches = [Alert.query.filter_by(alert_id=x).one()
                      for x in list_search_id]
    json_obj = make_alert_home_json(other_searches)
    return jsonify(json_obj)


@app.route('/user-account')
def show_account():

    return render_template('user-account.html')


@app.route('/get-current-alerts')
def get_current_alerts():

    user_alerts = Alert.query.filter_by(user_id=session['username']) \
                  .filter_by(alert_set=1).all()
    json_obj = make_alert_json(user_alerts)
    return jsonify(json_obj)


@app.route('/get-recently-viewed')
def get_recently_viewed():

    user_searches = Alert.query.filter_by(user_id=session['username'], alert_set=0)\
                    .order_by(Alert.product_id.desc()).limit(3).all()
    json_obj = make_alert_json(user_searches)
    return jsonify(json_obj)


@app.route('/get-random-search')
def get_random_search():

    random_search = UserSearch.query.filter_by(user_search_id=random.randint(0, UserSearch.quert.count())).one()
    return (random_search.category, random_search.user_input)


@app.route('/search-results', methods=['GET', 'POST'])
def show_results():

    user = assign_user()

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

    user_search = UserSearch(user_id=user.user_id,
                             category=category,
                             user_input=user_input,
                             search_results=json_string)
    db.session.add(user_search)
    db.session.commit()
    
    session['search_id'] = user_search.user_search_id

    return render_template('search-results.html', pages=5,
                           user_input=user_input)


@app.route('/paginate-search/<int:page_number>', methods=['GET'])
def show_page(page_number):

    search_results = UserSearch.query\
                    .filter_by(user_search_id=session['search_id']).first()
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

    user = assign_user()
    item = unpack_args()
    image_url = request.form['image_url']
    date_entered = datetime.utcnow()

    looking_for = Product.query.filter_by(asin=item['asin'], user_id=user.user_id).first()

    if not looking_for:
        add_item = Product(user_id=user.user_id,
                           asin=item['asin'],
                           title=item['title'],
                           price=item['price'],
                           image_url=image_url,
                           date_entered=date_entered)

        db.session.add(add_item)
        db.session.flush()

    product = Product.query.filter_by(asin=item['asin'], user_id=user.user_id).first()

    alert = Alert(user_id=user.user_id,
                  product_id=product.product_id,
                  alert_set=0, active=0)

    db.session.add(alert)
    db.session.commit()
    return "ok"


@app.route('/update-alert', methods=['POST'])
def update_alert():

    asin, title = request.form['asin'], request.form['title']
    alert_length = int(request.form['alert_length'])

    date_entered = datetime.utcnow()
    expiration_date = date_entered.replace(day=date_entered.day+alert_length)

    user = User.query.filter_by(user_id=session['username']).one()
    product = Product.query.filter_by(asin=asin,
                                      title=title).first()

    alert = Alert.query.filter_by(user_id=user.user_id,
                                  product_id=product.product_id,
                                  alert_set=0).first()

    alert.alert_price = float(request.form['alert_price'])
    alert.expiration_date = expiration_date
    alert.alert_set, alert.active = 1, 1

    db.session.add(alert)
    db.session.commit()
    return "ok"


@app.route('/delete-alert', methods=['POST'])
def delete_item():

    alert = Alert.query.filter_by(alert_id=int(request.form['alert_id'])).one()
    alert.alert_set = 0
    db.session.add(alert)
    db.session.commit()
    return "ok"


def assign_user():

    if session['username'] == 1:
        user = User.query.filter_by(user_id=1).one()
    else:
        user = User.query.filter_by(user_id=session['username']).one()
    return user


def unpack_args():

    item_attr = {'asin': request.form['asin'],
                 'title': request.form['title'],
                 'price': request.form['price']}

    return item_attr


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

def make_alert_home_json(alerts):

    home_page_alerts = []
    for alert in alerts:

        home_page_alerts.append({"ASIN": alert.product.asin,
                                 "Image_URL": alert.product.image_url,
                                 "Title": alert.product.title,
                                 "Price": alert.product.price})
    home_page_alerts_obj = {}
    home_page_alerts_obj["alerts"] = home_page_alerts
    json_obj = home_page_alerts_obj
    return json_obj

def make_alert_json(alerts):

    current_alerts = []
    for alert in alerts:

        if alert.expiration_date:
            expiration_date = unicode(alert.expiration_date.month)+"/"+unicode(alert.expiration_date.day)+"/"+unicode(alert.expiration_date.year)
        else:
            expiration_date = " "

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
