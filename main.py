from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import os


### CREATE FLASK SERVER ###
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

### CREATE DB ###
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

### CREATE LOGIN MANAGER ###
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 


### CREATE RELATIONAL TABLES ###
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    todo_items = relationship('ToDo', back_populates='person')

class ToDo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    deadline = db.Column(db.String, nullable=False)
    details = db.Column(db.String(200), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    person = relationship('User', back_populates='todo_items')

# db.create_all()

### CREATE ROUTE ###
@app.route("/")
def home():
    if current_user.is_authenticated:
        username = current_user.username
        return render_template("home.html", logged_in=current_user.is_authenticated, name=username)

    return render_template("home.html", logged_in=current_user.is_authenticated)

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":

        # CHECK IF THE USER ALREADY EXISTS
        if User.query.filter_by(username=request.form.get('username')).first():
            flash("You've already signed up with that username, log in instead!")
            return redirect(url_for('login'))

        # SECURE USER'S PASSWORD BY HASHING AND SALTING
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        # SAVE NEW USER WITH SECURED PASSWORD
        new_user = User(
            username=request.form.get('username'),
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("my_page"))

    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # CHECK IF THE USERNAME EXIST AND THE PASSWORD IS CORRECT
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("That username does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('my_page'))

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/my_page")
@login_required
def my_page():
    all_todos = ToDo.query.filter_by(person_id=current_user.id)
    db.session.commit()

    # SORT TO DO ITEMS BY DEADLINE
    items = []
    for todo in all_todos:
        item = {
            "id": todo.id,
            "title": todo.title,
            "deadline": todo.deadline,
            "details": todo.details
         }
        items.append(item)
    items.sort(key=lambda date:date["deadline"])

    return render_template("my_page.html", all_todos=items, logged_in=current_user.is_authenticated)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    # GET DATA FROM ADD FORM AND ADD DATA
    if request.method == 'POST':
        new_item = ToDo(
            title=request.form["title"],
            deadline=request.form["deadline"],
            details=request.form["details"],
            person_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("my_page"))

    return render_template("form.html")

@app.route("/edit", methods=["GET","POST"])
@login_required
def edit():
    # GET PREVIOUS DATA TO EDIT
    todo_id = request.args.get('id')
    todo_selected = ToDo.query.get(todo_id)

    # GET DATA FROM FORM AND EDIT A RECORD BY ID
    if request.method == 'POST':
        todo_id = request.args.get('id')
        todo_to_update = ToDo.query.get(todo_id)
        todo_to_update.title = request.form["title"]
        todo_to_update.deadline = request.form["deadline"]
        todo_to_update.details = request.form["details"]

        db.session.commit()
        return redirect(url_for('my_page'))

    return render_template("form.html", todo_selected=todo_selected)


@app.route("/delete")
@login_required
def delete():
    todo_id = request.args.get('id')

    # DELETE A RECORD BY ID
    todo_to_delete = ToDo.query.get(todo_id)
    db.session.delete(todo_to_delete)
    db.session.commit()
    return redirect(url_for('my_page'))

if __name__ == '__main__':
    app.run(debug=True)
