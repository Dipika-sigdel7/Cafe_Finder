from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="deepika@",
        database="Cafe_Finder"
    )


# ADMIN LOGIN ROUTE
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admins WHERE email = %s", 
            (email,)
        )

        admin = cursor.fetchone()

        if admin and check_password_hash(admin["password"], password):

            cursor.close()
            db.close()

            session["admin_id"] = admin["id"]

            return redirect(url_for("admin_dashboard"))
        
        else:
            error = "Invalid Email or Password"

        cursor.close()
        db.close()


    return render_template("admin_login.html", error=error)


#Review
@app.route("/cafe/<int:cafe_id>/review", methods=["POST"])
def submit_review(cafe_id):
    user_name = request.form['user_name']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO reviews (cafe_id, user_name, rating, comment, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (cafe_id, user_name, rating, comment)
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for('cafe_details', cafe_id=cafe_id))



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
    cursor.execute("SELECT user_name, comment, rating, created_at FROM reviews WHERE cafe_id=%s ORDER BY created_at DESC", (cafe_id,))
    reviews = cursor.fetchall()

    # Calculate average rating
    if reviews:
        avg_rating = round(sum(r['rating'] for r in reviews)/len(reviews), 1) 
    else:
        avg_rating=0
    cafe['rating'] = avg_rating

    cursor.close()
    db.close()

    return render_template("cafe_details.html", cafe=cafe, menu_items=menu_items, images=images, reviews=reviews)


