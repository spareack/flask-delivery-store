from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    food_list = db.Column(db.String)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)


@app.route("/")
def hello_world():
    all_categories = db.session.query(Categories).all()
    return render_template("index.html", categories=all_categories)


@app.route("/category/<int:category_id>")
def show_category(category_id):
    category = db.session.query(Categories).filter_by(id=category_id).first_or_404()

    foods_ids = json.loads(category.food_list)
    food_list = db.session.query(Food).filter(Food.id.in_(foods_ids)).all()

    return render_template("category.html", food_list=food_list, category_name=category.name)


@app.route("/meal/<int:food_id>")
def show_meal(food_id):
    food_id += 1

    food = db.session.query(Food).filter_by(id=food_id).first_or_404()
    return render_template("meal.html", food=food)


if __name__ == '__main__':
    app.run()