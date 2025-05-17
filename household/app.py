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
def main():
    return render_template('main.html')

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

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kakeibo WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/view')

@app.route('/view')
def view():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 収入取得
    cursor.execute("SELECT * FROM kakeibo WHERE type = '収入'")
    incomes = cursor.fetchall()
    total_income = sum(item['amount'] for item in incomes)

    # 支出取得
    cursor.execute("SELECT * FROM kakeibo WHERE type = '支出'")
    expenses = cursor.fetchall()
    total_expense = sum(item['amount'] for item in expenses)

    # 必要経費だけ抽出（教材代は除く）
    necessary_categories = ['交通費']
    necessary_expenses = [e for e in expenses if e['category'] in necessary_categories]
    total_necessary = sum(e['amount'] for e in necessary_expenses)

    # 実質収入 = 収入 - 必要経費
    net_income = total_income - total_necessary

    cursor.close()
    conn.close()

    return render_template(
        'view.html',
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expense=total_expense,
        total_necessary=total_necessary,
        net_income=net_income,
        balance=total_income - total_expense
    )

from collections import defaultdict

from collections import defaultdict
import json

@app.route('/monthly')
def monthly():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 必要経費カテゴリ
    necessary_categories = ['交通費']

    # すべての明細データ取得（年月付き）→ 実質収入計算用
    cursor.execute("""
        SELECT
            DATE_FORMAT(date, '%Y-%m') AS ym,
            type,
            category,
            amount
        FROM kakeibo;
    """)
    records = cursor.fetchall()

    # 月ごとの集計
    monthly = defaultdict(lambda: {
        'income': 0,
        'expense': 0,
        'necessary': 0,
        'net_income': 0
    })

    for r in records:
        ym = r['ym']
        if r['type'] == '収入':
            monthly[ym]['income'] += r['amount']
        elif r['type'] == '支出':
            monthly[ym]['expense'] += r['amount']
            if r['category'] in necessary_categories:
                monthly[ym]['necessary'] += r['amount']

    for ym, data in monthly.items():
        data['net_income'] = data['income'] - data['necessary']

    sorted_months = sorted(monthly.items())  # 昇順ソート

    # グラフ用：月別支出合計のみ
    cursor.execute("""
        SELECT
            DATE_FORMAT(date, '%Y-%m') AS ym,
            SUM(amount) AS total_expense
        FROM kakeibo
        WHERE type = '支出'
        GROUP BY ym
        ORDER BY ym ASC;
    """)
    rows = cursor.fetchall()

    labels = [row['ym'] for row in rows]
    expenses = [row['total_expense'] for row in rows]

    cursor.close()
    conn.close()

    return render_template(
        'monthly.html',
        monthly_data=sorted_months,
        labels=labels,
        expenses=expenses
    )


if __name__ == '__main__':
    app.run(debug=True)
