from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from google import genai

load_dotenv()


app = Flask(__name__)
app.secret_key = "cafe-finder-secret-key"

# 1. We use the new genai.Client and your copied API key
# Gemini AI client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


# Database Connection
def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="deepika@", database="Cafe_Finder"
    )


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        if not login_input or not password_input:
            return render_template( "login.html", error="Username/Email and password are required." )

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE username = %s OR email = %s
                """,
                (login, login),
            )

            user = cursor.fetchone()

            # Verify user exists AND the password matches the hash
            if user and check_password_hash(user["password"], password):

                # Log the user in by saving their ID in the session
                session["user_id"] = user["id"]
                session["username"] = user["username"]

                # Redirect to your home page or dashboard after logging in
                return redirect(url_for('home')) # Change 'home' to your actual main page route name

            else:
                return render_template("login.html", error="Invalid username/email or password.")

        except Exception as e:
            print("Login error:", e)
            return render_template("login.html", error="An error occurred. Please try again.")

        finally:
            cursor.close()
            db.close()

    # If it's a GET request, just show the login page
    return render_template("login.html")

# =========================================================
# REGISTER
# =========================================================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Required fields
        if (
            not name
            or not username
            or not email
            or not password
            or not confirm_password
        ):
            return render_template("register.html", error="All fields are required.")

        # Password confirmation
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:

            # Check existing username/email
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE username = %s OR email = %s
                """,
                (username, email),
            )

            if cursor.fetchone():
                return render_template(
                    "register.html", error="Username or email already exists."
                )

            # Hash password
            hashed_password = generate_password_hash(password)

            # Create account
            cursor.execute(
                """
                INSERT INTO users
                (name, username, email, password)
                VALUES (%s, %s, %s, %s)
                """,
                (name, username, email, hashed_password),
            )

            db.commit()

            # CREATE FLASH MESSAGE
            flash("Account created successfully. Please login.", "success")

            # Go to existing login page
            return redirect(url_for("login"))

        except Exception as e:

            db.rollback()

            print("Registration error:", e)

            return render_template(
                "register.html", error="Registration failed. Please try again."
            )

        finally:

            cursor.close()
            db.close()

    return render_template("register.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":

        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        # Check empty fields
        if not login or not password:
            return render_template(
                "admin_login.html",
                error="Username/Email and password are required."
            )

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:

            # Find ADMIN by username OR email
            cursor.execute(
                """
                SELECT id, username, email, password
                FROM admins
                WHERE username = %s OR email = %s
                LIMIT 1
                """,
                (login, login)
            )

            admin = cursor.fetchone()

            # Check admin and password
            if admin and check_password_hash(
                admin["password"],
                password
            ):

                # Store ADMIN session
                session["admin_id"] = admin["id"]
                session["admin_username"] = admin["username"]

                # Login successful
                return redirect(
                    url_for("admin_dashboard")
                )

            else:

                error = "Invalid Username/Email or Password."

        except Exception as e:

            print("Admin login error:", e)

            error = "Login failed. Please try again."

        finally:

            cursor.close()
            db.close()

    return render_template(
        "admin_login.html",
        error=error
    )


# Review
@app.route("/cafe/<int:cafe_id>/review", methods=["POST"])
def submit_review(cafe_id):

    db = get_db()
    cursor = db.cursor()

    user_name = request.form["user_name"]
    rating = request.form["rating"]
    comment = request.form["comment"]

    image_path = None

    if "review_image" in request.files:

        file = request.files["review_image"]

        if file.filename != "":

            filename = secure_filename(file.filename)
            upload_folder = "static/uploads"

            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))

            image_path = "uploads/" + filename

    cursor.execute(
        """
        INSERT INTO reviews
        (cafe_id,user_name,rating,comment,image_path)
        VALUES(%s,%s,%s,%s,%s)
    """,
        (cafe_id, user_name, rating, comment, image_path),
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("cafe_details", cafe_id=cafe_id))


