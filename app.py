from flask import Flask, flash, render_template, url_for, redirect, request, Markup
import os
# we use sql for our application with SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
# to have login page
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# to work with the class forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email, DataRequired
# to hash the users' passwords we use "bcrypt"
from flask_bcrypt import Bcrypt
# to create a number for two-factor-authentication
import pyotp
# to send email
from flask_mail import Mail, Message
# for calculation
from mpmath import *
# enable the app for sending the workout-programs to users' email
import smtplib
from email.mime.text import MIMEText
import requests
import time


# Get the port number from the environment(e.g., heroku) variable, or use a default value
port = int(os.environ.get('PORT', 5000))

# we have a user table that stores users information (username, password)
# we create a database with a file named "database.db", in order to connect to the "database.db", we need to use SQLAlchemy

# create a web instance
app = Flask(__name__)

# we need to connect our app file "db = SQLAlchemy(app)" to the file "database.db"
# we need to connect our app to postgres database as we want to deploy app on heroku
# therefore, "postgres://tcwgureblapxwo:6b845ecaf0926b7929062c0ecf602ae16a5d74b8a390c150bdea759a341ea81d@ec2-18-214-134-226.compute-1.amazonaws.com:5432/d2325b3q1sbvjl"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' change to
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tcwgureblapxwo:6b845ecaf0926b7929062c0ecf602ae16a5d74b8a390c150bdea759a341ea81d@ec2-18-214-134-226.compute-1.amazonaws.com:5432/d2325b3q1sbvjl'

# create a database instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# to solve creating the tables we need to 
# from app import app, db -> app.app_context().push() -> db.create_all() in our python environment
# we need to build a secret_key to have a secure session cookie, in a production environment this should be a secret, but for simplicty in here
# I just write a simple sentence here
app.config['SECRET_KEY'] = 'secretkeyvalue'

# initialize our mail, we give "app" to "Mail" class as an argument
mail = Mail(app)


# allow web_server and FLASK to work together to handle user when signin
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_signin" # write the "signin" view function "def user_signin():"

# define the "user_loader callback" function to reload user object from the user id stored in the session
@login_manager.user_loader
def load_user(user_id):
    return usercredentials.query.get(int(user_id))


# create a "user" table for checking/storing user information
class usercredentials(db.Model, UserMixin):
    # id column
    id = db.Column(db.Integer, primary_key=True)
    # username column with 50 character capacity, "unique=True" is for that two or more user cannot have a same username
    username = db.Column(db.String(50), nullable=False, unique=True)
    # email, the unique should enable as each user should has a unique email address
    useremail = db.Column(db.String(255), nullable=False, unique=True)
    # password column with 100 character capacity
    password = db.Column(db.String(255), nullable=False)

# create a signup form that consist of "username", "password", and "submit" button
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder":"Username"})
    useremail = StringField(validators=[InputRequired(), Email(), Length(min=5, max=50)], render_kw={"placeholder":"Email"})
    # Although I determined 100 character capacity for the password, we do not know how much character the hash function will produced.
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

    # Although we wrote "unique=True" in database to have unique username, but we need to check it in the "RegisterForm"
    def validate_username(self, username):
        # query the "usercredentials" database table for the inputed username to check if the written username is already exists
        existing_user_name = usercredentials.query.filter_by(username=username.data).first()
        # if existing_user_name==TRUE, then the form raising the validation error like below
        if existing_user_name:
            raise ValidationError("The username already exists, please write a different username!")
    
    # Although we wrote "unique=True" in database to have unique useremail, but we need to check it in the "RegisterForm"
    def validate_useremail(self, useremail):
        # query the "usercredentials" database table for the inputed useremail to check if the written useremail is already exists
        existing_user_email = usercredentials.query.filter_by(useremail=useremail.data).first()
        # if existing_user_name==TRUE, then the form raising the validation error like below
        if existing_user_email:
            raise ValidationError("The email already exists, please write a different email!")


# create a signin form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder":"Username"})
    # Although I determined 100 character capacity for the password, we do not know how much character the hash function will produced.
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")


# create a calculating BMI form
class BMIForm(FlaskForm):
    user_weight = IntegerField(validators=[InputRequired()], render_kw={"placeholder":"Weight"})
    user_height = IntegerField(validators=[InputRequired()], render_kw={"placeholder":"Height"})
    claculate_user_bmi = SubmitField("Calculate")


# home page's URL
@app.route('/')
def home():
    # to rendering a HTML page instead of a plain text, I use html files in template folder
    return render_template('home_page.html')
    

# Sign in's URL(), and the form need method for 'GET' & 'POST'
@app.route('/signin', methods=['GET','POST'])
def user_signin():
    # it is needed to pass the form into HTML file
    form = LoginForm()
    # check the user exists in the database or not?
    if form.validate_on_submit():
        user = usercredentials.query.filter_by(username=form.username.data).first()
        # if the user exists in the database, we need to check the password hash
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user_dashboard'))
            else:
                flash (('The written password is not correct, please try again!'), 'sign_in_alerts')
        else:
            flash (('The written username and password does not exist, please sign up!'), 'sign_in_alerts')

    return render_template('signin_page.html', form=form)


