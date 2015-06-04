from model import Alert
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URI = 'sqlite:///priceping.db'
engine = create_engine(DB_URI, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


def check_alerts():
    """checks if alerts have expired, if expired sets active to 0"""

    active_alerts = session.query(Alert).filter_by(active=1).all()
    current_date = datetime.utcnow()

    for a in active_alerts:
        if a.expiration_date < current_date:
            a.active = 0

            session.add(a)
            session.flush()

    session.commit()


if __name__ == '__main__':
    check_alerts()
