import mysql.connector
from mysql.connector import Error

def fetch_stock(symbol):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM stocks WHERE symbol = %s"
    cursor.execute(query, (symbol,))
    stock = cursor.fetchone()
    cursor.close()
    connection.close()
    return stock
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="stock_market"
        )
    except Error as e:
        print(f"Error: '{e}'")

    return connection


def update_stock(symbol, quantity, is_buy,uid):
    connection = create_connection()
    if connection is None:
        print("Failed to create connection")
        return

    cursor = connection.cursor()

    try:
        # Check current stock quantity and price
        cursor.execute("SELECT quantity, price FROM stocks WHERE symbol = %s", (symbol,))
        result = cursor.fetchone()
        if result is None:
            print("Stock symbol not found")
            return

        current_quantity, current_price = result
        perc=quantity/current_quantity
        if is_buy:
            if current_quantity < quantity:
                print("Not enough stock available")
                return
            new_quantity = current_quantity - quantity
            # Increase price by 1% for each unit bought
            new_price = float(current_price) * (1 + perc * (quantity))
        else:
            new_quantity = current_quantity + quantity
            # Decrease price by 1% for each unit sold
            new_price = float(current_price) * (1 - perc * quantity)
            if new_price < 0:  # Ensure the price doesn't go negative
                new_price = 0.01

        # Update the stock quantity and price
        cursor.execute("UPDATE stocks SET quantity = %s, price = %s WHERE symbol = %s",
                       (new_quantity, new_price, symbol))
        connection.commit()

        print(f"Stock {symbol} updated. New quantity: {new_quantity}, New price: ${new_price:.2f}")
    except Error as e:
        print(f"Error updating stock: {e}")
    finally:
        cursor.close()
        connection.close()
    act=0
    if is_buy:
        act='buy'
    else:
        act='sell'
    connection = create_connection()
    cursor = connection.cursor()
    query = "INSERT INTO transactions (user_id, symbol, quantity, price, type) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (uid, symbol, quantity, fetch_stock(symbol)[2], act))
    connection.commit()
    cursor.close()
    connection.close()


def add_stock(symbol, name, price, quantity):
    connection = create_connection()
    if connection is None:
        print("Failed to create connection")
        return

    cursor = connection.cursor()

    try:
        # Insert new stock into the stocks table
        query = "INSERT INTO stocks (symbol, name, price, quantity) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (symbol, name, price, quantity))
        connection.commit()

        print(f"Stock {symbol} added: {name} at ${price} with quantity {quantity}")
    except Error as e:
        print(f"Error adding stock: {e}")
    finally:
        cursor.close()
        connection.close()

def addstocx():
    add_stock('TSLA', "Tesla Motors Inc", 1500, 500)
    add_stock('AAPL', "Apple Inc", 1000, 150)
    add_stock('MSFT', "Microsoft Corporation", 800, 300)
    add_stock('GOOGL', "Alphabet Inc Class A", 600, 2500)
    add_stock('AMZN', "Amazon.com Inc", 700, 3200)
    add_stock('FB', "Meta Platforms Inc", 900, 350)
    add_stock('NVDA', "NVIDIA Corporation", 500, 800)
    add_stock('INTC', "Intel Corporation", 1200, 60)
    add_stock('AMD', "Advanced Micro Devices Inc", 1500, 100)
    add_stock('NFLX', "Netflix Inc", 600, 400)
    add_stock('TSLA', "Tesla Inc", 1500, 500)
    add_stock('PYPL', "PayPal Holdings Inc", 800, 250)
    add_stock('SQ', "Square Inc", 1000, 200)
    add_stock('DIS', "The Walt Disney Company", 700, 180)
    add_stock('CRM', "Salesforce.com Inc", 900, 220)
    add_stock('UBER', "Uber Technologies Inc", 1500, 50)