import tkinter as tk
from tkinter import messagebox, ttk
import csv
from collections import defaultdict
from datetime import datetime

CSV_PATH = 'data/kakeibo.csv'

# =======================
# データ保存
# =======================
def save_record():
    date = date_entry.get()
    item = item_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()

    if not (date and item and amount and category):
        messagebox.showerror("エラー", "すべての項目を入力してください")
        return

    try:
        int(amount)
    except:
        messagebox.showerror("エラー", "金額は数値で入力してください")
        return

    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([date, item, amount, category])

    messagebox.showinfo("保存完了", "記録を保存しました！")
    date_entry.delete(0, tk.END)
    item_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)

# =======================
# 項目ごとの集計表示
# =======================
def show_item_summary():
    item_totals = defaultdict(int)
    total_amount = 0

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 4:
                continue
            _, item, amount_str, _ = row
            try:
                amount = int(amount_str)
                item_totals[item] += amount
                total_amount += amount
            except:
                continue

    result = "\n".join([f"{item}: {total}円" for item, total in item_totals.items()])
    result += f"\n\n【合計金額】{total_amount}円"
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

# =======================
# 月別の集計表示
# =======================
def show_month_summary():
    month_totals = defaultdict(int)

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 4:
                continue
            date_str, _, amount_str, _ = row
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                amount = int(amount_str)
                key = f"{date.year}-{date.month:02}"
                month_totals[key] += amount
            except:
                continue

    result = "\n".join([f"{month}月: {total}円" for month, total in sorted(month_totals.items())])
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

# =======================
# GUIレイアウト
# =======================
root = tk.Tk()
root.title("家計簿アプリ（GUI版）")

# 入力フォーム
tk.Label(root, text="日付 (YYYY-MM-DD):").grid(row=0, column=0)
tk.Label(root, text="項目:").grid(row=1, column=0)
tk.Label(root, text="金額:").grid(row=2, column=0)
tk.Label(root, text="カテゴリ:").grid(row=3, column=0)

date_entry = tk.Entry(root)
item_entry = tk.Entry(root)
amount_entry = tk.Entry(root)
category_entry = tk.Entry(root)

date_entry.grid(row=0, column=1)
item_entry.grid(row=1, column=1)
amount_entry.grid(row=2, column=1)
category_entry.grid(row=3, column=1)

tk.Button(root, text="記録を保存する", command=save_record).grid(row=4, column=0, columnspan=2, pady=5)

# 集計ボタンと出力エリア
tk.Button(root, text="項目ごとの集計を表示", command=show_item_summary).grid(row=5, column=0, columnspan=2, pady=2)
tk.Button(root, text="月別の集計を表示", command=show_month_summary).grid(row=6, column=0, columnspan=2, pady=2)

result_text = tk.Text(root, height=15, width=40)
result_text.grid(row=7, column=0, columnspan=2, pady=5)

root.mainloop()
