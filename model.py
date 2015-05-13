from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)


class Product(db.Model):

    __tablename__ = "products"

    product_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date_entered = db.Column(db.DateTime, nullable=True)

class Alert(db.Model):

	__tablename__ = "alerts"

	alert_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
	alert_price = db.Column(db.Float(10), nullable=False)
	expiration_date = db.Column(db.DateTime, nullable=False)

def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hbproj.db'
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."