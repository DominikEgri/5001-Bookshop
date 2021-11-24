from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.utils import secure_filename
import os
import stripe



app = Flask(__name__)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(days = 3)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_database.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#'website/venv/static/images'
#Initialize the database
db = SQLAlchemy(app)


def array_merge( dict1 , dict2 ):						#addig two array together
	if isinstance( dict1 , list ) and isinstance( dict2 , list ):		#if bot parameters are list
		return dict1 + dict2						#add them together
	elif isinstance( dict1 , dict ) and isinstance( dict2 , dict ):		#if bot parameters are dictionary
		return dict( list( dict1.items() ) + list( dict2.items() ) )	#add them together
	elif isinstance( dict1 , set ) and isinstance( dict2 , set ):		#if bot parameters are set
		return dict1.union( dict2 )					#add them together
	return False								#or return false

PUBLIC_KEY = 'pk_test_51JySPLH0wY32hbDngjClJRA750Gz5R1ZPiOPLc5xwU7Q4LMK3BGW5q6EWlG4SFGwsGSnZTxGHtOvBeG9r6T4CzbF00NSacmOdL'
SECRET_KEY = 'sk_test_51JySPLH0wY32hbDn50tqqP9ojorUy2HTfb3V1qqFvdzhF6lfInfEwefOJT29j6T5WzqQpWspc00vSuI61sDg1vLb00oOrkPpdA'

@app.route('/payment_page', methods=["POST", "GET"])
def payment_page():
   with sqlite3.connect("database.db") as con:
              con.row_factory = sqlite3.Row 
              cur = con.cursor()
              for key, value in session['Shoppingcart'].items():
                cur.execute("UPDATE Books SET quantity=quantity + ? WHERE isbn13 = ?",(quantity, key,))
              con.commit()
              con.close()
              
              flash("The transaction was successfull!", "info")
              session.clear()
  
              return redirect(url_for('thanks_page'))

@app.route('/tanks')
def thanks_page():
  return render_template("thanks.html")


@app.route('/')
def home_page():
    
    return render_template('home.html', title="Home")



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
              return render_template('view_book.html', rows = rows)
              con.commit()
              con.close()
      return render_template('view_book.html', isbn13 = code)
          
@app.route('/chart/<string:code>')
def chartSaveProductId(code):
    session['product_id_session'] = code
    return redirect(url_for('addToChart_product'))

@app.route('/chart', methods=["POST", "GET"])   
def addToChart_product():
    if request.method == "POST":
      try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        if product_id and quantity:
            flash("im in the main part")
            con = sqlite3.connect('database.db')
            cur = con.cursor();
            cur.execute("SELECT * FROM Books WHERE isbn13=?;", (product_id,))
            row = cur.fetchone()

            dictItems = {product_id : {"isbn13" : row[0], "name" : row[1], "price" : row[6], "quantity" : quantity, "totalPrice": quantity * row[6]}}

            totalQuantity = 0
            totalPrice = 0

            session.modified = True

            if "Shoppingcart" in session:
              if product_id in session['Shoppingcart']:
                for key, value in session['Shoppingcart'].items():
                  if key == row[0]:
                    oldQuantity = session['Shoppingcart'][key]['quantity']
                    totalQuantity = oldQuantity + quantity
                    session['Shoppingcart'][key]['quantity'] = totalQuantity
                    session['Shoppingcart'][key]['totalPrice'] = totalQuantity * row[6]
              else:
                session['Shoppingcart'] = array_merge(session['Shoppingcart'], dictItems)
                
              for key, value in session['Shoppingcart'].items():
                itemQuantity = int(session['Shoppingcart'][key]['quantity'])
                itemPrice = int(session['Shoppingcart'][key]['totalPrice'])
                totalQuantity += itemQuantity
                totalPrice += itemPrice * row[6]
            else:
              session['Shoppingcart'] = dictItems
              totalQuantity += quantity
              totalPrice += quantity * row[6]

              session['totalQuantity'] = totalQuantity
              session['totalPrice'] = totalPrice

              return render_template("chart.html", id = session['product_id_session'])
        else:
              flash("Something went wrong!")
      except Exception as e:
        print(e)
      finally:
        cur.close()
        con.close()
    else:
      return render_template("chart.html", id = session['product_id_session'])
    return render_template("chart.html", id = session['product_id_session'])
        
@app.route('/YourBasket')
def your_basket_page():
    if "Shoppingcart" not in session:
      return render_template("user.html")
    total_price = 0
    total_items = 0
    for key, item in session['Shoppingcart'].items():
      total_price += item['totalPrice']
      total_items += item['quantity']
    
    if total_items == 1:
      postage_cost = 3
    else:
      postage_cost = total_items + 2
    total_price = total_price + postage_cost
    total_price = ("%.2f" % float(total_price))
    total_items = ("%.2f" % float(total_items))
    return render_template("costumer_cart.html", basic_total_price = total_price, total_price = total_price, postage_cost = postage_cost)

@app.route('/delete/<string:code>')
def delete_item(code):
	try:
		totalPrice = 0
		totalQuantity = 0
		session.modified = True
		
		for item in session['Shoppingcart'].items():
			if item[0] == code:				
				session['Shoppingcart'].pop(item[0], None)
				if 'Shoppingcart' in session:
					for key, value in session['Shoppingcart'].items():
						item_quantity = int(session['Shoppingcart'][key]['quantity'])
						item_price = float(session['Shoppingcart'][key]['totalPrice'])
						totalQuantity += item_quantity
						totalPrice += item_price
				break
		
		if totalQuantity == 0:
			session.clear()
		else:
			session['totalQuantity'] = totalQuantity
			session['totalPrice'] = totalPrice
		return redirect(url_for('your_basket_page'))
	except Exception as e:
		print(e)
  
@app.route('/checkout', methods=["POST", "GET"])
def checkout_page():
  return render_template("checkout.html")
  
@app.route('/logout')
def logout_page():
    flash("You have been logged out", "info")
    session.clear()
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
                  con.row_factory = sqlite3.Row 
                  cur = con.cursor()
                  cur.execute("SELECT * FROM Books WHERE isbn13 = ?",(isbn13,))
                  result = cur.fetchall()
                  if len(result) > 0:
                    cur.execute("UPDATE Books SET quantity = quantity + ? WHERE isbn13 = ?",(int(quantity),isbn13,))
                    flash("We add the item up to the existing stock!")
                    return redirect(url_for("admin_upload_page"))
                  else:
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
  
  
