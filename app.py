from flask import Flask, flash, render_template, url_for, redirect, request
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
from flask_mail import Mail
# for calculation
from mpmath import *

# locally we have a local development server running, but when we want to run our app on "Heroku" we need a professional webserver to run.
# Therefore, we install "gunicorn" -> pip install gunicorn
# In addition, although we use "sqlite3" locally, we need to install "PostgreSQL" when we want to deploy the app on the "Heroku".
# Therefore, to install "PostgreSQL" -> "pip install psycopg2"
# Moreover, Heroku has no idea about what modules we used in our app. Therefore, we "pip freeze" to see what python modules we have locally.
# Then, we need to put those modules names to a text file to notice the Heroku that which python-modules we use.
# As a result, we put all these python-modules in a text-file with "pip freeze > requirement.txt"
# Further, we need a "procfile", which tells Heroku that what kind of app is runing (i.e., a web app), so to do that we need to 
# write "" in terminal


# we have a user table that stores users information (username, password)
# we create a database with a file named "database.db", in order to connect to the "database.db", we need to use SQLAlchemy

# create a web instance
app = Flask(__name__)
# we need to connect our app file "db = SQLAlchemy(app)" to the file "database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# create a database instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# to solve creating the tables we need to 
# from web_server import app, db -> app.app_context().push() -> db.create_all() in our python environment
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
    return User.query.get(int(user_id))


# create a "user" table for checking/storing user information
class User(db.Model, UserMixin):
    # id column
    id = db.Column(db.Integer, primary_key=True)
    # username column with 50 character capacity, "unique=True" is for that two or more user cannot have a same username
    username = db.Column(db.String(50), nullable=False, unique=True)
    # password column with 100 character capacity
    password = db.Column(db.String(100), nullable=False)

# create a signup form that consist of "username", "password", and "submit" button
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder":"Username"})
    # Although I determined 100 character capacity for the password, we do not know how much character the hash function will produced.
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

    # Although we wrote "unique=True" in database to have unique username, but we need to check it in the "RegisterForm"
    def validate_username(self, username):
        # query the "User" database table for the inputed username to check if the written username is already exists
        existing_user_name = User.query.filter_by(username=username.data).first()
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
        user = User.query.filter_by(username=form.username.data).first()
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
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
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
        user_resp_to_fit_programs = str(request.form['fitprgrms'])
        sug_prog = str(db.session.execute(text(f"SELECT programname FROM fitnessprograms WHERE excersiegoal = '{user_resp_to_fit_programs}'")).scalar())
        user_email = request.form['email']
        flash ((f"Dear {current_user.username}; your selection is \"{user_resp_to_fit_programs}\". Therefore, we recommend program named \"{sug_prog}\" for you and will send it to your email."), 'res_user_fitness_program')
        print(sug_prog)
        print(user_email)

    return render_template('fitness_program_page.html', fit_programs=fit_programs)


# Sign out's URL()
@app.route('/signout', methods=['GET','POST'])
# same as "dashboard", we only can signout if we already signin
@login_required
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

if __name__ == "__main__":
    app.run()