# Sign up's URL()
@app.route('/signup', methods=['GET','POST'])
def user_signup():
    # it is needed to pass the form into HTML file
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = usercredentials(username=form.username.data, useremail=form.useremail.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_signin'))

    return render_template('signup_page.html', form=form)


# Dashboard's URL()
@app.route('/dashboard', methods=['GET','POST'])
# we only can get into the dashboard page if we already signin
@login_required
def user_dashboard():
    return render_template('dashboard_page.html', usr_nme = current_user.username)


# calculating the users BMI
@app.route('/bmi', methods=['GET','POST'])
# user only can calculate his/her bmi if he/she signed-in
@login_required
def user_bmi():
    form = BMIForm()
    if form.validate_on_submit():
        # calculating BMI
        bmi = form.user_weight.data / ((form.user_height.data/100)**2)
        # rounding BMI in having only "2" decimal digits
        bmi = round(bmi,1)
        if (bmi < 18.5):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"underweight\"."), 'bmi_calc_response')
        if ((bmi >= 18.5) and (bmi <= 24.9)):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"normal weight\"."), 'bmi_calc_response')
        if ((bmi >= 25) and (bmi <= 29.9)):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"overweight\"."), 'bmi_calc_response')
        if ((bmi >= 30) and (bmi <= 34.9)):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 1\"."), 'bmi_calc_response')
        if ((bmi >= 35) and (bmi <= 39.9)):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 2\"."), 'bmi_calc_response')
        if (bmi >= 40):
            flash ((f"Dear {current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 3\"."), 'bmi_calc_response')
    return render_template('bmi_page.html', form=form)


# calculating the users BMI
@app.route('/fitnessprogram', methods=['GET','POST'])
# user only can see the programs if he/she signed-in
@login_required
def user_fitness_program():
    fit_programs=db.session.execute(text('select * from fitnessprograms order by excersiegoal'))
    if (request.method == 'POST'):
        if 'submit_button' in request.form:
            sug_day = [''] * 7 # for determining the user per day exercise _ for a week
            user_resp_to_fit_programs = str(request.form['fitprgrms'])
            sug_prog = str(db.session.execute(text(f"SELECT programname FROM fitnessprograms WHERE excersiegoal = '{user_resp_to_fit_programs}'")).scalar())
            if (sug_prog == 'Walk'):
                sug_day[0] = 'Swimming or walk'
                sug_day[1] = 'play basketball or walk'
                sug_day[2] = 'play Volleyball or walk'
                sug_day[3] = 'play Football or walk'
                sug_day[4] = 'Swimming or walk'
                sug_day[5] = 'Yoga or walk'
                sug_day[6] = 'Pilates or walk'
            elif (sug_prog == 'Full Body'):
                sug_day[0] = 'Chest workouts'
                sug_day[1] = 'Leg workouts'
                sug_day[2] = 'Shoulder workouts'
                sug_day[3] = 'Biceps workouts'
                sug_day[4] = 'Triceps workouts'
                sug_day[5] = 'UpperBody workouts'
                sug_day[6] = 'LowerBody workouts'
            elif (sug_prog == 'Run'):
                sug_day[0] = 'Jogging for 45 miutes'
                sug_day[1] = 'Running for 30 miutes'
                sug_day[2] = 'Jogging for 45 miutes'
                sug_day[3] = 'Running for 30 miutes'
                sug_day[4] = 'Jogging for 45 miutes'
                sug_day[5] = 'Running for 30 miutes'
                sug_day[6] = 'Walk for 60 miutes'
                
            exercise_message = f"""
            Dear {current_user.username};
            your selection is \"{user_resp_to_fit_programs}\".
            Therefore, we recommend program named \"{sug_prog}\" for you and here it is:
            
            Monday => \"{sug_day[0]}\".
            Tuesday => \"{sug_day[1]}\".
            Wednesday => \"{sug_day[2]}\".
            Thursday => \"{sug_day[3]}\".
            Friday => \"{sug_day[4]}\".
            Saturday => \"{sug_day[5]}\".
            Sunday => \"{sug_day[6]}\".
            
            We will send a copy of this program to your email.
            
            Regards,
            ExLive
            """

            flash (exercise_message, 'res_user_fitness_program')
            flash (Markup("""<body><form action="/fitnessprogram" method="POST" id="form2">email?<input type="submit" name="submit_email_button" value="email"></form></body>"""), 'res_user_fitness_program')
                 

        ## send email via API of MailGun
        if 'submit_email_button' in request.form:
            requests.post(
            "https://api.mailgun.net/v3/exlive.tech/messages",
            auth=("api", "key-cf54e2dde70cc6411a7b3abbf8400eea"),
            data={"from": "mailgun@exlive.tech",
            "to": [f"{current_user.useremail}"],
            "subject": "ExLive: Your Recommended Workout Routine",
            "text": "hi"})

    return render_template('fitness_program_page.html', fit_programs=fit_programs)


# Sign out's URL()
@app.route('/signout', methods=['GET','POST'])
# same as "dashboard", we only can signout if we already signin
@login_required
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)