# Cafe Details
@app.route("/cafe/<int:cafe_id>")
def cafe_details(cafe_id):
    db = get_db()
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
    cursor.execute(
        "SELECT user_name, comment, rating, created_at, image_path FROM reviews WHERE cafe_id=%s ORDER BY created_at DESC",
        (cafe_id,),
    )
    reviews = cursor.fetchall()

    # Calculate average rating
    if reviews:
        avg_rating = round(sum(int(r["rating"]) for r in reviews) / len(reviews), 1)
    else:
        avg_rating = 0
    cafe["rating"] = avg_rating
    from datetime import datetime

    if cafe["open_time"]:
        cafe["open_time"] = datetime.strptime(
            str(cafe["open_time"]), "%H:%M:%S"
        ).strftime("%I:%M %p")

    if cafe["close_time"]:
        cafe["close_time"] = datetime.strptime(
            str(cafe["close_time"]), "%H:%M:%S"
        ).strftime("%I:%M %p")
    cursor.close()
    db.close()

    return render_template(
        "cafe_details.html",
        cafe=cafe,
        menu_items=menu_items,
        images=images,
        reviews=reviews,
    )

# Admin pop-up manager
@app.route("/admin/popups")
def admin_popups():

    # -----------------------------------------
    # check whether admin is logged in
    # -----------------------------------------

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )


    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    db = get_db()

    if db is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    cursor = db.cursor(
        dictionary=True
    )


    try:

        # -------------------------------------
        # GET NOTIFICATIONS
        # -------------------------------------

        cursor.execute("""
            SELECT
                n.id,
                n.cafe_id,
                n.type,
                n.title,
                n.message,
                n.discount_percent,
                n.button_text,
                n.button_url,
                n.image_url,
                n.start_date,
                n.end_date,
                n.is_active,
                n.show_popup,
                n.created_at,
                c.name AS cafe_name

            FROM notifications n

            LEFT JOIN cafes c
                ON n.cafe_id = c.id

            ORDER BY n.created_at DESC
        """)

        notifications = cursor.fetchall()


        # -------------------------------------
        # GET CAFES
        # -------------------------------------

        cursor.execute("""
            SELECT
                id,
                name
            FROM cafes
            ORDER BY name
        """)

        cafes = cursor.fetchall()


        # -------------------------------------
        # OPEN pop-up manager page
        # -------------------------------------

        return render_template(
            "admin_popups.html",
            notifications=notifications,
            cafes=cafes
        )


    except Error as error:

        print(
            "Popup loading error:",
            error
        )

        flash(
            "Unable to load popup manager.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        cursor.close()
        db.close()

#  Add the create popup Flask route
@app.route(
    "/admin/popups/create",
    methods=["POST"]
)
def admin_create_popup():

    # -----------------------------------------
    # SECURITY CHECK
    # -----------------------------------------

    if "admin_id" not in session:

        return redirect(
            url_for("admin_login")
        )


    # -----------------------------------------
    # GET FORM DATA
    # -----------------------------------------

    cafe_id = request.form.get(
        "cafe_id"
    )

    popup_type = request.form.get(
        "type"
    )

    title = request.form.get(
        "title",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()

    discount_percent = request.form.get(
        "discount_percent"
    )

    button_text = request.form.get(
        "button_text",
        ""
    ).strip()

    button_url = request.form.get(
        "button_url",
        ""
    ).strip()

    start_date = request.form.get(
        "start_date"
    )

    end_date = request.form.get(
        "end_date"
    )


    # -----------------------------------------
    # CHECKBOXES
    # -----------------------------------------

    is_active = 1 if request.form.get(
        "is_active"
    ) else 0


    show_popup = 1 if request.form.get(
        "show_popup"
    ) else 0


    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    if not title:

        flash(
            "Popup title is required.",
            "error"
        )

        return redirect(
            url_for("admin_popups")
        )


    if not message:

        flash(
            "Popup message is required.",
            "error"
        )

        return redirect(
            url_for("admin_popups")
        )


    if not popup_type:

        flash(
            "Popup type is required.",
            "error"
        )

        return redirect(
            url_for("admin_popups")
        )


    # -----------------------------------------
    # EMPTY VALUES
    # -----------------------------------------

    if cafe_id == "":

        cafe_id = None


    if discount_percent == "":

        discount_percent = None


    if end_date == "":

        end_date = None


    if button_text == "":

        button_text = None


    if button_url == "":

        button_url = None


    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    db = get_db()

    if db is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("admin_popups")
        )


    cursor = db.cursor()


    try:

        cursor.execute(
            """
            INSERT INTO notifications
            (
                cafe_id,
                type,
                title,
                message,
                discount_percent,
                button_text,
                button_url,
                start_date,
                end_date,
                is_active,
                show_popup
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,

            (
                cafe_id,
                popup_type,
                title,
                message,
                discount_percent,
                button_text,
                button_url,
                start_date,
                end_date,
                is_active,
                show_popup
            )
        )


        db.commit()


        flash(
            "Popup created successfully!",
            "success"
        )


    except Error as error:

        db.rollback()

        print(
            "Create popup error:",
            error
        )

        flash(
            "Failed to create popup.",
            "error"
        )


    finally:

        cursor.close()
        db.close()


    return redirect(
        url_for("admin_popups")
    )

# Reservation
@app.route("/reservation/<int:cafe_id>", methods=["POST"])
def reservation(cafe_id):

    db = get_db()
    cursor = db.cursor()

    name = request.form["customer_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    reservation_date = request.form["reservation_date"]
    time = request.form["reservation_time"]
    people = request.form["people"]
    message = request.form["message"]

    cursor.execute(
        """
    INSERT INTO reservations
    (cafe_id,customer_name,email,phone,reservation_date,reservation_time,people,message)

    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)

    """,
        (cafe_id, name, email, phone, reservation_date, time, people, message),
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("cafe_details", cafe_id=cafe_id))


# Admin Dashboard
@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    error = None

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        # Cafe Information
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        location = request.form["location"].strip()
        phone=request.form["phone"].strip()
        open_time = request.form["open_time"].strip()
        close_time = request.form["close_time"].strip()
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        # Payment Form
        esewa_account = request.form.get("esewa_account")
        khalti_account = request.form.get("khalti_account")
        # QR Files
        esewa_qr = request.files.get("esewa_qr")
        khalti_qr = request.files.get("khalti_qr")

        esewa_path = None
        khalti_path = None

        # Save eSewa QR

        if esewa_qr and esewa_qr.filename:

            esewa_filename = secure_filename(esewa_qr.filename)

            esewa_qr.save("static/uploads/" + esewa_filename)

            esewa_path = "uploads/" + esewa_filename

        # Save Khalti QR

        if khalti_qr and khalti_qr.filename:

            khalti_filename = secure_filename(khalti_qr.filename)

            khalti_qr.save("static/uploads/" + khalti_filename)

            khalti_path = "uploads/" + khalti_filename
            # Check Duplicate Cafe
        cursor.execute("SELECT id FROM cafes WHERE name=%s", (name,))

        existing_cafe = cursor.fetchone()

        if existing_cafe:
            error = "A cafe with this name already exists."

        else:
            # Insert Cafe
            cursor.execute(
                """
                INSERT INTO cafes 
                (name, description, location, open_time, close_time,latitude,longitude,esewa_account,khalti_account,esewa_qr,khalti_qr)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    name,
                    description,
                    location,
                    phone,
                    open_time,
                    close_time,
                    latitude,
                    longitude,
                    esewa_account,
                    khalti_account,
                    esewa_path,
                    khalti_path,
                ),
            )

            db.commit()

            cafe_id = cursor.lastrowid

            # Upload cafe images
            images = request.files.getlist("images")

            print("==============================")
            print("FILES:", request.files)
            print("IMAGE LIST:", images)
            print("IMAGE COUNT:", len(images))
            print("==============================")

            for image in images:

                print("PROCESSING IMAGE:", image.filename)

                if image.filename:

                    filename = secure_filename(image.filename)

                    print("SECURE NAME:", filename)

                    upload_folder = os.path.join(app.static_folder, "uploads")

                    os.makedirs(upload_folder, exist_ok=True)

                    filepath = os.path.join(upload_folder, filename)

                    image.save(filepath)

                    print("SAVED FILE:", filepath)

                    cursor.execute(
                        """
                        INSERT INTO cafe_images
                        (cafe_id, image_path)
                        VALUES (%s,%s)
                        """,
                        (cafe_id, "uploads/" + filename),
                    )

                    print("Inserted into cafe_images table")

            # Add menu items
            item_names = request.form.getlist("item_name[]")
            item_prices = request.form.getlist("item_price[]")
            item_categories = request.form.getlist("item_category[]")

            for item, price, category in zip(item_names, item_prices, item_categories):

                if item.strip() and price.strip():

                    cursor.execute(
                        """
                        INSERT INTO menu_items
                        (cafe_id,item_name,category,price)
                        VALUES(%s,%s,%s,%s)
                        """,
                        (cafe_id, item, category, price),
                    )
            db.commit()

            return redirect(url_for("admin_dashboard"))

            # save images
            if esewa_qr:

                esewa_filename = secure_filename(esewa_qr.filename)

                esewa_qr.save("static/uploads/" + esewa_filename)

            if khalti_qr:

                khalti_filename = secure_filename(khalti_qr.filename)

                khalti_qr.save("static/uploads/" + khalti_filename)

    # Load existing cafes
    cursor.execute("SELECT * FROM cafes")
    cafes = cursor.fetchall()

    for cafe in cafes:

        cursor.execute("SELECT * FROM menu_items WHERE cafe_id=%s", (cafe["id"],))

        cafe["menu_items"] = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin_dashboard.html", cafes=cafes, error=error)


