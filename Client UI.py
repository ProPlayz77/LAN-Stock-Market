import customtkinter as tk
from tkinter import messagebox
import mysql.connector
import socket
import pickle
hostip='localhost'
port=9997
def create_connection():  # function to create mysql connection
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="stocks",
        auth_plugin="caching_sha2_password"
        )
    return connection

hn = socket.gethostname()
IPs = socket.gethostbyname(hn)
uid = IPs #userid is the ip address of the client computer


def setup_database():  #sets up the portfolio and transactions tables on the client computer
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS transactions (id INT AUTO_INCREMENT PRIMARY KEY, user_id VARCHAR(25), symbol VARCHAR(10), quantity INT, price DECIMAL(10, 2), type ENUM('buy', 'sell'), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS portfolio (symbol VARCHAR(10) PRIMARY KEY, quantity INT, total_price DECIMAL(50, 2), purchase_price DECIMAL(10, 2), current_price DECIMAL(50, 2))")

    connection.commit()
    cursor.close()
    connection.close()
def show_port():
    conn = create_connection()
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM portfolio")
    stock_window = tk.CTkToplevel()
    stock_window.title("Stock Portfolio")
    headers = ["Symbol", "Quantity", "Total Price", "LTP"]
    stockx=cursor.fetchall()
    # Create headers
    for col, header in enumerate(headers):
        label = tk.CTkLabel(stock_window, text=header, padx=10, pady=5)
        label.grid(row=0, column=col, sticky=tk.W)

    # Insert data
    for row, stock in enumerate(stockx, start=1):
        for col, value in enumerate(stock):
            label = tk.CTkLabel(stock_window, text=value, padx=10, pady=5)
            label.grid(row=row, column=col, sticky=tk.W)

    stock_window.mainloop()
def show_list():
    stocks=send_to_host("@")
    stock_window = tk.CTkToplevel()
    stock_window.title("Stock Prices")
    headers = ["Symbol", "Company Name", "Price", "Quantity"]

    # Create headers
    for col, header in enumerate(headers):
        label = tk.CTkLabel(stock_window, text=header, padx=10, pady=5)
        label.grid(row=0, column=col, sticky=tk.W)

    # Insert data
    for row, stock in enumerate(stocks, start=1):
        for col, value in enumerate(stock):
            label = tk.CTkLabel(stock_window, text=value, padx=10, pady=5)
            label.grid(row=row, column=col, sticky=tk.W)

    stock_window.mainloop()

def send_to_host(message):  #function to interact with host machine using socket
    mesg = pickle.dumps(message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostip, port))
    sock.send(mesg)
    response = sock.recv(4096)
    resp=pickle.loads(response)
    print(resp)
    sock.close()
    return resp

def get_bal(uid):
    bal=send_to_host(f"${uid}")
    return bal
balance = get_bal(uid)

def update_balance_label(balance_label, new_balance): #updates the balance shown on the bottom right
    balance_label.configure(text=f"Balance: ${new_balance:.2f}")
def buy_stock(symbol, quantity, uid):
    connection = create_connection()
    cursor = connection.cursor()
    message=f"#{symbol}"
    price=float(send_to_host(message))
    cursor.execute("SELECT * FROM portfolio WHERE symbol = %s", (symbol,))
    stock = cursor.fetchone()
    if stock and balance>=(price*quantity):
        new_quantity = stock[1] + quantity
        new_total_price = stock[2] + (quantity * fetch_stock(symbol)[2])
        cursor.execute("UPDATE portfolio SET quantity = %s, total_price = %s, current_price = %s WHERE symbol = %s",
                       (new_quantity, new_total_price, fetch_stock(symbol)[2], symbol))
    else:
        total_price = float(price) * float(quantity)
        cursor.execute(
            "INSERT INTO portfolio (symbol, quantity, total_price, purchase_price, current_price) VALUES (%s, %s, %s, %s, %s)",
            (symbol, quantity, round(total_price,2), round(price,2), round(price,2)))
    send_to_host(f"buy {symbol} {quantity} {uid}")          #execute buy order on host machine
    cursor.execute("INSERT INTO transactions (user_id, symbol, quantity, price, type) VALUES (%s, %s, %s, %s, 'buy')",
                   (uid, symbol, quantity, price))

    connection.commit()
    cursor.close()
    connection.close()
    new_bal=float(balance)-float(price*quantity)
    update_balance_label(balance_label,new_bal)

def sell_stock(symbol, quantity, uid):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM portfolio WHERE symbol = %s", (symbol,))
    stock = cursor.fetchone()

    if stock and stock[1] >= quantity:
        new_bal = balance + (quantity * stock[3])
        update_balance_label(balance_label, new_bal)
        new_quantity = stock[1] - quantity
        new_total_price = stock[2] - (quantity * stock[3])
        send_to_host(f"sell {symbol} {quantity} {uid}")         #execute sell order on host machine
        if new_quantity > 0:
            cursor.execute("UPDATE portfolio SET quantity = %s, total_price = %s, current_price = %s WHERE symbol = %s",
                           (new_quantity, new_total_price, fetch_stock(symbol)[2], symbol))
        else:
            cursor.execute("DELETE FROM portfolio WHERE symbol = %s", (symbol,))

        cursor.execute(
            "INSERT INTO transactions (user_id, symbol, quantity, price, type) VALUES (%s, %s, %s, %s, 'sell')",
            (uid, symbol, quantity, fetch_stock(symbol)[2]))
        messagebox.showinfo("Success", f"Sold {quantity} shares of {symbol}!")
    else:
        messagebox.showinfo("There was a problem with Selling the stock, maybe check your portfolio?")
    connection.commit()
    cursor.close()
    connection.close()
def fetch_stock(symbol):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM portfolio WHERE symbol = %s"
    cursor.execute(query, (symbol,))
    stock = cursor.fetchone()
    cursor.close()
    connection.close()
    return stock



def on_submit():
    symbol = symbol_entry.get()
    action = action_var.get()
    quantity = int(quantity_entry.get())

    if action == 'Buy':
        buy_stock(symbol, quantity, uid)
    else:
        sell_stock(symbol, quantity, uid)



# Tkinter UI
root = tk.CTk()
root.title("Stock Market Client")

balance_label = tk.CTkLabel(root, text=f"Balance: ${balance:.2f}")
balance_label.place(relx=1.0, rely=1.0, anchor='se')

tk.CTkLabel(root, text="Stock Symbol").grid(row=0, column=0)
symbol_entry = tk.CTkEntry(root)
symbol_entry.grid(row=0, column=1)

tk.CTkLabel(root, text="Quantity").grid(row=1, column=0)
quantity_entry = tk.CTkEntry(root)
quantity_entry.grid(row=1, column=1)

action_var = tk.StringVar(value='Buy')
tk.CTkRadioButton(root, text="Buy", variable=action_var, value='Buy').grid(row=2, column=0)
tk.CTkRadioButton(root, text="Sell", variable=action_var, value='Sell').grid(row=2, column=1)

show_prices_button = tk.CTkButton(root, text="Show Stock Prices", command=show_list)
show_prices_button.grid(row=10,columnspan=2)

show_prices_button = tk.CTkButton(root, text="Show Portfolio", command=show_port)
show_prices_button.grid(row=1,column=5,columnspan=2)

config_button= tk.CTkButton(root, text="Config", command=setup_database)
config_button.grid(row=0,column=5,columnspan=2)

submit_button = tk.CTkButton(root, text="Submit", command=on_submit)
submit_button.grid(row=3, columnspan=2)

root.mainloop()
