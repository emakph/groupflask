from flask import Flask, render_template, url_for, request, redirect, session, flash
import psycopg2
import re

conn = psycopg2.connect("postgresql://postgres:admin123@localhost:5432/products_db")

app = Flask(__name__)

@app.route('/')
def index():

   cur = conn.cursor()
   cur.execute("SELECT * FROM products")
   data = cur.fetchall()
   
   return render_template('index.html', products = data)

@app.route('/insert')
def insert():
   return render_template('insert.html')

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
    return redirect(url_for('index'))

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id_data,))
    conn.commit()
    print('Data deleted successfully.')
    return redirect(url_for('index'))

#Used to insert the data
@app.route('/insert/insert_data/', methods = ['POST','GET'])
def insert_data():
   if request.method == "POST":
      product = request.form['product']
      manufacturer = request.form['manufacturer']
      stocks = request.form['stocks']

      cur = conn.cursor()
      insertQuery = "INSERT INTO products(product, manufacturer, stocks) VALUES (%s, %s, %s)"
      values = (product, manufacturer, stocks)
      cur.execute(insertQuery, values)
      print("Data Inserted Successfully.")
      conn.commit()
      
   return redirect(url_for('index'))

@app.route('/posts')
def posts():
   return render_template('posts.html')

#LOGIN LOGOUT REGISTER
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password, ))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('profile.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            conn.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/profile')
def profile(): 
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cur.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cur.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug=True)