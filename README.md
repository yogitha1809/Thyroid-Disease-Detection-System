# Thyroid Disease Detection System

##  Project Overview

The **Thyroid Disease Detection System** is a Machine Learning web application built using **Python, Flask, and Scikit-learn**.  
It predicts whether a patient has thyroid disorder using medical parameters such as:

- TSH  
- T3  
- TT4  
- Age  
- Gender  

The system also supports **PDF lab report analysis**, where medical values are automatically extracted using **PDFPlumber** and used for prediction.

---

##  Objectives

- Build a machine learning model for thyroid disease prediction  
- Perform medical dataset preprocessing and analysis  
- Extract medical values from PDF lab reports  
- Provide a web-based prediction system using Flask  
- Enable early detection of thyroid disorders  
- Store and track prediction history  

---

##  Technologies Used

- Python  
- Flask  
- Scikit-learn  
- Pandas  
- NumPy  
- Joblib  
- PDFPlumber  
- Regex (re module)  
- HTML, CSS, JavaScript  
- Chart.js  
- SQLite  
- VS Code  

---

## Python Libraries Required

pip install flask  
pip install pandas  
pip install numpy  
pip install scikit-learn  
pip install joblib  
pip install pdfplumber  

OR  

pip install -r requirements.txt  

---

##  Dataset Information

- Dataset Size: 9172 Records  

Features:
- Age  
- Gender  
- TSH  
- T3  
- TT4  

Target:
- Normal (0)  
- Thyroid Disease (1)  

---

##  Machine Learning Model

- Algorithm: Random Forest Classifier  
- Other Models Tested: SVM, KNN  
- Final Model Selected: Random Forest  

Accuracy: ~93.5%

---

##  Project Structure

THYROID DETECTION SYSTEM/

dataset/
  └── thyroid.csv

model/
  └── thyroid_model.pkl

static/
  ├── home.css
  ├── login.css
  ├── register.css
  ├── prediction.css
  ├── result.css

templates/
  ├── home.html
  ├── login.html
  ├── register.html
  ├── prediction.html
  ├── result.html
  ├── history.html

uploads/
  └── (PDF files)

app.py
train_model.py
requirements.txt
README.md

---

## Installation Steps

1. Create virtual environment  
python -m venv venv  

2. Activate environment  
venv\Scripts\activate  

3. Install dependencies  
pip install -r requirements.txt  

4. Train model  
python train_model.py  

5. Run app  
python app.py  

6. Open browser  
http://127.0.0.1:5001  

---

##  Working Flow

User Input / PDF Upload  
→ Flask Application  
→ PDFPlumber (if PDF uploaded)  
→ Data Processing  
→ Machine Learning Model  
→ Prediction Output  
→ Display Result  
→ Save to SQLite History  

---

## Features

- User Login & Registration  
- Thyroid Disease Prediction  
- PDF Report Upload & Extraction  
- Confidence Score Display  
- Patient History Tracking  
- Graph Visualization  
- Model Accuracy Comparison  

---

## Future Improvements

- Deep Learning model integration  
- Multi-class classification (Hypo / Hyper / Normal)  
- Cloud deployment  
- Doctor recommendation system  
- Email report generation  
- Better PDF NLP extraction  

---

## Author

Yogitha Lakshmi S  
Mini Project – Thyroid Disease Detection System