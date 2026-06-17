from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    make_response,
    flash
)

from flask_session import Session

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3
from datetime import datetime
import csv
import math
from io import StringIO

app = Flask(__name__)

app.secret_key = "websiteblockersecret"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

DATABASE = "website_blocker.db"


# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = user["username"]
            session["role"] = user["role"]

            flash("Welcome " + username + "!", "success")

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()

        try:
            conn.execute(
               """
               INSERT INTO users(username, password, role)
               VALUES(?, ?, ?)
               """,
               (
                  username,
                  hashed_password,
                  "user"
                )
            )     

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            return render_template(
                "register.html",
                error="Username already exists."
            )

    return render_template("register.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()
    
    flash("Logged out successfully.", "secondary")

    return redirect("/login")


# ---------------- CHANGE PASSWORD ----------------
@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (session["user"],)
        ).fetchone()

        if not check_password_hash(
            user["password"],
            current_password
        ):

            conn.close()

            flash("Current password is incorrect.", "danger")

            return redirect("/change_password")

        if new_password != confirm_password:

            conn.close()

            flash("New passwords do not match.", "warning")

            return redirect("/change_password")

        hashed_password = generate_password_hash(new_password)

        conn.execute(
            """
            UPDATE users
            SET password=?
            WHERE username=?
            """,
            (
                hashed_password,
                session["user"]
            )
        )

        conn.commit()
        conn.close()

        flash("Password changed successfully!", "success")

        return redirect("/")

    return render_template("change_password.html")


# -----------------------------
# User Profile
# -----------------------------
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (session["user"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user
    )

# ---------------- EXPORT CSV ----------------
@app.route("/export")
def export():

    if "user" not in session:
        return redirect("/login")

    conn = get_connection()

    websites = conn.execute(
        "SELECT * FROM blocked_websites ORDER BY id"
    ).fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow(["ID", "Website"])

    for website in websites:
        writer.writerow([website["id"], website["website"]])

    response = make_response(output.getvalue())

    response.headers["Content-Disposition"] = \
        "attachment; filename=blocked_websites.csv"

    response.headers["Content-Type"] = "text/csv"

    return response


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    page = request.args.get("page", 1, type=int)

    per_page = 5

    conn = get_connection()

    total_websites = conn.execute(
        "SELECT COUNT(*) FROM blocked_websites"
    ).fetchone()[0]

    total_pages = math.ceil(total_websites / per_page)

    offset = (page - 1) * per_page

    websites = conn.execute(
        """
        SELECT * FROM blocked_websites
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (per_page, offset)
    ).fetchall()

    history = conn.execute(
        """
        SELECT * FROM history
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    blocked_checks = conn.execute(
        """
        SELECT COUNT(*) FROM history
        WHERE status='Blocked'
        """
    ).fetchone()[0]

    allowed_checks = conn.execute(
        """
        SELECT COUNT(*) FROM history
        WHERE status='Allowed'
        """
    ).fetchone()[0]

    total_checks = blocked_checks + allowed_checks

    conn.close()

    return render_template(
        "index.html",
        websites=websites,
        history=history,
        total_websites=total_websites,
        blocked_checks=blocked_checks,
        allowed_checks=allowed_checks,
        total_checks=total_checks,
        page=page,
        total_pages=total_pages
    )

# -----------------------------
# Add Website
# -----------------------------
@app.route("/add", methods=["POST"])
def add():

    website = request.form["website"].strip().lower()

    if website:

        conn = get_connection()

        try:
            conn.execute(
                "INSERT INTO blocked_websites (website) VALUES (?)",
                (website,)
            )
            conn.commit()

            flash("✅ Website added successfully!", "success")

        except sqlite3.IntegrityError:

            flash("❌ Website already exists!", "danger")

        conn.close()

    return redirect("/")


# -----------------------------
# Delete Website
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM blocked_websites WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()
    
    flash("🗑️ Website deleted successfully!", "warning")

    return redirect("/")


# -----------------------------
# Edit Website
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_connection()

    if request.method == "POST":

        website = request.form["website"].strip().lower()

        conn.execute(
    """
    UPDATE blocked_websites
    SET website=?
    WHERE id=?
    """,
    (website, id)
)

        conn.commit()
        flash("✏️ Website updated successfully!", "info")
        conn.close()

        return redirect("/")

    website = conn.execute(
        "SELECT * FROM blocked_websites WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        website=website
    )


# -----------------------------
# Search Website
# -----------------------------
@app.route("/search", methods=["POST"])
def search():

    if "user" not in session:
        return redirect("/login")

    keyword = request.form["keyword"].strip().lower()

    conn = get_connection()

    websites = conn.execute(
        """
        SELECT *
        FROM blocked_websites
        WHERE LOWER(website) LIKE ?
        ORDER BY id DESC
        """,
        ("%" + keyword + "%",)
    ).fetchall()

    history = conn.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT 20"
    ).fetchall()

    total_websites = conn.execute(
        "SELECT COUNT(*) FROM blocked_websites"
    ).fetchone()[0]

    blocked_checks = conn.execute(
        "SELECT COUNT(*) FROM history WHERE status='Blocked'"
    ).fetchone()[0]

    allowed_checks = conn.execute(
        "SELECT COUNT(*) FROM history WHERE status='Allowed'"
    ).fetchone()[0]

    total_checks = blocked_checks + allowed_checks

    conn.close()

    # Pagination values
    page = 1
    total_pages = 1

    return render_template(
        "index.html",
        websites=websites,
        history=history,
        total_websites=total_websites,
        blocked_checks=blocked_checks,
        allowed_checks=allowed_checks,
        total_checks=total_checks,
        page=page,
        total_pages=total_pages
    )
# -----------------------------
# Check Website
# -----------------------------
@app.route("/check", methods=["POST"])
def check():

    if "user" not in session:
        return redirect("/login")

    website = request.form["website"].strip().lower()

    conn = get_connection()

    result = conn.execute(
        """
        SELECT *
        FROM blocked_websites
        WHERE LOWER(website)=?
        """,
        (website,)
    ).fetchone()

    if result:
        message = "❌ ACCESS BLOCKED"
        color = "danger"
        status = "Blocked"
    else:
        message = "✅ ACCESS ALLOWED"
        color = "success"
        status = "Allowed"

    # Save history
    conn.execute(
        """
        INSERT INTO history (website, status)
        VALUES (?, ?)
        """,
        (website, status)
    )

    conn.commit()

    # ---------------- Pagination ----------------
    page = 1
    per_page = 5

    total_websites = conn.execute(
        "SELECT COUNT(*) FROM blocked_websites"
    ).fetchone()[0]

    total_pages = max(1, math.ceil(total_websites / per_page))

    offset = (page - 1) * per_page

    websites = conn.execute(
        """
        SELECT *
        FROM blocked_websites
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (per_page, offset)
    ).fetchall()

    # ---------------- History ----------------
    history = conn.execute(
        """
        SELECT *
        FROM history
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    blocked_checks = conn.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE status='Blocked'
        """
    ).fetchone()[0]

    allowed_checks = conn.execute(
        """
        SELECT COUNT(*)
        FROM history
        WHERE status='Allowed'
        """
    ).fetchone()[0]

    total_checks = blocked_checks + allowed_checks

    conn.close()

    return render_template(
        "index.html",
        websites=websites,
        history=history,
        message=message,
        color=color,
        total_websites=total_websites,
        blocked_checks=blocked_checks,
        allowed_checks=allowed_checks,
        total_checks=total_checks,
        page=page,
        total_pages=total_pages
    )


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)