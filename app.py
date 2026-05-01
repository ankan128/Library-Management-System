from flask import Flask, render_template, request, redirect, session
from db_connection import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def home():
    return render_template("home.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        department = request.form["department"]

        if not name or not password:
            return "All fields required"

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(user_id) FROM users")
        result = cursor.fetchone()
        new_id = 1 if result[0] is None else result[0] + 1

        cursor.execute("""
            INSERT INTO users(user_id,password,name,department,is_admin)
            VALUES(%s,%s,%s,%s,0)
        """, (new_id, hashed_password, name, department))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password, name FROM users
            WHERE user_id=%s
        """, (user_id,))

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user_id"] = user_id
            session["name"] = user[1]
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        keyword = request.form["keyword"]
        cursor.execute("""
            SELECT * FROM books
            WHERE title LIKE %s OR author LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("SELECT * FROM books")

    books = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", name=session["name"], books=books)

# ADD TO CART
@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO cart(user_id, book_id)
        VALUES(%s,%s)
    """, (session["user_id"], book_id))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# CART
@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.book_id, b.title, b.author
        FROM cart c
        JOIN books b ON c.book_id = b.book_id
        WHERE c.user_id=%s
    """, (session["user_id"],))

    books = cursor.fetchall()
    conn.close()

    return render_template("cart.html", books=books)

# BORROW
@app.route("/borrow_all")
def borrow_all():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT book_id FROM cart WHERE user_id=%s", (session["user_id"],))
    books = cursor.fetchall()

    for book in books:
        book_id = book[0]

        cursor.execute("SELECT quantity FROM books WHERE book_id=%s", (book_id,))
        qty = cursor.fetchone()[0]

        if qty > 0:
            cursor.execute("""
                INSERT INTO issue(book_id,user_id,issue_date)
                VALUES(%s,%s,CURDATE())
            """, (book_id, session["user_id"]))

            cursor.execute("""
                UPDATE books SET quantity = quantity - 1
                WHERE book_id=%s
            """, (book_id,))

    cursor.execute("DELETE FROM cart WHERE user_id=%s", (session["user_id"],))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# MY BOOKS
@app.route("/my_books")
def my_books():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.issue_id, b.book_id, b.title, b.author, i.issue_date
        FROM issue i
        JOIN books b ON i.book_id = b.book_id
        WHERE i.user_id=%s AND i.return_date IS NULL
    """, (session["user_id"],))

    books = cursor.fetchall()
    conn.close()

    return render_template("my_books.html", books=books)

# RETURN BOOK
@app.route("/return_book/<int:issue_id>")
def return_book(issue_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT book_id FROM issue WHERE issue_id=%s", (issue_id,))
    book_id = cursor.fetchone()[0]

    cursor.execute("UPDATE issue SET return_date=CURDATE() WHERE issue_id=%s", (issue_id,))
    cursor.execute("UPDATE books SET quantity=quantity+1 WHERE book_id=%s", (book_id,))

    conn.commit()
    conn.close()

    return redirect("/my_books")


@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    # Check admin
    cursor.execute("SELECT is_admin FROM users WHERE user_id=%s", (session["user_id"],))
    if cursor.fetchone()[0] == 0:
        return "Access Denied"

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    conn.close()

    return render_template("admin.html", books=books)



@app.route("/add_book", methods=["POST"])
def add_book():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_admin FROM users WHERE user_id=%s", (session["user_id"],))
    if cursor.fetchone()[0] == 0:
        return "Access Denied"

    title = request.form["title"]
    author = request.form["author"]
    quantity = request.form["quantity"]

    cursor.execute("""
        SELECT book_id, quantity FROM books
        WHERE title=%s AND author=%s
    """, (title, author))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE books
            SET quantity = quantity + %s
            WHERE book_id=%s
        """, (quantity, existing[0]))

    else:

        cursor.execute("SELECT MAX(book_id) FROM books")
        result = cursor.fetchone()
        new_id = 1 if result[0] is None else result[0] + 1

        cursor.execute("""
            INSERT INTO books(book_id,title,author,quantity,is_available)
            VALUES(%s,%s,%s,%s,1)
        """, (new_id, title, author, quantity))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
    
    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)