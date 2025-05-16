from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='fjdkSLA1983%!',
        database='dwh'
    )

@app.route('/')
def index():
    return redirect('/add')

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = int(request.form['amount'])
        type_ = request.form['type'].strip()
        memo = request.form['memo']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO kakeibo (date, category, amount, type, memo) VALUES (%s, %s, %s, %s, %s)",
            (date, category, amount, type_, memo)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/add')
    
    return render_template('add.html')

@app.route('/view')
def view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kakeibo ORDER BY date DESC")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