# Delete
@app.route("/admin/delete_cafe/<int:cafe_id>")
def delete_cafe(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Delete cafe
    cursor.execute("DELETE FROM cafes WHERE id=%s", (cafe_id,))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("admin_dashboard"))


# Front Landing Page
@app.route("/")
def front():
    return render_template("front.html")



# for service
@app.route("/admin/add_service", methods=["POST"])
def add_service():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    cafe_id = request.form.get("cafe_id")
    service_name = request.form.get("service_name")
    service_description = request.form.get("service_description")
    service_icon = request.form.get("service_icon")

    if not cafe_id or not service_name or not service_description:
        flash("Please fill all required service fields.", "error")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO cafe_services
        (
            cafe_id,
            service_name,
            service_description,
            service_icon
        )
        VALUES (%s, %s, %s, %s)
    """, (
        cafe_id,
        service_name,
        service_description,
        service_icon
    ))

    db.commit()
    cursor.close()
    db.close()

    flash("Service added successfully.", "success")

    return redirect(url_for("admin_dashboard"))


# Cafe Home Page
@app.route("/home")
def home():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cafes")
    cafes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("index.html", cafes=cafes)



# =========================================================
#   AI CAFE ASSISTANT ROUTE
# =========================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"reply": "Please type a question about our cafes!"})

        msg_lower = user_message.lower()

        # 1. Instant greeting responses
        greetings = ["hello", "hi", "hey", "hola", "hi there", "hello there"]
        if msg_lower in greetings or msg_lower.startswith(("hi ", "hello ")):
            return jsonify({"reply": "Hi! How may I help you find the best cafe today?"})

        # 2. Your Cafe Data (The AI uses this to give accurate answers)
        cafe_database_info = """
        AVAILABLE CAFES:
        1. Brew & Bite:
           - Location: Downtown Mall
           - Timings: 8:00 AM - 8:00 PM
           - Discounts: 10% student discount with student ID.
           - Popular Items: Caramel Latte, Cappuccino, Butter Croissants, Brownies.
           
        2. The Roastery:
           - Location: Uptown High Street
           - Timings: 7:00 AM - 10:00 PM
           - Discounts: Buy 1 Get 1 Free on all Iced Coffees every Friday.
           - Popular Items: Pour-over Espresso, Cold Brew, Club Sandwiches, New York Cheesecake.
           
        3. Midnight Mocha:
           - Location: University Avenue
           - Timings: Open 24/7
           - Discounts: Free chocolate chip cookie with any large mocha order.
           - Popular Items: Dark Chocolate Mocha, Hot Chocolate, Paninis, Energy Smoothies.
        """

        prompt = f"""
        You are 'Cafe Finder AI', an expert assistant for our cafe discovery platform.
        Answer the user's question accurately, concisely, and warmly based ONLY on the following cafe data:

        {cafe_database_info}

        User Question: {user_message}
        """

        # 3. Ask Gemini AI for a dynamic response
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            if response and response.text:
                return jsonify({"reply": response.text.strip()})
        except Exception as ai_err:
            print("Gemini API issue (using smart fallback):", ai_err)

        # 4. Smart Fallback (Guarantees an answer if the API key fails)
        if any(w in msg_lower for w in ["discount", "offer", "deal", "cheap"]):
            return jsonify({
                "reply": "Here are our active offers:\n• Brew & Bite: 10% student discount.\n• The Roastery: Buy 1 Get 1 Free on Iced Coffees on Fridays.\n• Midnight Mocha: Free cookie with large mochas!"
            })
        elif any(w in msg_lower for w in ["open", "time", "hours", "late"]):
            return jsonify({
                "reply": "'Midnight Mocha' is open 24/7! 'The Roastery' is open 7 AM – 10 PM, and 'Brew & Bite' is open 8 AM – 8 PM."
            })
        elif any(w in msg_lower for w in ["drink", "coffee", "menu", "food"]):
            return jsonify({
                "reply": "Popular drinks include Caramel Lattes at Brew & Bite, Cold Brew at The Roastery, and Dark Chocolate Mochas at Midnight Mocha."
            })
        elif any(w in msg_lower for w in ["best", "explore", "recommend"]):
            return jsonify({
                "reply": "For artisan coffee, visit 'The Roastery'. For late-night study sessions, 'Midnight Mocha' (open 24/7) is the top choice!"
            })
        else:
            return jsonify({
                "reply": "I can help you find open cafes, check special discounts, or explore menus. What are you looking for?"
            })

    except Exception as e:
        print("Chat Error:", e)
        return jsonify({"reply": "Hi! How may I help you explore cafes today?"})


# About Page
@app.route("/about")
def about():
    return render_template("about.html")


# contact
@app.route("/contact")
def contact():
    return render_template("contact.html")


# update price
@app.route("/admin/update_price/<int:item_id>/<price>")
def update_price(item_id, price):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        UPDATE menu_items
        SET price=%s
        WHERE id=%s
    """,
        (price, item_id),
    )

    db.commit()

    cursor.execute("SELECT cafe_id FROM menu_items WHERE id=%s", (item_id,))

    result = cursor.fetchone()
    cafe_id = result["cafe_id"]

    cursor.close()
    db.close()

    return redirect(url_for("manage_menu", cafe_id=cafe_id))


