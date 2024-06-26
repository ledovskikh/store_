import os
import random

from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from data.basket import Basket
from data.products import Product
from data.users import User
from forms.loginform import LoginForm
from forms.product import ProductsForm
from forms.user import RegisterForm
from flask_restful import reqparse, abort, Api, Resource

# from forms import db_session, news_api

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JSON_AS_ASCII'] = False

def main():
    db_session.global_init("db/shop.db")
    api.add_resource(NewsListResource, '/api/v2/product')
    # app.register_blueprint(news_api.blueprint)
    app.run(debug=False)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        products = db_sess.query(Product).filter(
            (Product.user == current_user) | (Product.is_private != True))
    else:
        products = db_sess.query(Product).filter(Product.is_private != True)

    return render_template("index.html", products=products, title='Store')


@app.route("/shops")
def shops():
    db_sess = db_session.create_session()
    shops = db_sess.query(User).filter(User != current_user)

    return render_template("shops.html", shops=shops, title='Магазины')


@app.route("/my_products")
@login_required
def my_products():
    db_sess = db_session.create_session()
    my_products = db_sess.query(Product).filter(Product.user == current_user)

    return render_template("index.html", products=my_products, title='Мои товары')


@app.route("/basket")
@login_required
def basket():
    db_sess = db_session.create_session()
    basket_products = db_sess.query(Basket).filter(Basket.user == current_user)
    all_products = db_sess.query(Product)

    return render_template("basket.html", basket_products=basket_products, all_products=all_products,
                           title='Корзина')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/products', methods=['GET', 'POST'])
@login_required
def add_products():
    form = ProductsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Product()
        f = form.pic.data
        filename = secure_filename(f.filename)
        mimetype = f.mimetype
        if not filename or not mimetype:
            return 'Bad upload!', 400

        print(product.id)
        file_type = '.' + filename.split('.')[1]
        while True:
            try:
                filename = str(random.randint(1, 9999999))
                filename += file_type
                product.name = filename
                with open(f"static/img/products_img/{filename}", "wb") as img:
                    img.write(f.read())
                break
            except:
                pass

        product.mimetype = mimetype
        product.title = form.title.data
        product.content = form.content.data
        product.is_private = form.is_private.data
        current_user.products.append(product)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('products.html', title='Добавление товара',
                           form=form)


@app.route('/<int:id>', methods=['GET', 'POST'])
def product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()

    return render_template("product.html", product=product, title=product.title)


@app.route('/products_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = ProductsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        products = db_sess.query(Product).filter(Product.id == id,
                                                 Product.user == current_user
                                                 ).first()
        if products:
            form.title.data = products.title
            form.content.data = products.content
            form.is_private.data = products.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        products = db_sess.query(Product).filter(Product.id == id,
                                                 Product.user == current_user
                                                 ).first()
        if products:
            products.title = form.title.data
            products.content = form.content.data
            products.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('products.html',
                           title='Изменение параметров товара',
                           form=form
                           )


@app.route('/product_add_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def product_add_basket(id):
    db_sess = db_session.create_session()
    products = Basket()
    products.product_id = id
    current_user.basket.append(products)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect('/')


@app.route('/products_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(Product.id == id,
                                             Product.user == current_user
                                             ).first()

    if products:
        os.remove(f"static/img/products_img/{products.name}")
        db_sess.delete(products)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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
        products = session.query(Product).all()
        return jsonify({'products': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
        )
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})


if __name__ == '__main__':
    main()
