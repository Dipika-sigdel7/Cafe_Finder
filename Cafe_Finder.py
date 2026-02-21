from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Connection
db = mysql.connector.connect(
    host="localhost", user="root", password="deepika@", database="Cafe_Finder"
)


# ADMIN LOGIN ROUTE
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["id"]
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid Email or Password"

    return render_template("admin_login.html", error=error)


@app.route("/cafe/<int:cafe_id>/review", methods=["POST"])
def submit_review(cafe_id):
    user_name = request.form['user_name']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reviews (cafe_id, user_name, rating, comment, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (cafe_id, user_name, rating, comment)
    )
    db.commit()
    return redirect(url_for('cafe_details', cafe_id=cafe_id))



@app.route("/cafe/<int:cafe_id>")
def cafe_details(cafe_id):
    cursor = db.cursor(dictionary=True)

    # Fetch cafe info
    cursor.execute("SELECT * FROM cafes WHERE id=%s", (cafe_id,))
    cafe = cursor.fetchone()
    if not cafe:
        return "Cafe not found", 404

    # Fetch menu items
    cursor.execute("SELECT * FROM menu_items WHERE cafe_id=%s", (cafe_id,))
    menu_items = cursor.fetchall()

    # Fetch images
    cursor.execute("SELECT * FROM cafe_images WHERE cafe_id=%s", (cafe_id,))
    images = cursor.fetchall()

    # Fetch public reviews
    cursor.execute("SELECT user_name, comment, rating, created_at FROM reviews WHERE cafe_id=%s ORDER BY created_at DESC", (cafe_id,))
    reviews = cursor.fetchall()

    # Calculate average rating
    if reviews:
        avg_rating = round(sum(r['rating'] for r in reviews)/len(reviews), 1) 
    else:
        avg_rating=0
    cafe['rating'] = avg_rating

    return render_template("cafe_details.html", cafe=cafe, menu_items=menu_items, images=images, reviews=reviews)


# Admin Dashboard
@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    error = None

    if request.method == "POST":
        # Get cafe info
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        location = request.form["location"].strip()
        open_time = request.form["open_time"].strip()
        close_time = request.form["close_time"].strip()

        cursor = db.cursor(dictionary=True)

        # Check if cafe already exists (prevents duplicates)
        cursor.execute("SELECT id FROM cafes WHERE name=%s", (name,))
        existing_cafe = cursor.fetchone()
        if existing_cafe:
            error = "A cafe with this name already exists."
            return render_template("admin_dashboard.html", error=error)

        # Insert cafe into DB
        cursor.execute(
            """
            INSERT INTO cafes (name, description, location, open_time, close_time)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, description, location, open_time, close_time),
        )
        db.commit()
        cafe_id = cursor.lastrowid

        # Handle menu items
        item_names = request.form.getlist("item_name[]")
        item_prices = request.form.getlist("item_price[]")
        for item, price in zip(item_names, item_prices):
            if item.strip() and price.strip():
                cursor.execute(
                    """
                    INSERT INTO menu_items (cafe_id, item_name, price)
                    VALUES (%s, %s, %s)
                    """,
                    (cafe_id, item.strip(), price.strip()),
                )
        db.commit()

        # Handle images (optional)
        if "images" in request.files:
            images = request.files.getlist("images")
            for image in images:
                if image.filename:
                    filepath = f"static/uploads/{image.filename}"
                    image.save(filepath)
                    cursor.execute(
                        """
                        INSERT INTO cafe_images (cafe_id, image_path)
                        VALUES (%s, %s)
                        """,
                        (cafe_id, filepath),
                    )
        db.commit()

        # Redirect after POST to prevent resubmission
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_dashboard.html", error=None)


@app.route("/")
def home():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cafes")
    cafes = cursor.fetchall()

    return render_template("index.html", cafes=cafes)

# password restore
@app.route("/admin/restore-password", methods=["GET", "POST"])
def admin_restore_password():
    message = None
    error = None

    if request.method == "POST":
        email = request.form["email"]

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE email=%s", (email,))
        admin = cursor.fetchone()

        if admin:
            # Here you would generate a reset token or link
            # For simplicity, let's just show a message
            message = "A password reset link has been sent to your email."
            # TODO: send actual email with token/link
        else:
            error = "Email not found."

    return render_template("admin_restore_password.html")


# Manage Menu
@app.route("/admin/manage_menu/<int:cafe_id>", methods=["GET", "POST"])
def manage_menu(cafe_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    cursor = db.cursor(dictionary=True)
# Fetch cafe info
    cursor.execute("SELECT * FROM cafes WHERE id=%s", (cafe_id,))
    cafe = cursor.fetchone()

# Fetch menu items
    cursor.execute("SELECT * FROM menu_items WHERE cafe_id=%s", (cafe_id,))
    menu_items = cursor.fetchall()

    if request.method == "POST":
# Update existing menu item
        for item_id, name, price in zip(request.form.getlist("item_id[]"),
                                        request.form.getlist("item_name[]"),
                                        request.form.getlist("item_price[]")):
            cursor.execute(
                "UPDATE menu_items SET item_name=%s, price=%s WHERE id=%s",
                (name, price, item_id)
            )
        db.commit()
        return redirect(url_for("manage_menu", cafe_id=cafe_id))
    return render_template("manage_menu.html", cafe=cafe, menu_items=menu_items)


@app.route('/cafes')
def cafes():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM cafes ORDER BY name")
    all_cafes = cursor.fetchall()
    cursor.close()
    return render_template("cafes.html", cafes=all_cafes)


@app.route("/search_cafe")
def search_cafe():
    cafe_name = request.args.get("name", "").strip()
    
    if not cafe_name:
        return{"found":False}
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM cafes WHERE name LIKE %s", (f"%{cafe_name}%",))
    cafe = cursor.fetchone()

    if cafe:
        return {"found": True, "cafe_id": cafe["id"]}
    else:
        return {"found": False}
    
# LOGOUT
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)
