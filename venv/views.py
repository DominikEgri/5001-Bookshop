from flask import Flask, render_template, url_for, request, redirect, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = "alma"
app.permanent_session_lifetime = timedelta(days = 3)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialize the database
db = SQLAlchemy(app)

#Create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.id

    
@app.route('/')
def home_page():
    items = [
        {"id" : 1, "name" : "phone", "price" : 500},
        {"id" : 2, "name" : "laptop", "price" : 900},
        {"id" : 3, "name" : "keyboard", "price" : 150}
    ]
    
    return render_template('home.html', title="Home",items=items)


@app.route('/view')
def view_page():
    return render_template('view.html', values=users.query.all())


@app.route('/login', methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()
            
        flash("You have been logged in", "info")
        return redirect(url_for("user_page"))
    
    else:
        if "user" in session:
            return redirect(url_for('user_page'))
        
        return render_template('login.html')
    
    
@app.route('/user', methods=["POST", "GET"])
def user_page():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved.", "info")
        else:
            if "email" in session:
                email = session["email"]
                
        return render_template('user.html', email=email)
    else:
        flash("You are not logged in.")
        redirect(url_for('login_page'))
        

@app.route('/logout')
def logout_page():
    flash("You have been logged out", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for('login_page'))

db.create_all()