from flask import Flask, render_template, url_for, request, redirect, session, flash
import psycopg2
import re

conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/products_db")

app = Flask(__name__)
app.secret_key = '1234jsldfja;kldj;fla2'
@app.route('/')
def index():
    if session:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        data = cur.fetchall()

        return render_template('index.html', products = data)
    else:
        return redirect(url_for('login'))

@app.route("/edit/<int:id>", methods = ['GET'])
def user(id):
    cur = conn.cursor() 
    cur.execute("""SELECT * FROM products WHERE id = %s""", (id,))
    product = cur.fetchone()
    #cur.close()
    return render_template('edit.html', product = product)

@app.route('/edit/update_data/', methods = ["POST", "GET"])
def update_data():
    if request.method == 'POST':
        id = request.form['id']
        product = request.form['product']
        manufacturer = request.form['manufacturer']
        stocks = request.form['stocks']
    cur = conn.cursor()
    query = "UPDATE products SET product = %s,manufacturer = %s, stocks = %s WHERE id = %s"
    val = product, manufacturer, stocks, id
    cur.execute(query,val)
    conn.commit()
    return redirect(url_for('profile'))

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id_data,))
    conn.commit()
    print('Data deleted successfully.')
    return redirect(url_for('profile'))

@app.route('/insert')
def insert():
    return render_template('insert.html')

#Used to insert the data
@app.route('/insert/insert_data/', methods = ['POST','GET'])
def insert_data():
    if request.method == "POST":
        product = request.form['product']
        manufacturer = request.form['manufacturer']
        stocks = request.form['stocks']

        cur = conn.cursor()
        insertQuery = "INSERT INTO products(product, manufacturer, stocks, author) VALUES (%s, %s, %s, %s)"
        values = (product, manufacturer, stocks, session['id'])
        cur.execute(insertQuery, values)
        print("Data Inserted Successfully.")
        conn.commit()
        
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():

    if session:
        cur = conn.cursor()

        viewQuery = "SELECT * FROM products WHERE author= %s "
        values = str(session['id'])
        cur.execute(viewQuery, values)
        data = cur.fetchall()

        return render_template('profile.html', products = data)
    else:
        return redirect(url_for('login'))

    

#LOGIN LOGOUT REGISTER
@app.route("/login", methods = ['POST','GET'])
def login():
    if session:
        return redirect(url_for('index'))
    else:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            
            username = request.form['username']
            password = request.form['password']

            cursor =conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]

                msg = 'Logged in successfully !'
                return redirect(url_for('index'))
                #return render_template('index.html', msg = msg)
            else:
                msg = 'Incorrect username / password !'
        return render_template('login.html', msg = msg)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    if session:
        return redirect(url_for('index'))
    else:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username, ))
            account = cursor.fetchone()
            if account:
                #msg = 'Account already exists !'
                flash("Accounts exists Already")
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
        
                insertQuery = "INSERT INTO accounts(username, password, email) VALUES (%s, %s, %s)"
                values = (username,password, email)
                cursor.execute(insertQuery,values)
                conn.commit()
                msg = 'You have successfully registered !'
                return redirect(url_for('login'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('register.html', msg = msg)

if __name__ == '__main__':
   app.run(debug=True)