from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datas import users_data, orders_data, offers_data
from datetime import datetime
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """Модель для пользователей"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(20))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    """Модель для заказов"""
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    """Модель для предложений"""
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

    for user in users_data:
        new_user = User(**user)
        db.session.add(new_user)
        db.session.commit()

    for order in orders_data:
        order['start_date'] = datetime.strptime(order['start_date'], '%m/%d/%Y').date()
        order['end_date'] = datetime.strptime(order['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order)
        db.session.add(new_order)
        db.session.commit()

    for offer in offers_data:
        new_offer = Offer(**offer)
        db.session.add(new_offer)
        db.session.commit()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        users = User.query.all()
        result = [usr.to_dict() for usr in users]
        return json.dumps(result)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()


@app.route('/users/<uid>')
def get_user(uid):
    one_user = User.query.get(uid)
    return one_user.to_dict()


@app.route('/orders')
def get_orders():
    orders = Order.query.all()
    result = [ordr.to_dict() for ordr in orders]
    return result


@app.route('/orders/<oid>')
def get_order(oid):
    one_order = Order.query.get(oid)
    return one_order.to_dict()


@app.route('/offers')
def get_offers():
    offers = Offer.query.all()
    result = [ofr.to_dict() for ofr in offers]
    return result


@app.route('/offers/<oid>')
def get_offer(oid):
    one_offer = Offer.query.get(oid)
    return one_offer.to_dict()


if __name__ == '__main__':
    app.run()
