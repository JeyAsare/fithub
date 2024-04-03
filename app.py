import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 
from werkzeug.security import (
    generate_password_hash, check_password_hash)
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


# Profile route
@app.route("/profile<username>", methods=["GET","POST"])
def profile():
    # grab the sessions user's username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    posts = mongo.db.posts.find()
    return render_template("profile.html", username=username, posts=posts)


# Run the app if executed directly
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
