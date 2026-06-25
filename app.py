from flask import Flask, render_template, request, session, redirect, url_for
import joblib
import numpy as np
import sqlite3
import pdfplumber
import re
import os

app = Flask(__name__)
app.secret_key = "thyroid_secret_key_123"


# LOAD MODEL

model = joblib.load("model/thyroid_model.pkl")


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================
def extract_pdf_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ==========================================
# VALUE EXTRACTION
# ==========================================
def get_value(text, keywords):

    for keyword in keywords:

        pattern = rf"{keyword}[\s\S]{{0,200}}?(\d+\.?\d*)"

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return None


# ==========================================
# HOME PAGE
# ==========================================
@app.route('/')
def home():

    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template(
        'home.html',
        user=session['user']
    )


# ==========================================
# LOGIN
# ==========================================
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
            session['user'] = username
            return redirect(url_for('home'))

        else:
            return render_template(
                'login.html',
                error="Invalid Username or Password"
            )

    return render_template('login.html')


# ==========================================
# REGISTER
# ==========================================
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

            return render_template(
                'register.html',
                error="Username already exists"
            )

        finally:
            conn.close()

    return render_template('register.html')


# ==========================================
# LOGOUT
# ==========================================
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('login'))


# ==========================================
# PREDICTION PAGE
# ==========================================
@app.route('/prediction')
def prediction():

    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template(
        'prediction.html',
        user=session['user']
    )


# ==========================================
# MANUAL PREDICTION
# ==========================================
@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:
        return redirect(url_for('login'))

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

        confidence = round(max(prob[0]) * 100, 2)

        result = (
            "Normal"
            if prediction[0] == 0
            else "Thyroid Disease Detected"
        )

        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions
        (
            age, gender, tsh, t3, tt4,
            prediction, confidence, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            age,
            gender,
            tsh,
            t3,
            tt4,
            result,
            confidence,
            "Manual"
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

        return render_template(
            "result.html",
            prediction_text=f"Error: {str(e)}",
            confidence=0,
            user=session['user']
        )

# ==========================================
# PDF PREDICTION
# ==========================================
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():

    if 'user' not in session:
        return redirect(url_for('login'))

    try:

        file = request.files['pdf_file']

        if file.filename == "":
            return redirect(url_for('prediction'))

        os.makedirs("uploads", exist_ok=True)

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        text = extract_pdf_text(filepath)
        text = re.sub(r"\s+", " ", text)

        tsh = get_value(text, ["TSH"])
        t3 = get_value(text, ["T3", "FT3"])
        tt4 = get_value(text, ["TT4", "FT4"])

        tsh = tsh if tsh is not None else 2.5
        t3 = t3 if t3 is not None else 2.0
        tt4 = tt4 if tt4 is not None else 1.2

        age = 30
        sex = 1
        gender = "Male"

        features = np.array([[age, sex, tsh, t3, tt4]])

        prediction = model.predict(features)
        prob = model.predict_proba(features)

        confidence = round(max(prob[0]) * 100, 2)

        result = (
            "Normal"
            if prediction[0] == 0
            else "Thyroid Disease Detected"
        )

        conn = sqlite3.connect("thyroid.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO predictions
        (
            age, gender, tsh, t3, tt4,
            prediction, confidence, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            age,
            gender,
            tsh,
            t3,
            tt4,
            result,
            confidence,
            "PDF"
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

        return render_template(
            "result.html",
            prediction_text=f"Error: {str(e)}",
            confidence=0,
            user=session['user']
        )

# ==========================================
# HISTORY PAGE
# ==========================================
@app.route('/history')
def history():

    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("thyroid.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM predictions ORDER BY id DESC"
    )

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        records=records,
        user=session['user']
    )


# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )