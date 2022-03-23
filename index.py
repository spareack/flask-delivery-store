from flask import Flask, render_template, send_from_directory, redirect, request, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_frozen import Freezer

import json
import traceback
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_PASS"] = "zs9XYCbTPKvux46UJckflw"
freezer = Freezer(app)
Session(app)

db = SQLAlchemy(app)


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    food_list = db.Column(db.String)
    filename = db.Column(db.String, default="-1.png")


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    weight = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, default="-1.png")


@app.route("/")
def hello_world():
    all_categories = db.session.query(Categories).all()
    return render_template("index.html", categories=all_categories)


@app.route("/category/<int:category_id>/")
def show_category(category_id):
    category = db.session.query(Categories).filter_by(id=category_id).first_or_404()

    foods_ids = json.loads(category.food_list)
    food_list = db.session.query(Food).filter(Food.id.in_(foods_ids)).all()

    return render_template("category.html", food_list=food_list, category_name=category.name)


@freezer.register_generator
def show_category():
    all_categories = db.session.query(Categories).all()
    for category in all_categories:
        yield {'category_id': category.id}


@app.route("/meal/<int:food_id>/")
def show_meal(food_id):
    food = db.session.query(Food).filter_by(id=food_id).first_or_404()
    return render_template("meal.html", food=food)


@freezer.register_generator
def show_meal():
    all_food = db.session.query(Food).all()
    for food in all_food:
        yield {'food_id': food.id}


@app.route("/sales/")
def open_sales():
    # return render_template("sales.html")
    return render_template("sales.html")


@app.route("/admin/", methods=['GET'])
def open_admin():
    if request.method == 'GET':
        if "auth" in session and session['auth'] == app.config["SECRET_PASS"]:
            base = list()
            all_categories = db.session.query(Categories).all()
            for category in all_categories:
                foods_ids = json.loads(category.food_list)
                food_list = db.session.query(Food).filter(Food.id.in_(foods_ids)).all()
                base.append([category.name, food_list])

            return render_template("admin.html")
        else:
            return render_template("admin_auth.html")


@app.route("/auth_admin/", methods=['GET', 'POST'])
def auth_admin():

    if request.method == 'POST':
        return "asd"

        password = request.form.get("pass")
        return "asd"

        session['auth'] = password
        return "asd"

        return redirect("/admin/")

    return "asdfgh"


@app.route("/admin_out")
def admin_out():
    session["name"] = None
    return redirect('/admin/')


@app.route("/save_changes", methods=["POST"])
def save_changes():
    if request.method == 'POST':

        try:
            foods_ids = db.session.query(Food.id).all()

            categories = db.session.query(Categories).all()
            for category in categories:

                category_file = request.files["category_" + str(category.id - 1)]

                if category_file and category_file.filename != '' and '.' in category_file.filename:
                    name = secure_filename(category_file.filename).split(".")
                    if name[1].lower() in ['jpg', 'jpeg', 'png']:
                        endgame = str(category.id-1) + "." + name[1]

                        path = os.path.join(os.path.join(os.path.abspath(os.getcwd()), "mysite/static/media/category", endgame))
                        if os.path.isfile(path):
                            os.remove(path)

                        category_file.save(path)
                        category.filename = endgame

            for index in foods_ids:
                food = db.session.query(Food).filter_by(id=index[0]).first_or_404()

                name_temp = request.form.get("name_" + str(index[0]))
                price_temp = request.form.get("price_" + str(index[0]))
                weight_temp = request.form.get("weight_" + str(index[0]))
                description_temp = request.form.get("description_" + str(index[0]))

                file = request.files["file_" + str(index[0])]

                if file and file.filename != '' and '.' in file.filename:
                    name = secure_filename(file.filename).split(".")
                    if name[1].lower() in ['jpg', 'jpeg', 'png']:
                        endgame = str(index[0]-1) + "." + name[1]

                        path = os.path.join(os.path.join(os.path.abspath(os.getcwd()), "mysite/static/media/food", endgame))
                        if os.path.isfile(path):
                            os.remove(path)
                        file.save(path)

                        food.filename = endgame

                if food.name != name_temp or food.price != price_temp or food.weight != weight_temp \
                        or food.description != description_temp:

                    if food.name != name_temp:
                        food.name = name_temp

                    if food.price != price_temp:
                        food.price = price_temp

                    if food.weight != weight_temp:
                        food.weight = weight_temp

                    if food.description != description_temp:
                        food.description = description_temp

            db.session.commit()

        except Exception as e:
            print(str(e))
            print(traceback.format_exc())

        return redirect("/admin")
    else:
        return 1


@app.route("/favicon.ico")
def get_favicon():
    return send_from_directory("static/media", 'favicon.ico')


if __name__ == '__main__':
    # freezer.freeze()
    freezer.run(debug=True)
    # app.run()
