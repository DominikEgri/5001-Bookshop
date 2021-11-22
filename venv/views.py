from flask import Flask, render_template, url_for, request, redirect, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
import os



app = Flask(__name__)
app.secret_key = "alma"
app.permanent_session_lifetime = timedelta(days = 3)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#'website/venv/static/images'
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
        if session["username"] == "admin":
            return redirect(url_for('admin_page_validation'))
        else:
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
        username = request.form["name"]
        password = request.form["password"]
        try:
            
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
            flash("The username is already in use. Try another one!")
            return redirect(url_for('register_page'))
            con.close()
    return render_template('register.html')
    
@app.route('/user', methods=["POST", "GET"])
def user_page():
    if "username" in session:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from Books WHERE quantity > 0")   
        rows = cur.fetchall()
        return render_template('user.html', title="User",rows=rows)
    else:
        flash("You are not logged in.")
        redirect(url_for('login_page'))
        
        
@app.route('/user/<string:code>')
def user_bookview(code):
      with sqlite3.connect("database.db") as con:
              con.row_factory = sqlite3.Row 
              cur = con.cursor()
              cur.execute("SELECT * FROM Books WHERE title = ?",(code,))
              rows = cur.fetchall()
              return render_template('nothing.html', rows = rows)
              con.commit()
              con.close()
      return render_template('nothing.html', isbn13 = code)
        

@app.route('/logout')
def logout_page():
    flash("You have been logged out", "info")
    session.pop("username", None)
    return redirect(url_for('login_page'))



@app.route('/admin', methods=["POST","GET"])
def admin_page_validation():
    if session["username"] == "admin":
        return redirect(url_for('admin_upload_page'))
    else:
        return redirect(url_for('home_page'))
    
@app.route('/admin/upload', methods=["POST","GET"])
def admin_upload_page():
    target = os.path.join(APP_ROOT, "static/images")
    if request.method == "POST":
        image = request.files['file']
        if request.files['file'].filename == '':
            flash("There is no image!")
            return redirect(url_for("admin_page_validation"))
        
        elif image != "":
            filename = secure_filename(image.filename)
            destination = "/".join([target, filename])
            image.save(destination)
            
            #Uploading data to database
            isbn13 = request.form["ISBN13"]
            title = request.form["title"]
            author = request.form["author"]
            date_upload = request.form["date"]
            description = request.form["description"]
            image = request.files['file']
            price = request.form["price"]
            quantity = request.form["quantity"]
            flash("Image upload was successfull!")
            try:
              with sqlite3.connect("database.db") as con:
                  cur = con.cursor()
                  cur.execute('INSERT INTO Books(isbn13, title, author, releaseDate, description, image, price, quantity) VALUES(?, ?, ?, ?, ?, ? , ?, ?)',(isbn13, title, author, date_upload, description, image.filename, price, quantity))
                  flash("Upload was successfull!")
                  con.commit()
                  con.close()
                  flash("Upload was successfull!")
            except:
              return redirect(url_for('admin_upload_page'))
        else:
            flash("Something went wrong.")
            con.close()
            return redirect(url_for("admin_upload_page"))
    return render_template('admin.html')
            
        

@app.route('/stock')
def stock_page():
    try:
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row  
        cur = con.cursor();
        cur.execute("SELECT name, password FROM Users")
        rows = cur.fetchall()
        return render_template("stock.html", rows=rows)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        con.close()
    return render_template('stock.html')