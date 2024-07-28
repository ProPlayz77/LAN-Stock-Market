import mysql.connector
import HOST
import socket
import pickle
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

def fetch_stocks():
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM stocks"
    cursor.execute(query)
    stock = cursor.fetchall()
    cursor.close()
    connection.close()
    return stock


def buy_stock(symbol, quantity, uid):
    HOST.update_stock(symbol, quantity, True, uid)

def sell_stock(symbol, quantity, uid):
    HOST.update_stock(symbol, quantity, False, uid)

def fetch_stock_price(symbol):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT price FROM stocks WHERE symbol = %s"
    cursor.execute(query, (symbol,))
    price = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return price


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(('localhost',9997))
sock.listen()
print("listening for incoming connections....")

while True:
    conn, addr = sock.accept()
    data = conn.recv(1024)
    mesga = pickle.loads(data)
    if mesga[0]=="@":
        stox=fetch_stocks()
        conn.sendall((pickle.dumps(stox)))
    elif mesga[0]=="#":
        inp=mesga[1:]
        x=fetch_stock_price(inp)
        conn.sendall(pickle.dumps(str(x)))
        print("stock price sent to user")
    elif mesga[0] == '$':  # Fetch user balance or insert new user
        uid = mesga[1:]
        connection = create_connection()
        cursor = connection.cursor()

        try:
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (uid,))
            user_data = cursor.fetchone()

            if user_data:
                balance = user_data[1]  # Assuming balance is in the second column
                conn.sendall(pickle.dumps(balance))
                print(f"User balance sent to user: {balance}")
            else:
                initial_balance = 100000
                query = "INSERT INTO users (user_id, balance) VALUES (%s, %s)"
                cursor.execute(query, (uid, initial_balance))
                connection.commit()
                conn.sendall(pickle.dumps(initial_balance))
                print(f"New user inserted with initial balance: {initial_balance}")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            conn.sendall(pickle.dumps("Error fetching user balance"))

        finally:
            cursor.close()
            connection.close()
    else:
        inp=mesga.split()
        if inp[0]=="buy":
            HOST.update_stock(str(inp[1]),int(inp[2]),True, inp[3])

            connection = create_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (inp[3],))
            user_data = cursor.fetchone()
            balance = user_data[1]
            cost= fetch_stock_price(str(inp[1]))*int(inp[2])
            new_balance= balance-cost
            query = "UPDATE users SET balance = %s WHERE user_id = %s"
            print("user Balance updated!")
            print(new_balance,cost,balance)
            cursor.execute(query, (new_balance, inp[3]))
            connection.commit()
            cursor.close()
            connection.close()
            conn.sendall(pickle.dumps("Success!"))

        else:
            HOST.update_stock(str(inp[1]), int(inp[2]), False, inp[3])
            conn.sendall(pickle.dumps("Success!"))



