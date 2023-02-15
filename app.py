from flask import Flask, render_template, url_for, request, redirect
import psycopg2
import os

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


if __name__ == '__main__':
   app.run(debug=False)