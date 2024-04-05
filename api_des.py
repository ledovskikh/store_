from flask_restful import reqparse, abort, Api, Resource
from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data import db_session
from data.products import Product


def abort_if_news_not_found(id):
    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(Product.id == id,
                                             Product.user == current_user
                                             ).first()

    news = session.query(Product).get()
    if not news:
        abort(404, message=f"Products {Product.id} not found")


class NewsResource(Resource):
    def get(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(Product).get(id)
        return jsonify({'product': product.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(Product).get(id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(Product).all()
        return jsonify({'products': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in product]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = Product(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
        )
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
