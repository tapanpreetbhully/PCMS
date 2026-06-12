import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nonmedical",
    database="pcms"
)

print("Database Connected Successfully")