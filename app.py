from flask import Flask, redirect, request, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, bcrypt, Feedback
from forms import AddUserForm, LoginForm, FeedbackForm
import os.path

app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "32m54hwcon49s1kl6"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

with app.app_context():
    connect_db(app)
    db.create_all()

debug = DebugToolbarExtension(app)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))
# credit: MarredCheese at https://stackoverflow.com/questions/41144565/flask-does-not-see-change-in-js-file
# is used to automatically update static files without having to hard refresh the browser for every change :D


@app.route("/")
def root():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = AddUserForm()
    if form.validate_on_submit():
        first = form.first_name.data
        last = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        user = User.register(username=username, password=password, email=email, first_name=first, last_name=last)
        db.session.add(user)
        db.session.commit()
        session["username"] = username
        return redirect(f"/users/{username}")
    else:
        return render_template("add_user.html", form=form, last_updated=dir_last_updated("static"))
    
@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.get(username)
        if (bcrypt.check_password_hash(user.password, password)):
            session["username"] = username
            return redirect(f"/users/{username}")
        else:
            return render_template("login.html", form=form, last_updated=dir_last_updated("static"))
    else:
        return render_template("login.html", form=form, last_updated=dir_last_updated("static"))
    
@app.route("/users/<username>")
def user_page(username):
    if (session.get("username", None) == username):
        user = User.query.get(username)
        return render_template("user.html", user=user, last_updated=dir_last_updated("static"))
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    form = FeedbackForm()
    if (session.get("username", None) == username):
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            feedback = Feedback(username=username, title=title, content=content)
            db.session.add(feedback)
            db.session.commit()
            return redirect(f"/users/{username}")
        else:
            return render_template("feedback.html", form=form, last_updated=dir_last_updated("static"))
    else:
        return redirect("/")
    
@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback(id):
    feedback = Feedback.query.get(id)
    form = FeedbackForm(obj=feedback)
    if (session.get("username", None) == feedback.username):
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            feedback.title = title
            feedback.content = content
            db.session.add(feedback)
            db.session.commit()
            return redirect(f"/users/{feedback.username}")
        else:
            return render_template("feedback.html", form=form, last_updated=dir_last_updated("static"))
    else:
        return redirect("/")
    
@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
    feedback = Feedback.query.get(id)
    if (session.get("username", None) == feedback.username):
        Feedback.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    else:
        return redirect("/")
    


