from flask import Flask,render_template,url_for,request,jsonify,redirect
from flask_cors import cross_origin
import pandas as pd
import numpy as np
import datetime
import pickle
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import joblib

app = Flask(__name__, template_folder="templates")
model=joblib.load('forestfiremodel.pkl')
print("Model Loaded")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Enter a secret key
app.config["SECRET_KEY"] = "secretkey12"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()


login_manager = LoginManager()
login_manager.init_app(app)


# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)


@app.route("/",methods=['GET'])
@cross_origin()
def home():
	return render_template("index.html")


@app.route("/register" , methods=["GET", "POST"])
def register():
	
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                    password=request.form.get("password"))
        # Add the user to the database
        db.session.add(user)
        # Commit the changes made
        db.session.commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login" , methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by
    # filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        # Check if the password entered is the
        # same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return render_template("dashboard.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
        logout_user()
        return render_template("index.html")

@app.route('/predict', methods=["GET","POST"])
def predict():
    if request.method=="POST":
        return render_template("fire.html")


@app.route('/result',methods=['POST','GET'])
def result():
    if request.method == "POST":
        int_features=[float(x) for x in request.form.values()]
        final=[np.array(int_features)]
        print(int_features)
        print(final)
        prediction=model.predict_proba(final)
        output='{0:.{1}f}'.format(prediction[0][1], 2)

        if output>str(0.5):
            return render_template('fire.html',pred='Your Forest is in Danger.\nProbability of fire occuring is {}'.format(output))
        else:
            return render_template('fire.html',pred='Your Forest is safe.\n Probability of fire occuring is {}'.format(output))


if __name__ == '__main__':
    app.run(debug=True)
