import customtkinter as tk
import mysql.connector
import HOST as h

tk.set_default_color_theme("blue")
tk.set_appearance_mode("dark")


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="stock_market",
        auth_plugin="caching_sha2_password"
    )
    return connection


def fetch_stock(symbol):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM stocks WHERE symbol = %s"
    cursor.execute(query, (symbol,))
    stock = cursor.fetchone()
    cursor.close()
    connection.close()
    return stock


def add_stock(symbol, quantity):
    h.update_stock(symbol, quantity, False, 0)


def revoke(symbol, quantity):
    h.update_stock(symbol, quantity, True, 0)


def delt(symbol):
    connection = create_connection()
    cursor = connection.cursor()
    update_query = "DELETE FROM stocks WHERE symbol = %s"
    cursor.execute(update_query, (symbol))
    print(f"Stock {symbol} Deleted")
    connection.commit()
    cursor.close()
    connection.close()

def show_list():
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM stocks"
    cursor.execute(query)
    stock = cursor.fetchall()
    cursor.close()
    connection.close()
    stock_window = tk.CTkToplevel()
    stock_window.title("Stock Prices")
    headers = ["Symbol", "Company Name", "Price", "Quantity"]

    # Create headers
    for col, header in enumerate(headers):
        label = tk.CTkLabel(stock_window, text=header, padx=10, pady=5)
        label.grid(row=0, column=col, sticky=tk.W)

    # Insert data
    for row, stoc in enumerate(stock, start=1):
        for col, value in enumerate(stoc):
            label = tk.CTkLabel(stock_window, text=value, padx=10, pady=5)
            label.grid(row=row, column=col, sticky=tk.W)

    stock_window.mainloop()

def change_price(symbol, amount):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        update_query = "UPDATE stocks SET price = %s WHERE symbol = %s"
        cursor.execute(update_query, (amount, symbol))
    except Exception as e:
        print(e)
    print(f"Stock {symbol} updated, New price: ${amount}")
    connection.commit()
    cursor.close()
    connection.close()


def on_submit():
    symbol = symbol_entry.get()
    action = action_var.get()
    quantity = int(quantity_entry.get())

    if action == 'Issued':
        add_stock(symbol, quantity)
    elif action == 'Revoked':
        revoke(symbol, quantity)
    elif action == 'changed':
        change_price(symbol, quantity)
    else:
        delt(symbol)


# Tkinter UI
root = tk.CTk()
root.title("Stock Market Host Client")

tk.CTkLabel(root, text="Stock Symbol").grid(row=0, column=0)
symbol_entry = tk.CTkEntry(root)
symbol_entry.grid(row=0, column=1)

tk.CTkLabel(root, text="Quantity").grid(row=1, column=0)
quantity_entry = tk.CTkEntry(root)
quantity_entry.grid(row=1, column=1)

action_var = tk.StringVar(value='Buy')
tk.CTkRadioButton(root, text="Issue Stocks", variable=action_var, value='Issued').grid(row=2, column=0)
tk.CTkRadioButton(root, text="Remove Stocks", variable=action_var, value='Revoked').grid(row=2, column=1)
tk.CTkRadioButton(root, text="Change price", variable=action_var, value='changed').grid(row=2, column=3)
tk.CTkRadioButton(root, text="Delete Stock", variable=action_var, value='deleted').grid(row=3, column=3)
show_prices_button = tk.CTkButton(root, text="Show Stock Prices", command=show_list)
show_prices_button.grid(row=9,columnspan=2)
submit_button = tk.CTkButton(root, text="Submit", command=on_submit)
submit_button.grid(row=4, columnspan=2)

root.mainloop()
