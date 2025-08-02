import logging

from flask import render_template

from app import app

logger = logging.getLogger("terrahacks-backend")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list/")
def posts():
    return render_template("list.html")


@app.route("/view/<user_id>/")
def view(user_id):
    return render_template("view.html")

