import re
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name = request.form['full_name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nonmedical",
            database="pcms"
        )

        cursor = db.cursor()

        sql = """
INSERT INTO users(name, email, phone, password)
VALUES(%s, %s, %s, %s)
"""

        values = (full_name, email, mobile, password)

        cursor.execute(sql, values)
        db.commit()

        return "Registration Successful!"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nonmedical",
            database="pcms"
        )

        cursor = db.cursor()

        sql = """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:
            return render_template('dashboard.html')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Complaint Page
# Complaint Page

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():


  if request.method == 'POST':

    category = request.form['category']
    title = request.form['title']
    description = request.form['description']
    location = request.form['location']

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nonmedical",
        database="pcms"
    )

    cursor = db.cursor()

    sql = """
    INSERT INTO complaints
    (title, description, category, location)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        title,
        description,
        category,
        location
    )

    cursor.execute(sql, values)
    db.commit()

    return "Complaint Submitted Successfully!"
  return render_template('complaint.html')
# view complaint 
@app.route('/view_complaints')
def view_complaints():

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nonmedical",
        database="pcms"
    )

    cursor = db.cursor()

    cursor.execute("""
        SELECT complaint_id, category, title, status
        FROM complaints
    """)

    complaints = cursor.fetchall()

    return render_template(
        'view_complaints.html',
        complaints=complaints
    ) 
@app.route('/admin')
def admin():

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nonmedical",
        database="pcms"
    )

    cursor = db.cursor()

    cursor.execute("""
        SELECT complaint_id, category, title, status
        FROM complaints
    """)

    complaints = cursor.fetchall()

    return render_template(
        'admin.html',
        complaints=complaints
    )
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nonmedical",
        database="pcms"
    )

    cursor = db.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE complaint_id=%s",
        (status, id)
    )

    db.commit()

    return redirect('/admin')
if __name__ == '__main__':
 app.run(debug=True)


