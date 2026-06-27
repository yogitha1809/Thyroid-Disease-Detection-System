from flask import Flask, render_template, request, session, redirect, url_for
import joblib
import numpy as np
import sqlite3
import pdfplumber
import re
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)


app.secret_key = "thyroid_secret_key_123"

# OPTIONAL: better session handling
app.config['SESSION_PERMANENT'] = False

# LOAD MODEL
model = joblib.load("model/thyroid_model.pkl")

# LOGIN REQUIRED DECORATOR

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

# PDF TEXT EXTRACTION

def extract_pdf_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# VALUE EXTRACTION

def get_value(text, keywords):
    for keyword in keywords:
        pattern = rf"{keyword}[\s\S]{{0,200}}?(\d+\.?\d*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None
def get_age(text):
    match = re.search(r"\bAge\s*[:\-]?\s*(\d{2})\b", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # fallback: pick reasonable age range (10–100)
    match = re.search(r"\b(\d{2})\s*(years|yrs|y)?\b", text, re.IGNORECASE)
    if match:
        age = int(match.group(1))
        if 10 <= age <= 100:
            return age

    return None

def get_gender(text):
    match = re.search(r"(Male|Female|M|F)", text, re.IGNORECASE)
    if match:
        gender = match.group(1).upper()

        if gender == "MALE" or gender == "M":
            return 1, "Male"

        elif gender == "FEMALE" or gender == "F":
            return 0, "Female"

    return None, None

# HOME

@app.route('/')
@login_required
def home():
    return render_template('home.html', user=session['user'])

# LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session.clear() 
            session['user'] = username
            return redirect(url_for('home'))

        return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')

# REGISTER

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            return redirect(url_for('login'))

        except:
            return render_template('register.html', error="Username already exists")

        finally:
            conn.close()

    return render_template('register.html')

# LOGOUT

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# PREDICTION PAGE

@app.route('/prediction')
@login_required
def prediction():
    return render_template('prediction.html', user=session['user'])

# MANUAL PREDICTION

@app.route('/predict', methods=['POST'])
@login_required
def predict():

    try:
        age = float(request.form['age'])

        sex_input = request.form['sex'].lower()
        sex = 1 if sex_input == "male" else 0
        gender = "Male" if sex == 1 else "Female"

        tsh = float(request.form['TSH'])
        t3 = float(request.form['T3'])
        tt4 = float(request.form['TT4'])

        features = np.array([[age, sex, tsh, t3, tt4]])

        prediction = model.predict(features)
        prob = model.predict_proba(features)
        print("Features:", features)
        print("Prediction:", prediction)
        print("Probability:", prob)
        confidence = round(max(prob[0]) * 100, 2)
        prediction_time = datetime.now().strftime("%d-%m-%Y %H:%M")

        # Predict disease type
        if prediction[0] == 0:
            result = "Normal"

        else:
            # Hyperthyroidism
            if tsh < 0.4:
                result = "Hyperthyroidism"

            # Hypothyroidism
            elif tsh > 4.0:
                result = "Hypothyroidism"

            # Other thyroid disorder
            else:
                result = "Thyroid Disorder"

        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO predictions
            (age, gender, tsh, t3, tt4, prediction, confidence, source, prediction_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                age,
                gender,
                tsh,
                t3,
                tt4,
                result,
                confidence,
                "Manual",
                prediction_time
            ))

        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            prediction_text=result,
            confidence=confidence,
            age=age,
            gender=gender,
            tsh=tsh,
            t3=t3,
            tt4=tt4,
            source="Manual Entry",
            user=session['user']
        )

    except Exception as e:
        print("ERROR in predict():", e)

        return render_template(
            "result.html",
            prediction_text=f"Error: {str(e)}",
            confidence=0,
            age="",
            gender="",
            tsh=0,
            t3=0,
            tt4=0,
            source="Manual Entry",
            user=session['user']
        )
# PDF PREDICTION

@app.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():

    try:
        file = request.files['pdf_file']

        if file.filename == "":
            return redirect(url_for('prediction'))

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        text = extract_pdf_text(filepath)
        text = re.sub(r"\s+", " ", text)

        tsh = get_value(text, ["TSH"])
        t3 = get_value(text, ["T3", "FT3"])
        tt4 = get_value(text, ["TT4", "FT4"])

        tsh = tsh if tsh is not None else 2.5
        t3 = t3 if t3 is not None else 2.0
        tt4 = tt4 if tt4 is not None else 1.2

        age = get_age(text)

        if age is None:
            age = 30

        sex, gender = get_gender(text)

        if sex is None:
            sex = 1
            gender = "Male"

        features = np.array([[age, sex, tsh, t3, tt4]])

        prediction = model.predict(features)
        prob = model.predict_proba(features)
        print("Features:", features)
        print("Prediction:", prediction)
        print("Probability:", prob)

        confidence = round(max(prob[0]) * 100, 2)
        prediction_time = datetime.now().strftime("%d-%m-%Y %H:%M")

        # Predict disease type
        if prediction[0] == 0:
            result = "Normal"

        else:
            # Hyperthyroidism
            if tsh < 0.4:
                result = "Hyperthyroidism"

            # Hypothyroidism
            elif tsh > 4.0:
                result = "Hypothyroidism"

            # Other thyroid disorder
            else:
                result = "Thyroid Disorder"
        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO predictions
            (age, gender, tsh, t3, tt4, prediction, confidence, source, prediction_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                age,
                gender,
                tsh,
                t3,
                tt4,
                result,
                confidence,
                "PDF",
                prediction_time
            ))
        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            prediction_text=result,
            confidence=confidence,
            age=age,
            gender=gender,
            tsh=tsh,
            t3=t3,
            tt4=tt4,
            source="PDF Report",
            user=session['user']
        )

    except Exception as e:
        print("ERROR in upload_pdf():", e)

        return render_template(
            "result.html",
            prediction_text=f"Error: {str(e)}",
            confidence=0,
            age="",
            gender="",
            tsh=0,
            t3=0,
            tt4=0,
            source="PDF Report",
            user=session['user']
        )

# HISTORY

@app.route('/history')
@login_required
def history():

    conn = sqlite3.connect("thyroid.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()

    return render_template('history.html', records=records, user=session['user'])

# RUN APP

if __name__ == "__main__":
    app.run(debug=True, port=5001)