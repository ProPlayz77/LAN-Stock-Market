Stock Market Client Application
-----------------
Introduction
-----------------
This project is a Stock Market Client Application developed using Python and Tkinter (with CustomTkinter). The application allows users to buy and sell stocks, view their portfolio, and check the balance. The user ID is determined by the IP address of the client computer. The project uses MySQL for database management and sockets for client-server communication.
-----------------
Features
Buy and sell stocks
View portfolio
Check balance
Fetch real-time stock prices
Maintain transaction history
Setup Instructions
-----------------

Prerequisites
Python 3.x
MySQL server
MySQL Connector for Python
Tkinter (with CustomTkinter)
Pickle (for data serialization)

-----------------
MySQL Setup
To set up the MySQL database and tables for the host, execute the following commands in your MySQL command line or any MySQL client:


CREATE DATABASE stock_market;

USE stocks;

CREATE TABLE stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    quantity INT
);

CREATE TABLE users (
    user_id VARCHAR(25) PRIMARY KEY,
    balance DECIMAL(15, 2)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(25),
    symbol VARCHAR(10),
    quantity INT,
    price DECIMAL(10, 2),
    type ENUM('buy', 'sell'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE portfolio (
    user_id VARCHAR(25),
    symbol VARCHAR(10),
    quantity INT,
    total_price DECIMAL(15, 2),
    purchase_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    PRIMARY KEY (user_id, symbol)
);
-----------------

To set up the client computers, open up the client UI and click on the config button

-----------------

In the HOST, hostui, client_handler, and client UI files, replace the "password" in the create_connection() functions to your sql password
