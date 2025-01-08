from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',       # Replace with your MySQL username
    'password': 'Gova@12345', # Replace with your MySQL password
    'database': 'user_management'  # Replace with your database name
}

# Initialize the database
def init_db():
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS user_management")
        connection.database = db_config['database']
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

init_db()

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("welcome"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            if user:
                session["user"] = user[1]  # Store first name in session
                return redirect(url_for("welcome"))
            else:
                return render_template("login.html", error_message="Invalid credentials. Please try again.")
        except Error as e:
            print(f"Error during login: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password) 
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, email, password))
            connection.commit()
            return render_template("signup.html", success_message="Account created successfully! Please login.")
        except mysql.connector.IntegrityError:
            return render_template("signup.html", error_message="Email already exists. Please try another.")
        except Error as e:
            print(f"Error during signup: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template("signup.html")

@app.route("/welcome")
def welcome():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("welcome.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
