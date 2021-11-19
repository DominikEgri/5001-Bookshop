from flask import Flask, render_template, url_for, request, redirect, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3


app = Flask(__name__)
app.secret_key = "alma"
app.permanent_session_lifetime = timedelta(days = 3)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialize the database
db = SQLAlchemy(app)



    
@app.route('/')
def home_page():
    items = [
        {"id" : 1, "name" : "phone", "price" : 500},
        {"id" : 2, "name" : "laptop", "price" : 900},
        {"id" : 3, "name" : "keyboard", "price" : 150}
    ]
    
    return render_template('home.html', title="Home",items=items)



@app.route('/login', methods=["POST", "GET"])
def login_page():
    if "username" in session:
            return redirect(url_for('user_page'))
        
    elif request.method == "POST":
        session.permanent = True
        username = request.form["nm"]
        password = request.form["ps"]
        with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                query = "SELECT name, password FROM Users WHERE name = '"+username+"'  AND password = '"+password+"'"
                cur.execute(query)
                users = cur.fetchall()
                for user in users:
                    if(username == user[0] and password == user[1]):
                        session["username"] = username
                        flash("You have been logged in", "info")
                        redirect(url_for('user_page'))
                    else:
                        return render_template('login.html', text="Unsuccessful login")   
    
    
    return render_template('login.html', text="im heree.")
    
    
@app.route('/register', methods=["POST", "GET"])
def register_page():
    if request.method == "POST":
        try:
            username = request.form["name"]
            password = request.form["password"]
            
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                
                cur.execute("INSERT INTO Users (name, password) VALUES (?, ?)",(username, password))
                
                con.commit()
                con.close()
                session.permanent = True
                user = request.form["name"]
                session["username"] = user
                flash("You have been registered!", "info")
                return redirect(url_for('user_page'))
        except:
            return redirect(url_for('register_page'))
            con.close()
    return render_template('register.html')
    
@app.route('/user', methods=["POST", "GET"])
def user_page():
    if "username" in session:
        return render_template('user.html', text = "You are in!")
    else:
        flash("You are not logged in.")
        redirect(url_for('login_page'))
        

@app.route('/logout')
def logout_page():
    flash("You have been logged out", "info")
    session.pop("username", None)
    return redirect(url_for('login_page'))


@app.route('/stock')
def stock_page():
    try:
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row  
        cur = con.cursor();
        cur.execute("SELECT * FROM Users")
        rows = cur.fetchall()
        return render_template("stock.html", rows=rows)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        con.close()