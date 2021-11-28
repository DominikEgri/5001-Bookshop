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
      try:
        with sqlite3.connect("database.db") as con:
                  con.row_factory = sqlite3.Row 
                  cur = con.cursor()
                  for key, value in session['Shoppingcart'].items():
                    cur.execute("UPDATE Books SET quantity=quantity + ? WHERE isbn13 = ?",(quantity, key,)) #if user pay the update the quantity of the database correspondly the amount of books what the user bought.
                    con.commit()
                  cur.close()
                  con.close()
                  flash("The transaction was successfull!", "info")
                  session.clear()
                  redirect(url_for('payment_page'))
      except:
          flash("The transaction was unsuccessful1")
          return redirect(url_for('YourBasket'))
      finally:
          cur.close()
          con.close()
      return redirect(url_for('thanks_page'))

@app.route('/tanks')
def thanks_page():
  return render_template("thanks.html")


@app.route('/')
def home_page():
    
    return render_template('home.html', title="Home")



@app.route('/login', methods=["POST", "GET"])
def login_page():							#logging into the website
    if "username" in session:						#checking the session which name is username
        if session["username"] == "admin":				#if it is admin then
            return redirect(url_for('admin_page_validation'))		#Then redirect to the admin interface
        else:
            return redirect(url_for('user_page'))			#else redirect to the user interface
        
    elif request.method == "POST":					#if the user send their name and password
        session.permanent = True					#make the session permanent (3 days long)
        username = request.form["nm"]					#get the username from the form
        password = request.form["ps"]					#get the username from the form
        with sqlite3.connect("database.db") as con:			#connect to the database
                cur = con.cursor()
                query = "SELECT name, password FROM Users WHERE name = '"+username+"'  AND password = '"+password+"'"	#select the name and password
                cur.execute(query)											#execute query
                users = cur.fetchall()
                for user in users:
                    if(username == user[0] and password == user[1]):							#if username and password exist enter
                        session["username"] = username									#save username to session
                        flash("You have been logged in", "info")
                        redirect(url_for('user_page'))									#redirect to the user interface
                    else:
                        return render_template('login.html', text="Unsuccessful login")   				#else redirect back to loginpage
    
    
    return render_template('login.html')										#default render template
    
    
@app.route('/register', methods=["POST", "GET"])			#registering
def register_page():
    if request.method == "POST":					#if user sent the form save username and passsword into variables
        username = request.form["name"]					#username
        password = request.form["password"]				#password
        try:		
            
             with sqlite3.connect("database.db") as con:		#connect to database.db
                cur = con.cursor()
                
                cur.execute("INSERT INTO Users (name, password) VALUES (?, ?)",(username, password))	#Insert into username and password, registrate
                
                con.commit()										#commit the query
                con.close()										#close connection
                session.permanent = True
                session["username"] = username
                flash("You have been registered!", "info")
                return redirect(url_for('user_page'))
        except:												#handling exceptions
            flash("The username is already in use. Try another one!")
            return redirect(url_for('register_page'))							#redirect back to register page
            con.close()
    return render_template('register.html')								#default render register
    
@app.route('/user', methods=["POST", "GET"])					#user page
def user_page():
    if "username" in session:							#if user already in session it is automaticly lets them in
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row						#it is fetching rows 
        cur = con.cursor()
        cur.execute("select * from Books WHERE quantity > 0")   		#selects books where quantity is not empyt
        rows = cur.fetchall()	
        return render_template('user.html', title="User",rows=rows)		#sending the rows from the database to the user.html
    else:
        redirect(url_for('login_page'))						#Your are not logged in, redirect to login page
        
        
@app.route('/user/<string:code>')						#html page giving back code variable
def user_bookview(code):
      with sqlite3.connect("database.db") as con:
              con.row_factory = sqlite3.Row 
              cur = con.cursor()
              cur.execute("SELECT * FROM Books WHERE title = ?",(code,))	#select book where the isbn13 number is the same
              rows = cur.fetchall()
              return render_template('view_book.html', rows = rows)		#sending the book
              con.commit()
              con.close()
      return render_template('view_book.html', isbn13 = code)			#default render
          
@app.route('/chart/<string:code>')						#saving the sibn13 number
def chartSaveProductId(code):
    session['product_id_session'] = code					#saving it to the "product_id_session"
    return redirect(url_for('addToChart_product'))				#sending it to the addToChart_product function

