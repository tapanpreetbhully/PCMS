import os
import mysql.connector
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "pcms_secret_key"

# database connection settings
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "nonmedical"
DB_NAME = "pcms"

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# home page
@app.route("/")
def home():
    return render_template("index.html")


# user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]

        db = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        cursor = db.cursor()

        # check if email already exists
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            cursor.close()
            db.close()
            return redirect("/register")

        # save the new user
        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (full_name, email, mobile, password)
        )
        db.commit()
        cursor.close()
        db.close()

        flash("Registration successful. Please login.", "success")
        return redirect("/login")

    return render_template("register.html")


# login for both user and admin
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # check if its admin
        if email == "admin@pcms.com" and password == "admin123":
            session.clear()
            session["admin"] = True
            session["admin_email"] = email
            flash("Admin login successful.", "success")
            return redirect("/admin")

        # otherwise check from database
        db = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session.clear()
            session["user"] = email
            session["user_name"] = user[1]
            flash("Login successful.", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid email or password.", "danger")
            return redirect("/login")

    return render_template("login.html")


# user dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login to continue.", "warning")
        return redirect("/login")
    return render_template("dashboard.html")


# submit a new complaint
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "user" not in session:
        flash("Please login to continue.", "warning")
        return redirect("/login")

    if request.method == "POST":
        category = request.form["category"]
        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        photo = request.files.get("photo")

        # handle photo upload if provided
        filename = ""
        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        user_email = session["user"]

        db = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME
        )
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO complaints
            (title, description, category, location, user_email, photo, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (title, description, category, location, user_email, filename, "Pending")
        )
        db.commit()

        complaint_id = cursor.lastrowid
        cursor.close()
        db.close()

        flash("Complaint submitted successfully! Complaint ID: " + str(complaint_id), "success")
        return redirect("/complaint")

    return render_template("complaint.html")


# view complaints filed by logged in user
@app.route("/view_complaints")
@app.route("/my_complaints")
def my_complaints():
    if "user" not in session:
        flash("Please login to continue.", "warning")
        return redirect("/login")

    db = mysql.connector.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT complaint_id, category, title, status FROM complaints WHERE user_email=%s ORDER BY complaint_id DESC",
        (session["user"],)
    )
    complaints = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("view_complaints.html", complaints=complaints)


# admin panel - shows all complaints
@app.route("/admin")
def admin():
    if "admin" not in session:
        flash("Admin access required.", "danger")
        return redirect("/login")

    db = mysql.connector.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT complaint_id, category, title, description, location, status, photo FROM complaints ORDER BY complaint_id DESC"
    )
    complaints = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("admin.html", complaints=complaints)


# update complaint status (admin only)
@app.route("/update_status/<int:id>/<status>")
def update_status(id, status):
    if "admin" not in session:
        flash("Admin access required.", "danger")
        return redirect("/login")

    db = mysql.connector.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )
    cursor = db.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE complaint_id=%s",
        (status, id)
    )
    db.commit()
    cursor.close()
    db.close()

    flash("Complaint updated successfully.", "success")
    return redirect("/admin")


# delete a complaint (admin only)
@app.route("/delete_complaint/<int:id>")
def delete_complaint(id):
    if "admin" not in session:
        flash("Admin access required.", "danger")
        return redirect("/login")

    db = mysql.connector.connect(
        host=DB_HOST, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME
    )
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM complaints WHERE complaint_id=%s",
        (id,)
    )
    db.commit()
    cursor.close()
    db.close()

    flash("Complaint deleted successfully.", "success")
    return redirect("/admin")


# logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