# Admin Dashboard
@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    error = None

    db = get_db()
    cursor = db.cursor(dictionary=True)


    if request.method == "POST":

        name = request.form["name"].strip()
        description = request.form["description"].strip()
        location = request.form["location"].strip()
        open_time = request.form["open_time"].strip()
        close_time = request.form["close_time"].strip()


        cursor.execute(
            "SELECT id FROM cafes WHERE name=%s",
            (name,)
        )

        existing_cafe = cursor.fetchone()

        if existing_cafe:
            error = "A cafe with this name already exists."

        else:

            cursor.execute(
                """
                INSERT INTO cafes 
                (name, description, location, open_time, close_time)
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    name,
                    description,
                    location,
                    open_time,
                    close_time
                )
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

                    upload_folder = os.path.join(
                        app.static_folder,
                        "uploads"
                    )

                    os.makedirs(upload_folder, exist_ok=True)

                    filepath = os.path.join(
                        upload_folder,
                        filename
                    )

                    image.save(filepath)

                    print("SAVED FILE:", filepath)


                    cursor.execute(
                        """
                        INSERT INTO cafe_images
                        (cafe_id, image_path)
                        VALUES (%s,%s)
                        """,
                        (
                            cafe_id,
                            "uploads/" + filename
                        )
                    )

                    print("Inserted into cafe_images table")


            # Add menu items
            item_names = request.form.getlist("item_name[]")
            item_prices = request.form.getlist("item_price[]")
            item_categories = request.form.getlist("item_category[]")

            for item, price, category in zip(item_names, item_prices, item_categories):

                if item.strip() and price.strip():

                    cursor.execute("""
                        INSERT INTO menu_items
                        (cafe_id,item_name,category,price)
                        VALUES(%s,%s,%s,%s)
                        """,
                        (
                           (
                                cafe_id,
                                name,
                                price,
                                category
                            )  
                        ))

            db.commit()

            return redirect(url_for("admin_dashboard"))


    # Load existing cafes
    cursor.execute("SELECT * FROM cafes")
    cafes = cursor.fetchall()


    for cafe in cafes:

        cursor.execute(
            "SELECT * FROM menu_items WHERE cafe_id=%s",
            (cafe["id"],)
        )

        cafe["menu_items"] = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_dashboard.html",
        cafes=cafes,
        error=error
    )

#Delete
@app.route("/admin/delete_cafe/<int:cafe_id>")
def delete_cafe(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    db = get_db()
    cursor = db.cursor(dictionary=True)


    # Delete cafe
    cursor.execute(
        "DELETE FROM cafes WHERE id=%s",
        (cafe_id,)
    )


    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for("admin_dashboard")
    )


@app.route("/")
def home():


    db = get_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute("SELECT * FROM cafes")
 
    cafes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "index.html",
        cafes=cafes
    )

#update price
@app.route("/admin/update_price/<int:item_id>/<price>")
def update_price(item_id, price):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    db = get_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute("""
        UPDATE menu_items
        SET price=%s
        WHERE id=%s
    """,
    (
        price,
        item_id
    ))


    db.commit()


    cursor.execute(
        "SELECT cafe_id FROM menu_items WHERE id=%s",
        (item_id,)
    )

    result = cursor.fetchone()
    cafe_id = result["cafe_id"]

    cursor.close()
    db.close()

    return redirect(
        url_for(
            "manage_menu",
            cafe_id=cafe_id
        )
    )


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

        if 'cursor' in locals():
            cursor.close()
            db.close()

        return render_template(
            "admin_restore_password.html",
            message=message,
            error=error
        )


# Manage Menu
@app.route("/admin/manage_menu/<int:cafe_id>", methods=["GET", "POST"])
def manage_menu(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)


    # Get cafe information
    cursor.execute(
        "SELECT * FROM cafes WHERE id=%s",
        (cafe_id,)
    )

    cafe = cursor.fetchone()


    # Get menu items
    cursor.execute(
        "SELECT * FROM menu_items WHERE cafe_id=%s",
        (cafe_id,)
    )

    menu_items = cursor.fetchall()


    print("Cafe ID:", cafe_id)
    print("Cafe:", cafe)
    print("Items:", menu_items)


    cursor.close()

    cursor.close()
    db.close()

    return render_template(
        "manage_menu.html",
        cafe=cafe,
        menu_items=menu_items
    )
#Adding new items
@app.route("/admin/add_menu_item/<int:cafe_id>", methods=["POST"])
def add_menu_item(cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    item_name = request.form["item_name"]
    price = request.form["price"]


    db = get_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute("""
        INSERT INTO menu_items
        (cafe_id,item_name,price)
        VALUES(%s,%s,%s)
    """,
    (
        cafe_id,
        item_name,
        price
    ))


    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for(
            "manage_menu",
            cafe_id=cafe_id
        )
    )


#Delete menu item
@app.route("/admin/delete_menu_item/<int:item_id>/<int:cafe_id>")
def delete_menu_item(item_id,cafe_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))


    db = get_db()
    cursor = db.cursor(dictionary=True)


    cursor.execute(
        """
        DELETE FROM menu_items
        WHERE id=%s
        """,
        (item_id,)
    )


    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for(
            "manage_menu",
            cafe_id=cafe_id
        )
    )


#Cafes
@app.route('/cafes')
def cafes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM cafes ORDER BY name")
    all_cafes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("cafes.html", cafes=all_cafes)



#Search Cafe
@app.route("/search_cafe")
def search_cafe():
    cafe_name = request.args.get("name", "").strip()
    
    if not cafe_name:
        return{"found":False}
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM cafes WHERE name LIKE %s", (f"%{cafe_name}%",))
    cafe = cursor.fetchone()

    if cafe:
        result= {"found": True, "cafe_id": cafe["id"]}
    else:
        result= {"found": False}

    cursor.close()
    db.close()

    return result   


# Edit Cafe Details
@app.route('/admin/edit_cafe/<int:cafe_id>', methods=['GET','POST'])
def edit_cafe(cafe_id):

    conn = get_db()
    cursor = conn.cursor(dictionary=True)


    if request.method == "POST":


        # Update cafe details
        name = request.form['name']
        description = request.form['description']
        location = request.form['location']
        open_time = request.form['open_time']
        close_time = request.form['close_time']


        cursor.execute("""
        UPDATE cafes
        SET name=%s,
            description=%s,
            location=%s,
            open_time=%s,
            close_time=%s
        WHERE id=%s
        """,
        (
            name,
            description,
            location,
            open_time,
            close_time,
            cafe_id
        ))



        # Delete selected images

        delete_images = request.form.getlist("delete_images")


        for img_id in delete_images:


            cursor.execute(
            """
            SELECT image_path 
            FROM cafe_images
            WHERE id=%s
            """,
            (img_id,)
            )

            img = cursor.fetchone()


            if img:

                filepath = os.path.join(
                    app.static_folder,
                    img['image_path']
                )


                if os.path.exists(filepath):
                    os.remove(filepath)



                cursor.execute(
                """
                DELETE FROM cafe_images
                WHERE id=%s
                """,
                (img_id,)
                )



        # Add new multiple images

        new_images = request.files.getlist("new_images")


        for image in new_images:


            if image.filename:


                filename = secure_filename(image.filename)


                upload_folder = os.path.join(
                    app.static_folder,
                    "uploads"
                )


                os.makedirs(
                    upload_folder,
                    exist_ok=True
                )


                image.save(
                    os.path.join(
                        upload_folder,
                        filename
                    )
                )


                cursor.execute(
                """
                INSERT INTO cafe_images
                (cafe_id,image_path)
                VALUES(%s,%s)
                """,
                (
                    cafe_id,
                    "uploads/"+filename
                )
                )



        conn.commit()


        return redirect(
            url_for('admin_dashboard')
        )



    # GET request

    cursor.execute(
    "SELECT * FROM cafes WHERE id=%s",
    (cafe_id,)
    )

    cafe = cursor.fetchone()



    cursor.execute(
    """
    SELECT * FROM cafe_images
    WHERE cafe_id=%s
    """,
    (cafe_id,)
    )

    images = cursor.fetchall()



    return render_template(
        "edit_cafe.html",
        cafe=cafe,
        images=images
    )
    
# LOGOUT
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)