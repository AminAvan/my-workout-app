# 🏋️ ExLive — Workout & Fitness Web App

ExLive is a Flask-based fitness web application that helps users track their health by calculating their BMI and receiving personalized weekly workout programs delivered directly to their email.

---

## 🚀 Features

- **User Authentication** — Secure sign-up and sign-in with bcrypt password hashing
- **BMI Calculator** — Calculates Body Mass Index and classifies it (Underweight, Normal, Overweight, Obesity Class 1–3)
- **Fitness Program Recommender** — Suggests a personalized 7-day workout plan based on the user's exercise goal (Walk, Run, or Full Body)
- **Email Delivery** — Sends the recommended workout routine directly to the user's registered email via Mailgun API
- **Protected Routes** — Dashboard, BMI, and Fitness pages are login-protected

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | PostgreSQL (via SQLAlchemy) |
| Authentication | Flask-Login, Flask-Bcrypt |
| Forms | Flask-WTF, WTForms |
| Email Service | Mailgun API |
| Deployment | Heroku (Gunicorn, Procfile) |
| Frontend | HTML, Jinja2 Templates |

---

## 📁 Project Structure

```
my-workout-app/
├── app.py                  # Main application — routes, models, forms
├── writing_on_database.py  # Script for seeding fitness programs into DB
├── database.db             # Local SQLite DB (dev only)
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku deployment config
├── static/
│   └── images/             # UI icons and images
├── templates/
│   ├── home_page.html
│   ├── signin_page.html
│   ├── signup_page.html
│   ├── dashboard_page.html
│   ├── bmi_page.html
│   └── fitness_program_page.html
└── instance/               # Flask instance config (secret keys, etc.)
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/AminAvan/my-workout-app.git
cd my-workout-app
```

### 2. Create and activate a virtual environment
```bash
python -m venv env
source env/bin/activate        # macOS/Linux
env\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file or set the following variables in your environment:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_or_sqlite_url
MAILGUN_API_KEY=your_mailgun_api_key
```

> ⚠️ **Never commit API keys or database credentials to your repository.** Use environment variables or a `.env` file (add `.env` to `.gitignore`).

### 5. Initialize the database
```bash
python
>>> from app import app, db
>>> app.app_context().push()
>>> db.create_all()
```

### 6. Run the application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## ☁️ Deployment (Heroku)

This app is configured for Heroku deployment via `Procfile` and `gunicorn`.

```bash
heroku create
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DATABASE_URL=your_postgres_url
git push heroku master
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).