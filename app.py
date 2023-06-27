from flask import Flask, render_template, flash, redirect, session, url_for, logging, request
#rom data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import mysql.connector
from functools import wraps


app = Flask(__name__)
#configure db
connection = mysql.connector.connect(
            host = "localhost",
            user = "philip",
            password = "1234",
            database = "myflaskapp"
            );

cursor = connection.cursor()

#rticles = Articles()

@app.route("/")
def index():
    return render_template("home.html") 

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/jobs")
def jobs():
    cur = connection.cursor()
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    return render_template("jobs.html", jobs=jobs)

@app.route("/apply/<int:job-id>/")
def apply(job_id):
    #create connection
    cur = connection.cursor()
    #execute
    cur.execute("SELECT * FROM jobs WHERE id=%s",(job_id,))
    job = cur.fetchone()
    if job:
        return render_template("apply.html", job=job)
    else:
        return "Job notfound"
    if request.method == "POST":
        #handle application submission here
        return "Application is successful"

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
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(str(form.password.data))

        #create cursor
        cur = connection.cursor()
        cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)", (name, username, email, password))

        #commit to db
        connection.commit()

        #close connection
        cur.close()
        flash("You are now logged in and can register", "success")
        return redirect(url_for("index"))
    return render_template("register.html",form=form)

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        #get form feld
        username = request.form["username"]
        password_candidate = request.form["password"]

        #create cursor
        cur = connection.cursor(buffered=True)

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        data = cur.fetchone()
        if data is not None:
            #get hashed password
            password = data[4]

            #compare password
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "invalid login"
                return render_template("login.html", error=error)
            #close connection
            cur.close()
        else:
            error = "username not found"
            return render_template("login.html", error=error)
    return render_template("login.html")


#check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("unauthorised, please login", "danger")
            return redirect(url_for("login"))
    return wrap


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@is_logged_in
def dashboard():
    #create cursor
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    if not jobs:
        msg = "no jobs found"
        return render_template("dashboard.html", msg=msg)
    else:
        return render_template("dashboard.html", jobs=jobs)

#job form class
class JobForm(Form):
        title = StringField("Title",[validators.Length(min=4, max=200)])
        description = TextAreaField("Description", [validators.Length(min=30)])
        location = StringField("Location", [validators.Length(min=2)])
        salary = StringField("Salary", [validators.Length(min=2)])


@app.route("/add_job", methods=["GET", "POST"])
@is_logged_in
def add_job():
    form = JobForm(request.form)
    if request.method == "POST" and form.validate():

        title = form.title.data
        description = form.description.data
        location = form.location.data
        salary = form.salary.data
    
        #create cursor
        cur = connection.cursor()

        #execute
        cur.execute("INSERT INTO jobs(title, description, location, salary) VALUES(%s, %s, %s, %s)", (title, description, location, salary))

        #commit to db
        connection.commit()

        #close connection
        cur.close()

        flash("job created", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_job.html", form=form)


@app.route("/edit_job/<string:id>", methods=["GET", "POST"])
@is_logged_in
def edit_job(id):
    #create cursor
    cur = connection.cursor()

    #execute
    cur.execute("SELECT * FROM jobs WHERE id = %s", (id,))
    job = cur.fetchone()

    #get form
    form = JobForm(request.form)

    #populate the field
    form.title.data = job[1]
    form.description.data = job[2]
    form.location.data = job[3]
    form.salary.data = job[4]

    if request.method == "POST" and form.validate():

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        salary = request.form["salary"]
        
        #create cursor
                                                
        cur = connection.cursor()

        #execute
        cur.execute("UPDATE articles SET title=%s, description=%s, location=%s, salary=%s WHERE id=%s",(title, description, location, salary, id))

        #commit to db
        connection.commit()

        #close connection
        cur.close()

        flash("job updated", "success")
        return redirect(url_for("dashboard"))
    return render_template("edit_job.html", form=form)

@app.route("/delete_job/<string:id>", methods=["POST"])
@is_logged_in
def delete_job(id):
    #create cursor
    cur = connection.cursor()
    #execute
    cur.execute("DELETE FROM jobs WHERE id=%s",(id,))
    connection.commit()
    #close connection
    cur.close()
    flash("Job deleted", "success")
    return redirect(url_for("dashboard"))




if __name__ == "__main__":
    app.secret_key="secret1234"
    app.run(debug=True)


