# Thyroid Disease Detection System

## Project Overview

The Thyroid Disease Detection System is a Machine Learning based web application developed using Python, Flask, and Scikit-learn. The system predicts whether a patient has thyroid disease based on medical test parameters such as TSH, T3, TT4, T4U, and FTI.

The system also supports PDF lab report analysis using PDFPlumber, allowing users to upload medical reports for automatic prediction.

---

## Objectives

- Develop a machine learning model for thyroid disease prediction
- Analyze thyroid medical datasets
- Extract data from PDF lab reports using PDFPlumber
- Provide a web-based prediction system
- Enable early detection of thyroid disorders

---

## Technologies Used

- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Matplotlib
- PDFPlumber
- HTML
- CSS
- JavaScript
- VS Code

---

## Python Libraries Required

pip install flask  
pip install pandas  
pip install numpy  
pip install scikit-learn  
pip install joblib  
pip install matplotlib  
pip install pdfplumber  

OR

pip install -r requirements.txt

---

## Dataset Information

Dataset Size: 9172 Records

Features:
- Age
- Gender
- TSH
- T3
- TT4
- T4U
- FTI

Target:
- Normal
- Thyroid Disease

---

## Machine Learning Model

Algorithm Used:
Random Forest Classifier

Accuracy:
93.51%

---

## Project Structure

THYROID DETECTION/

dataset/
- thyroid.csv
- dataset_summary.txt

model/
- thyroid_model.pkl

static/
- home.css
- login.css
- register.css
- prediction.css
- result.css
- accuracy_graph.png

templates/
- home.html
- login.html
- register.html
- prediction.html
- result.html
- history.html

app.py  
train_model.py  
check_dataset.py  
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

5. Run application  
python app.py  

6. Open browser  
http://127.0.0.1:5000  

---

## Working Flow

User Input / PDF Upload  
→ Flask Web Application  
→ PDFPlumber (if PDF uploaded)  
→ Random Forest Model  
→ Prediction Output  
→ Result Display  

---

## System Architecture

User Input  
→ Flask Application  
→ Data Processing  
→ Machine Learning Model  
→ Prediction Result  
→ Web Output  

---

## Results

The Random Forest Classifier achieved 93.51% accuracy and successfully predicts thyroid disease from medical data.

---

## Features

- User Login and Registration
- Thyroid Disease Prediction
- PDF Report Upload and Extraction
- Confidence Score Display
- Patient History Tracking
- Graph Visualization
- Model Accuracy Comparison Graph

---

## Future Improvements

- Deep Learning integration
- Multi-class classification
- Cloud deployment
- Doctor recommendation system
- Email report generation

---

## Author

Yogitha Lakshmi S
Mini Project – Thyroid Disease Detection System