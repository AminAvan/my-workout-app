from flask import Flask, flash, render_template, url_for, redirect, request
import os
# we use sql for our application with SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
# to have login page
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# to work with the class forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email
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
#import requests

# locally we have a local development server running, but when we want to run our app on "Heroku" we need a professional webserver to run.
# Therefore, we install "gunicorn" -> pip install gunicorn
# In addition, although we use "sqlite3" locally, we need to install "PostgreSQL" when we want to deploy the app on the "Heroku".
# Therefore, to install "PostgreSQL" -> "pip install psycopg2"
# Moreover, Heroku has no idea about what modules we used in our app. Therefore, we "pip freeze" to see what python modules we have locally.
# Then, we need to put those modules names to a text file to notice the Heroku that which python-modules we use.
# As a result, we put all these python-modules in a text-file with "pip freeze > requirement.txt"
# Further, we need a "procfile", which tells Heroku that what kind of app is runing (i.e., a web app), so to do that we need to 
# write "echo web: gunicorn app:app > procfile" in terminal, then it produce a file named "procfile"
# In addition, I need to push my code to the Github and then from github push them to Heroku. Therefore, the first step is to push the code to the github.
# So, after creating a repsitory on github with a name, copy the "https://github.com/AminAvan/my-workout-app.git" repo.
# Next, write "git remote add origin https://github.com/AminAvan/my-workout-app.git" in the terminal.
# next, to check the repo is added correctly we use "git remote -v"
# next, write "git push origin master" in the terminal to push the code
# in addition, we create an app on heroku with "heroku create exlive" --> our app-name is exlive
# in addition, to apply changes on files on github we need to -> "git add -A" -> "git commit -m "comments"" --> "git push origin master"
# in addition, before pushing the code of program we need to define the database of the app on heroku.
# so we want a postgres, let's install it on heroku and apply changes to our code "app"
# to install "postgres", "heroku addons:create heroku-postgresql:mini --app app_name" (app_name: exlive) in terminal , mini cost 5$ 
# that is pay with the student-plan of heroku. Therefore, we need to have the url of the database to plugin it to our code.
# to get the url of database, write "heroku config --app exlive" in terminal, then copy the "DATABASE_URL"
# in addition, connect to the database, psql --host=ec2-18-214-134-226.compute-1.amazonaws.com --port=5432 --username=tcwgureblapxwo --password --dbname=d2325b3q1sbvjl
# based on the information of sql in heroku

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
# app.config['MAIL_SERVER']='smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 2525
# app.config['MAIL_USERNAME'] = '06d66d657a1edc'
# app.config['MAIL_PASSWORD'] = 'd6369e5a3796c8'
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
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
    # password column with 100 character capacity
    password = db.Column(db.String(255), nullable=False)

# create a signup form that consist of "username", "password", and "submit" button
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder":"Username"})
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


# create a signin form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder":"Username"})
    # Although I determined 100 character capacity for the password, we do not know how much character the hash function will produced.
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

# # create form for receiving the execise program via emails of users
# class RecEmailForm(FlaskForm):
#     #user_email = StringField('Email', [validators.DataRequired(), validators.Email()])
#     user_email = StringField("Email", validators=[InputRequired(), Email()])
    

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
                flash ("The written password is not correct, please try again!")
        else:
            flash ("The written username and password does not exist, please sign up!")

    return render_template('signin_page.html', form=form)

# Sign up's URL()
@app.route('/signup', methods=['GET','POST'])
def user_signup():
    # it is needed to pass the form into HTML file
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = usercredentials(username=form.username.data, password=hashed_password)
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
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"underweight\".")
        if ((bmi >= 18.5) and (bmi <= 24.9)):
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"normal weight\".")
        if ((bmi >= 25) and (bmi <= 29.9)):
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"overweight\".")
        if ((bmi >= 30) and (bmi <= 34.9)):
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 1\".")
        if ((bmi >= 35) and (bmi <= 39.9)):
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 2\".")
        if (bmi >= 40):
            flash (f"{current_user.username}; your BMI is {bmi}, it is considered \"Obesity class 3\".")
    return render_template('bmi_page.html', form=form)


# calculating the users BMI
@app.route('/fitnessprogram', methods=['GET','POST'])
# user only can see the programs if he/she signed-in
@login_required
def user_fitness_program():
    fit_programs=db.session.execute(text('select * from fitnessprograms order by excersiegoal'))
    if (request.method == 'POST'):
        # mailtrap_port = 2525
        # smtp_server = 'smtp.mailtrap.io'
        # mailtrap_username = '06d66d657a1edc'
        # mailtrap_password = 'd6369e5a3796c8'
        # mailtrap_message = """
        #                     Hi,
        #                     Check out the new post on the Mailtrap blog:
        #                     SMTP Server for Testing: Cloud-based or Local?
        #                     https://blog.mailtrap.io/2018/09/27/cloud-or-local-smtp-server/
        #                     Feel free to let us know what content would be useful for you!"""

        # sender_email = '5ce439e0-0796-4eeb-a9d4-48bb377598d5@heroku.com'
        # msg = MIMEText(mailtrap_message, "plain")
        # msg['Subject'] = 'ExLive - Workout daily program'
        # msg['From'] = sender_email


        user_resp_to_fit_programs = str(request.form['fitprgrms'])
        sug_prog = str(db.session.execute(text(f"SELECT programname FROM fitnessprograms WHERE excersiegoal = '{user_resp_to_fit_programs}'")).scalar())
        user_email = request.form['email']

        # receiver_email = user_email
        # msg['To'] = receiver_email

        flash ((f"Dear {current_user.username}; your selection is \"{user_resp_to_fit_programs}\". Therefore, we recommend program named \"{sug_prog}\" for you and will send it to your email."), 'res_user_fitness_program')
        print(sug_prog)
        print(user_email)

        # #send email
        # with smtplib.SMTP(smtp_server, mailtrap_port) as server:
        #     server.login(mailtrap_username, mailtrap_password)
        #     server.sendmail(sender_email, receiver_email, msg.as_string())
        # requests.post(
		# "https://api.mailgun.net/v3/sandboxc3fe58440daa454198bab3f3848a938b.mailgun.org/messages",
		# auth=("api", "key-cf54e2dde70cc6411a7b3abbf8400eea"),
		# data={"from": "mailgun@sandboxc3fe58440daa454198bab3f3848a938b.mailgun.org",
		# 	"to": [f"{user_email}"],
		# 	"subject": "hete 17",
		# 	"text": f"your program is {sug_prog}"})


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