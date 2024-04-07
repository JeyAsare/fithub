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
        if request.form.get("password") != request.form.get("confirm_password"):
            flash("Passwords do not match")
            return redirect(url_for("register"))

        # create a new user
        register = {
            "username" : request.form.get("username").lower(),
            "email_address" : request.form.get("email_address"),
            "password" : generate_password_hash(request.form.get("password")),
            "profile_bio" : request.form.get("profile_bio")
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
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))

# Add workout rout
@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":

        workout_post = {
            "workout_category" : request.form.get("workout_category"),
            "workout_title" : request.form.get("workout_title"),
            "workout_description" : request.form.get("workout_description"),
            "rpe_scale" : request.form.get("rpe_scale"),
            "profile_by" : session["user"],
            "date_posted" : datetime.now().strftime("%d %B, %Y")

        }
        mongo.db.posts.insert_one(workout_post)
        flash("Post Successfully Added")
        return redirect(url_for("profile", username=session["user"]))

    workouts = mongo.db.workouts.find()
    return render_template("add_post.html", workouts=workouts)


@app.route("/edit_post/<post_id>" , methods=["GET", "POST"])
def edit_post(post_id):
    if request.method == "POST":

        edited_workout = {
            "workout_category" : request.form.get("workout_category"),
            "workout_title" : request.form.get("workout_title"),
            "workout_description" : request.form.get("workout_description"),
            "rpe_scale" : request.form.get("rpe_scale"),
            "profile_by" : session["user"],
            "date_posted" : datetime.now().strftime("%d %B, %Y")

        }
    
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)}, {"$set": edited_workout})
        flash("Post Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    current_rpe_scale = request.form.get("rpe_scale")
    workouts = mongo.db.workouts.find()
    return render_template("edit_post.html", workouts=workouts, current_rpe_scale=current_rpe_scale, post=post)


@app.route("/delete_post/<post_id>")
def delete_post(post_id):
    mongo.db.posts.delete_one({"_id": ObjectId(post_id)})
    flash("Post Successfully Removed")
    return redirect(url_for("profile", username=session["user"]))


# Profile route
@app.route("/profile/<username>", methods=["GET","POST"])
def profile(username):
    # grab the sessions user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    posts = list(mongo.db.posts.find())

    # defensive programming
    if session["user"]:
        return render_template("profile.html", username=username, posts=posts)
    
    return redirect(url_for('login'))

@app.route("/community")
def community():
    posts = mongo.db.posts.find()

    return render_template("community.html", posts=posts)

# Run the app if executed directly
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
