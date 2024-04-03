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
    
    return render_template("register.html")


# Profile route
@app.route("/profile")
def profile():
    posts = mongo.db.posts.find()
    return render_template("profile.html", posts=posts)


# Run the app if executed directly
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
