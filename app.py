import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import (
    generate_password_hash, check_password_hash)
from werkzeug.utils import secure_filename
# Check if the file env.py exists
if os.path.exists("env.py"):
    import env


# Create an instance of Flask
app = Flask(__name__)


# Configure MongoDB settings
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
# Set secret key for session management
app.secret_key = os.environ.get("SECRET_KEY")


# Initialize PyMongo
mongo = PyMongo(app)


# Home route
@app.route("/")
@app.route("/home")
def home():

    return render_template("home.html")


# Search route
@app.route("/search", methods=["GET", "POST"])
def search():

    query = request.form.get("query")
    posts = list(mongo.db.posts.find({"$text": {"$search": query}}))
    return render_template("community.html", posts=posts)


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # check if username is already in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        # if username already exists in database
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        # normalize the email address before querying the database
        normalized_email = request.form.get("email_address").lower().strip()
        # check if email address is already in the database
        existing_email = mongo.db.users.find_one(
            {"email_address": normalized_email})

        # if email address already exists in the database
        if existing_email:
            flash("Email Address already exists")
            return redirect(url_for("register"))
        # check if user passwords match
        if request.form.get("password") != request.form.get(
                "confirm_password"):
            flash("Passwords do not Match")
            return redirect(url_for("register"))

        # create a new user
        register = {
            "username": request.form.get("username").lower(),
            "email_address": request.form.get("email_address"),
            "dob": request.form.get("dob"),
            "password": generate_password_hash(request.form.get("password")),
            "profile_bio": request.form.get("profile_bio")
        }

        mongo.db.users.insert_one(register)

        # put the new user into session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful !")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in the database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Username or Password is incorrect")
                return redirect(url_for("login"))

        else:
            # if there is not an existing user in the database
            flash("Username or Password is incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


# Logout route
@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("See You Soon")
    session.pop("user")
    return redirect(url_for("login"))


# Add workout route
@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if session.get('user'):
        if request.method == "POST":
            # retrieve data from the form
            workout_category = request.form.get("workout_category")
            workout_title = request.form.get("workout_title")
            workout_description = request.form.get("workout_description")
            rpe_scale = request.form.get("rpe_scale")
            profile_by = session["user"]
            date_posted = datetime.now().strftime("%d %B, %Y")
            like_count = 0

            # Fetch the workout image corresponding to the selected category
            workout_image = mongo.db.workouts.find_one(
                {'workout_category': workout_category})['workout_image']

            # Create a new workout post
            workout_post = {
                "workout_category": workout_category,
                "workout_title": workout_title,
                "workout_description": workout_description,
                "rpe_scale": rpe_scale,
                "profile_by": profile_by,
                "date_posted": date_posted,
                "workout_image": workout_image,
                "like_count": like_count}

            mongo.db.posts.insert_one(workout_post)
            flash("Post Successfully Added")
            return redirect(url_for("profile", username=session["user"]))

        workouts = mongo.db.workouts.find()
        return render_template("add_post.html", workouts=workouts)
    else:
        flash("Please Log In")
        return redirect(url_for('login'))


# Edit workout route
@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if session['user'] == post['profile_by']:
        if request.method == "POST":
            # Retrieve updated data from the form
            edited_workout = {
                "workout_category": request.form.get("workout_category"),
                "workout_title": request.form.get("workout_title"),
                "workout_description": request.form.get("workout_description"),
                "rpe_scale": request.form.get("rpe_scale"),
                "profile_by": session["user"],
                "date_posted": datetime.now().strftime("%d %B, %Y"),
                "like_count": 0
            }
            # Fetch the workout image corresponding to the updated category
            workout_image = mongo.db.workouts.find_one(
                    {'workout_category':
                        edited_workout["workout_category"]})['workout_image']

            edited_workout['workout_image'] = workout_image
            # Update the workout post
            mongo.db.posts.update_one(
                {"_id": ObjectId(post_id)}, {"$set": edited_workout})
            flash("Post Successfully Updated")
            return redirect(url_for("profile", username=session["user"]))

        current_rpe_scale = request.form.get("rpe_scale")
        workouts = mongo.db.workouts.find()
        return render_template(
            "edit_post.html", workouts=workouts,
            current_rpe_scale=current_rpe_scale, post=post)
    else:
        flash("You are not the owner of the post")
        return redirect(url_for('community'))


# Delete workout route
@app.route("/delete_post/<post_id>")
def delete_post(post_id):

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    if not session.get("user"):
        flash("You are not logged in.")
        return redirect(url_for("login"))
    if session.get("user") != post[
            "profile_by"] and session.get("user") != "admin":
        flash("You are not allowed to delete this post.")
        return redirect(url_for("community"))

    if session.get("user") != "admin":
        mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
        flash("Post Successfully Removed")
        return redirect(url_for("profile", username=session["user"]))
    else:
        mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
        flash("Post Successfully Removed")
        return redirect(url_for("community"))


# Profile route
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if 'user' in session:

        # grab the sessions user's username from the database
        user = mongo.db.users.find_one(
                {"username": session["user"]})
        posts = list(mongo.db.posts.find())
        # Update posts with workout images
        for post in posts:
            workout_category = post['workout_category']
            workout_image = mongo.db.workouts.find_one(
                    {"workout_category": workout_category})["workout_image"]
            post['workout_image'] = workout_image

            return render_template(
                "profile.html", username=username, user=user, posts=posts)
    else:
        flash("Please log in to view this page")
        return redirect(url_for('login'))


# Community route
@app.route("/community")
def community():
    if session.get('user'):
        posts = list(mongo.db.posts.find())
        for post in posts:
            workout_category = post['workout_category']
            workout_image = mongo.db.workouts.find_one(
                {"workout_category": workout_category})["workout_image"]
            post['workout_image'] = workout_image
        return render_template("community.html", posts=posts)
    else:
        flash("Please Log In")
        return redirect(url_for('login'))


# Workout Categories route
@app.route("/workout_categories")
def workout_categories():

    workouts = list(mongo.db.workouts.find())
    return render_template("workout_categories.html", workouts=workouts)


# Add Workout Category route
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if session.get('user'):
        if request.method == "POST":
            # retrieve data from the form
            workout_category = request.form.get("workout_category")
            workout_category_image = request.form.get("workout_category_image")
            workout_category_description = request.form.get("workout_category_description")

            # Create a new workout post
            workout_category = {
                "workout_category": workout_category,
                "workout_category_image": workout_category_image,
                "workout_category_description": workout_category_description }

            mongo.db.workouts.insert_one(workout_category)
            flash("Category Successfully Added")
            return redirect(url_for("add_category", username=session["user"]))

        workouts = mongo.db.workouts.find()
        return render_template("add_category.html", workouts=workouts)
    else:
        flash("Please Log In")
        return redirect(url_for('login'))


# Edit Workout Category route
@app.route("/edit_category/<workout_id>", methods=["GET", "POST"])
def edit_category(workout_id):
    workout = mongo.db.workouts.find_one({"_id": ObjectId(workout_id)})
    if request.method == "POST":
        # Retrieve updated data from the form
        edited_category = {
            "workout_category": request.form.get("workout_category"),
            "workout_category_image": request.form.get("workout_category_image"),
            "workout_category_description": request.form.get("workout_category_description") }

        mongo.db.workouts.update_one(
            {"_id": ObjectId(workout_id)}, {"$set": edited_category})
        flash("Category Successfully Updated")
        return redirect(url_for("workout_categories"))

    return render_template(
        "edit_category.html", workout=workout)


# Edit Profile route
@app.route("/edit_profile<username>", methods=["GET", "POST"])
def edit_profile(username):

    if session.get('user'):
        if session.get('user') == username:
            if request.method == "POST":
                # Retrieve updated profile information from the form
                edit_profile = {
                    "email_address": request.form.get("email_address"),
                    "dob": request.form.get("dob"),
                    "profile_bio": request.form.get("profile_bio")
                }
                # Update the user's profile information in the database
                mongo.db.users.update_one(
                    {"username": session['user']}, {"$set": edit_profile})
                flash("Profile details have been updated")
                return redirect(url_for("profile", username=username))
        else:
            flash("You are not permitted to edit this account")
            return redirect(url_for('profile', username=username))
    else:
        flash("Please Log In")
        return redirect(url_for('login'))
    user = mongo.db.users.find_one({
        "username": session["user"]})
    return render_template("edit_profile.html", username=username, user=user)


# Delete Profile Route
@app.route("/delete_profile/<user_id>")
def delete_profile(user_id):
    if not session.get("user"):
        flash("You are not logged in")
        return redirect(url_for('login'))

    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    flash("Profile has been deleted")
    session.pop('user')
    return redirect(url_for("home"))


# Like Post Route
@app.route("/like_post/<_id>", methods=["GET", "POST"])
def like_post(_id):
    _id = _id
    liked_post = mongo.db.users.find_one({
        "username": session["user"]}).get("liked_post", [])

    if _id in liked_post:
        # If a User unlikes
        mongo.db.users.update_one({
            "username": session["user"]}, {"$pull": {"liked_post": _id}})
        mongo.db.posts.update_one({
            "_id": ObjectId(_id)}, {"$inc": {"like_count": -1}})
    else:
        # If a user likes
        mongo.db.users.update_one(
            {"username": session["user"]}, {"$push": {"liked_post": _id}})
        mongo.db.posts.update_one(
            {"_id": ObjectId(_id)}, {"$inc": {"like_count": 1}})

    like_count = mongo.db.posts.find_one(
        {"_id": ObjectId(_id)})["like_count"]
    if like_count == 0:
        mongo.db.posts.update_one(
            {"_id": ObjectId(_id)}, {"$unset": {"like_count": ""}})

    session["liked_post"] = liked_post

    return redirect(url_for('community'))


# Route for 404 page
@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# Run the app if executed directly
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
            