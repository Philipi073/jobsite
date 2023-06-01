from flask import Flask, render_template, flash, redirect, session, url_for, logging, request
from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
app = Flask(__name__)
Articles = Articles()

@app.route("/")
def index():
    return render_template("home.html") 

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    return render_template("articles.html", articles=Articles)

@app.route("/article/<int:id>")
def article(id):
    return render_template("article.html", id=id)

class RegisterForm(Form):
    name = StringField("Name",[validators.Length(min=4, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("email", [validators.Length(min=6, max=25)])
    password = PasswordField("Password", [validators.DataRequired(), validators.EqualTo("confirm", message="password do not match")])
    confirm = PasswordField("Confirm password")

@app.route("/register", methods= ["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        return render_template("register.html")
    return render_template("register.html",form=form)


if __name__ == "__main__":
    app.run(debug=True)