#  Admin password restore
@app.route("/admin/restore-password", methods=["GET", "POST"])
def admin_restore_password():
    message = None
    error = None

    if request.method == "POST":
        email = request.form["email"]

        db = get_db()
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

        if "cursor" in locals():
            cursor.close()
            db.close()

        return render_template(
            "admin_restore_password.html", message=message, error=error
        )


# Manage Menu
@app.route("/admin/manage_menu/<int:cafe_id>", methods=["GET", "POST"])
def manage_menu(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get cafe information
    cursor.execute("SELECT * FROM cafes WHERE id=%s", (cafe_id,))

    cafe = cursor.fetchone()

    # Get menu items
    cursor.execute("SELECT * FROM menu_items WHERE cafe_id=%s", (cafe_id,))

    menu_items = cursor.fetchall()

    print("Cafe ID:", cafe_id)
    print("Cafe:", cafe)
    print("Items:", menu_items)

    cursor.close()

    cursor.close()
    db.close()

    return render_template("manage_menu.html", cafe=cafe, menu_items=menu_items)


# Adding new items
@app.route("/admin/add_menu_item/<int:cafe_id>", methods=["POST"])
def add_menu_item(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    item_name = request.form["item_name"]
    price = request.form["price"]

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        INSERT INTO menu_items
        (cafe_id,item_name,price)
        VALUES(%s,%s,%s)
    """,
        (cafe_id, item_name, price),
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("manage_menu", cafe_id=cafe_id))


# Delete menu item
@app.route("/admin/delete_menu_item/<int:item_id>/<int:cafe_id>")
def delete_menu_item(item_id, cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        DELETE FROM menu_items
        WHERE id=%s
        """,
        (item_id,),
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("manage_menu", cafe_id=cafe_id))


# Cafes
@app.route("/cafes")
def cafes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM cafes ORDER BY name")
    all_cafes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("cafes.html", cafes=all_cafes)


# Search Cafe
@app.route("/search_cafe")
def search_cafe():
    cafe_name = request.args.get("name", "").strip()

    if not cafe_name:
        return {"found": False}

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM cafes WHERE name LIKE %s", (f"%{cafe_name}%",))
    cafe = cursor.fetchone()

    if cafe:
        result = {"found": True, "cafe_id": cafe["id"]}
    else:
        result = {"found": False}

    cursor.close()
    db.close()

    return result


# Edit Cafe Details
@app.route("/admin/edit_cafe/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        # Update cafe details
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        open_time = request.form["open_time"]
        close_time = request.form["close_time"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]

        cursor.execute(
            """
        UPDATE cafes
        SET name=%s,
            description=%s,
            location=%s,
            open_time=%s,
            close_time=%s,
            latitude=%s,
            longitude=%s
        WHERE id=%s
        """,
            (
                name,
                description,
                location,
                open_time,
                close_time,
                latitude,
                longitude,
                cafe_id,
            ),
        )

        # Delete selected images

        delete_images = request.form.getlist("delete_images")

        for img_id in delete_images:

            cursor.execute(
                """
            SELECT image_path 
            FROM cafe_images
            WHERE id=%s
            """,
                (img_id,),
            )

            img = cursor.fetchone()

            if img:

                filepath = os.path.join(app.static_folder, img["image_path"])

                if os.path.exists(filepath):
                    os.remove(filepath)

                cursor.execute(
                    """
                DELETE FROM cafe_images
                WHERE id=%s
                """,
                    (img_id,),
                )

        # Add new multiple images

        new_images = request.files.getlist("new_images")

        for image in new_images:

            if image.filename:

                filename = secure_filename(image.filename)

                upload_folder = os.path.join(app.static_folder, "uploads")

                os.makedirs(upload_folder, exist_ok=True)

                image.save(os.path.join(upload_folder, filename))

                cursor.execute(
                    """
                INSERT INTO cafe_images
                (cafe_id,image_path)
                VALUES(%s,%s)
                """,
                    (cafe_id, "uploads/" + filename),
                )

        conn.commit()

        return redirect(url_for("admin_dashboard"))

    # GET request

    cursor.execute("SELECT * FROM cafes WHERE id=%s", (cafe_id,))

    cafe = cursor.fetchone()

    cursor.execute(
        """
    SELECT * FROM cafe_images
    WHERE cafe_id=%s
    """,
        (cafe_id,),
    )

    images = cursor.fetchall()

    return render_template("edit_cafe.html", cafe=cafe, images=images)


# LOGOUT
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
