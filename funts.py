import mysql.connector
from mysql.connector import Error


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


def update_stock(symbol, quantity, is_buy):
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

        if is_buy:
            if current_quantity < quantity:
                print("Not enough stock available")
                return
            new_quantity = current_quantity - quantity
            # Increase price by 1% for each unit bought
            new_price = float(current_price) * (1 + 0.01 * (quantity))
        else:
            new_quantity = current_quantity + quantity
            # Decrease price by 1% for each unit sold
            new_price = float(current_price) * (1 - 0.01 * quantity)
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