@app.route('/chart', methods=["POST", "GET"])   				#adding products to the shopping cart
def addToChart_product():
    if request.method == "POST":						#if form sent from user
      try:
        product_id = request.form.get('product_id')				#saving id from form
        quantity = int(request.form.get('quantity'))				#saving quantity from form
        if product_id and quantity:						#if id and quantity exists
            con = sqlite3.connect('database.db')
            cur = con.cursor();
            cur.execute("SELECT * FROM Books WHERE isbn13=?;", (product_id,))	#selecting the correct book
            row = cur.fetchone()

            dictItems = {product_id : {"isbn13" : row[0], "name" : row[1], "price" : row[6], "quantity" : quantity, "totalPrice": quantity * row[6]}}	#saving specific value about the correct book from the database in a dictionary

            totalQuantity = 0	#seting up default value
            totalPrice = 0	#seting up default value

            session.modified = True

            if "Shoppingcart" in session:							#if session "Shoppingcart" exist
              if product_id in session['Shoppingcart']:						#if the dictionary in session
                for key, value in session['Shoppingcart'].items():				#looping through the "Shoppincart" session elements
                  if key == row[0]:								#if Shoppingcart key ("isbn13" or "name" etc..) == row[0] 
                    oldQuantity = session['Shoppingcart'][key]['quantity']			#the amount of the item before
                    totalQuantity = oldQuantity + quantity					#the amount of the item now
                    session['Shoppingcart'][key]['quantity'] = totalQuantity			#setting "Shoppingcart" session by adding up the two number
                    session['Shoppingcart'][key]['totalPrice'] = totalQuantity * row[6]		#setting "Shoppingcart" session with the new correct value, calculating the total value
              else:
                session['Shoppingcart'] = array_merge(session['Shoppingcart'], dictItems)	#else creating the "Shoppingcart" session with the dictItems dictionary
                
              for key, value in session['Shoppingcart'].items():				#looping "Shoppingcart" session
                itemQuantity = int(session['Shoppingcart'][key]['quantity'])			#get how many item
                itemPrice = int(session['Shoppingcart'][key]['totalPrice'])			#get how much money
                totalQuantity += itemQuantity							#adding together the total quantity
                totalPrice += itemPrice * row[6]						#calculating the total price
            else:					
              session['Shoppingcart'] = dictItems						#if the program didnt find the item
              totalQuantity += quantity								#saving total item
              totalPrice += quantity * row[6]							#saving total price

              session['totalQuantity'] = totalQuantity						#saving total item to session
              session['totalPrice'] = totalPrice						#saving total price to session

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
        
@app.route('/YourBasket')							#showing user cart
def your_basket_page():
    if "Shoppingcart" not in session:						#if there is not any item in the shoppincart
      return render_template("user.html")					#go back to user.html
    total_price = 0
    total_items = 0
    for key, item in session['Shoppingcart'].items():
      total_price += item['totalPrice']						#calculating the total price to pay
      total_items += item['quantity']						#calculating the quantity
    
    if total_items == 1:				#if only one book
      postage_cost = 3					#postage fee 3 pound
    else:						#if it is more than 1
      postage_cost = total_items + 2			#postage fee 3 + 1 pound for each book
    total_price = total_price + postage_cost
    total_price = ("%.2f" % float(total_price))
    total_items = ("%.2f" % float(total_items))
    return render_template("costumer_cart.html", basic_total_price = total_price, total_price = total_price, postage_cost = postage_cost)

@app.route('/delete/<string:code>')		#deleting items from the shopping cart
def delete_item(code):
	try:
		totalPrice = 0
		totalQuantity = 0
		session.modified = True
		
		for item in session['Shoppingcart'].items():		#looping "Shoppingcart" session
			if item[0] == code:				#if found the item
				session['Shoppingcart'].pop(item[0], None)	#delete the item
				if 'Shoppingcart' in session:
					for key, value in session['Shoppingcart'].items():
						item_quantity = int(session['Shoppingcart'][key]['quantity'])
						item_price = float(session['Shoppingcart'][key]['totalPrice'])
						totalQuantity += item_quantity	#recalculated total quantity
						totalPrice += item_price	#recalculated total price
				break
		
		if totalQuantity == 0:		#if it cart is empty then clear it fully
			session.clear()
		else:
			session['totalQuantity'] = totalQuantity
			session['totalPrice'] = totalPrice
		return redirect(url_for('your_basket_page'))
	except Exception as e:
		print(e)
  
  
@app.route('/logout')		#logout
def logout_page():
    flash("You have been logged out", "info")
    session.clear()				#clear the session
    return redirect(url_for('login_page'))	#redirect to login page



@app.route('/admin', methods=["POST","GET"])		#admin page
def admin_page_validation():
    if session["username"] == "admin":			#validating admin
        return redirect(url_for('admin_upload_page'))
    else:
        return redirect(url_for('home_page'))		#or redirect to home page
    
@app.route('/admin/upload', methods=["POST","GET"])	#routes what only can admin reach
def admin_upload_page():
    target = os.path.join(APP_ROOT, "static/images")	#the root path to the images file
    if request.method == "POST":
        image = request.files['file']			#getting the iamge from the form
        if request.files['file'].filename == '':	#if there if no file
            flash("There is no image!")
            return redirect(url_for("admin_page_validation"))
        
        elif image != "":
            filename = secure_filename(image.filename)
            destination = "/".join([target, filename])	#creating the destination
            image.save(destination)			#saving to the destination
            
            #Uploading data to database
            isbn13 = request.form["ISBN13"]		#Geting data from the user
            title = request.form["title"]		#
            author = request.form["author"]		#
            date_upload = request.form["date"]		#
            description = request.form["description"]	#
            image = request.files['file']		#
            price = request.form["price"]		#
            quantity = request.form["quantity"]		#
            try:
              with sqlite3.connect("database.db") as con:
                  con.row_factory = sqlite3.Row 
                  cur = con.cursor()
                  cur.execute("SELECT * FROM Books WHERE isbn13 = ?",(isbn13,))		#select book if it is exist
                  result = cur.fetchall()
                  if len(result) > 0:							#if book exist in database
                    cur.execute("UPDATE Books SET quantity = quantity + ? WHERE isbn13 = ?",(int(quantity),isbn13,))		#add quantity
                    flash("We add the item up to the existing stock!")
                    return redirect(url_for("admin_upload_page"))
                  else:														#if book doesnt exist in database
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
            
        

@app.route('/stock')						#stock view for only admin access
def stock_page():
    try:
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row  
        cur = con.cursor();
        cur.execute("SELECT name, password FROM Users")		#selecting specific columns
        rows = cur.fetchall()
        return render_template("stock.html", rows=rows)		#sending the rows to the webpage to appear them
    except Exception as e:
        print(e)
    finally:
        cur.close()
        con.close()
    return render_template('stock.html')
  
  
