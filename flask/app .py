from flask import Flask, render_template, request, redirect, url_for,flash,session
import mysql.connector

app = Flask(__name__,static_url_path='/static')
app.secret_key = '123'
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="20ita19",
    database="demo"
)

@app.route('/index')
def index():
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    return render_template('index.html', cash_balance=cash_balance,username=session.get('username'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login')) 

@app.route("/storage", methods=["GET", "POST"])
def storage():
    if request.method == "POST":
        if request.form["action"] == "add":
            item_name = request.form["item_name"].lower() 
            
            cursor = db.cursor()
            
           
            cursor.execute("SELECT COUNT(*) FROM item WHERE LOWER(item_name) = %s", (item_name,))
            item_count = cursor.fetchone()[0]
            
            if item_count > 0:
                flash("Item already exists.", "warning")
            else:
                cursor.execute("SELECT MAX(item_id) FROM item")
                last_id = cursor.fetchone()[0]
                if last_id is None:
                    next_id = "PRO001"
                else:
                    last_number = int(last_id[3:])  
                    next_number = last_number + 1
                    next_id = "PRO" + str(next_number).zfill(3)
                cursor.execute("INSERT INTO item (item_id, item_name) VALUES (%s, %s)", (next_id, item_name,))
                db.commit()
                flash("Item added successfully.", "success")
            
            cursor.close()
        elif request.form["action"] == "remove":
            cursor = db.cursor()
            item_name = request.form["item_name"].lower()  
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            db.commit()

            cursor.execute("DELETE FROM item WHERE LOWER(item_name) = %s", (item_name,))
            db.commit()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            cursor.close()

    cursor = db.cursor()
    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    return render_template("storage.html", items=items, cash_balance=cash_balance, username=session.get('username'))



@app.route('/history')
def history():
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM purchase")
    data = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sales")
    datas = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    
    return render_template('history.html', data=data,datas=datas,cash_balance=cash_balance,username=session.get('username'))
    
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        item_id = request.form['item']
        qty = int(request.form['qty'])
        rate = float(request.form['rate'])
        cursor=db.cursor()
        cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
        cbal = cursor.fetchone()[0]
        cursor.close()

        if qty * rate > cbal:
             prompt_message = "insufficient balance"
             cursor = db.cursor()
             cursor.execute("SELECT * FROM item")
             items = cursor.fetchall()
             cursor.close()
             cursor = db.cursor()
             cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
             cash_balance = cursor.fetchone()[0]
             cursor.close()
             return render_template('purchase.html', items=items,prompt_message=prompt_message,cash_balance=cash_balance,username=session.get('username'))
        else:

            cursor=db.cursor()
            cursor.execute("SELECT MAX(purchase_id) FROM purchase")
            last_id = cursor.fetchone()[0]
            if last_id is None:
                next_id = "P001"
            else:
                last_number = int(last_id[1:])  
                next_number = last_number + 1
                next_id = "P" + str(next_number).zfill(3)

            cursor.execute("INSERT INTO purchase (purchase_id,item_id, qty, rate, amount) VALUES (%s ,%s, %s, %s, %s)",
                       (next_id,item_id, qty, rate, qty * rate))
        
            db.commit()
            cursor.execute("UPDATE item SET qty = qty + %s WHERE item_id = %s", (qty,item_id,))
            db.commit()
            cursor.execute("UPDATE company SET cash_balance = cash_balance - %s", (qty * rate,))
            db.commit()

            cursor.close()

    cursor = db.cursor()
    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    return render_template('purchase.html', items=items, cash_balance=cash_balance,username=session.get('username'))

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    message=""
    if request.method == 'POST':
        item_id = request.form['item']
        qty = int(request.form['qty'])
        rate = float(request.form['rate'])
        
       
        cursor = db.cursor()
        cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
        cbal = cursor.fetchone()[0]
        cursor.close()
        if qty * rate > cbal:
             prompt_message = "insufficient balance"
             cursor = db.cursor()
             cursor.execute("SELECT * FROM item where qty>0")
             items = cursor.fetchall()
             cursor.close()
             cursor = db.cursor()
             cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
             cash_balance = cursor.fetchone()[0]
             cursor.close()
             return render_template('sales.html', items=items,prompt_message=prompt_message,cash_balance=cash_balance,username=session.get('username'))
        else:
            cursor = db.cursor()
            cursor.execute("select qty from item where item_id=%s",(item_id,))
            tmp =cursor.fetchone()[0]
        
            if qty>tmp or qty<0:
                  prompt_message = "exceeds the available quantity or does not meet the minimum quantity"
                  cursor = db.cursor()
                  cursor.execute("SELECT * FROM item where qty>0")
                  items = cursor.fetchall()
                  cursor.close()
                  cursor = db.cursor()
                  cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
                  cash_balance = cursor.fetchone()[0]
                  cursor.close()
                  return render_template('sales.html', items=items,prompt_message=prompt_message,cash_balance=cash_balance,username=session.get('username'))
               
            else: 
                cursor.execute("SELECT MAX(sales_id) FROM sales")
                last_id = cursor.fetchone()[0]
                if last_id is None:
                    next_id = "S001"
                else:
                    last_number = int(last_id[1:])  
                    next_number = last_number + 1
                    next_id = "s" + str(next_number).zfill(3)   

                cursor.execute("INSERT INTO sales (sales_id,item_id, qty, rate, amount) VALUES (%s,%s, %s, %s, %s)",
                       (next_id,item_id, qty, rate, qty * rate))
                db.commit()
                cursor.execute("UPDATE item SET qty = qty - %s WHERE item_id = %s", (qty,item_id,))
                db.commit()

                cursor.execute("UPDATE company SET cash_balance = cash_balance + %s", (qty * rate,))
                db.commit()
                cursor.close()

    cursor = db.cursor()
    cursor.execute("SELECT * FROM item where qty>0")
    items = cursor.fetchall()
    cursor.close()
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    return render_template('sales.html', items=items,message=message,cash_balance=cash_balance,username=session.get('username'))
@app.route('/money', methods=['GET', 'POST'])
def money():
    if request.method == 'POST':
        amount = float(request.form['amount'])

        cursor = db.cursor()
        cursor.execute("UPDATE company SET cash_balance = cash_balance + %s", (amount,))
        db.commit()
        cursor.close()

        
    cursor = db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()[0]
    cursor.close()
    return render_template('money.html',cash_balance=cash_balance,username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
