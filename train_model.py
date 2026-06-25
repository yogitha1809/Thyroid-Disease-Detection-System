import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Load dataset
df = pd.read_csv("dataset/thyroid.csv")

print("Dataset Shape:", df.shape)

# Keep ONLY required columns
df = df[['age', 'sex', 'TSH', 'T3', 'TT4', 'target']]

# Missing values
df['sex'] = df['sex'].fillna(df['sex'].mode()[0])
df['TSH'] = df['TSH'].fillna(df['TSH'].median())
df['T3'] = df['T3'].fillna(df['T3'].median())
df['TT4'] = df['TT4'].fillna(df['TT4'].median())

# Encode sex
df['sex'] = df['sex'].map({'F': 0, 'M': 1})

# Encode target
df['target'] = df['target'].apply(
    lambda x: 0 if str(x).strip() == '-' else 1
)

df = df.dropna()

# Features
X = df[['age', 'sex', 'TSH', 'T3', 'TT4']]
y = df['target']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Models
models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),

    "SVM": SVC(
        probability=True,
        random_state=42
    ),

    "KNN": KNeighborsClassifier(
        n_neighbors=5
    )
}

best_model = None
best_acc = 0
best_name = ""

# For graph
model_names = []
accuracies = []

print("\n===== MODEL COMPARISON =====")

for name, model in models.items():

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)

    model_names.append(name)
    accuracies.append(round(acc * 100, 2))

    print(f"{name}: {acc * 100:.2f}%")

    if acc > best_acc:
        best_acc = acc
        best_model = model
        best_name = name

print("\nBest Model:", best_name)
print("Accuracy:", round(best_acc * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    best_model.predict(X_test)
))

# ACCURACY GRAPH

plt.figure(figsize=(8, 5))

bars = plt.bar(
    model_names,
    accuracies
)

plt.title("Model Accuracy Comparison")
plt.xlabel("Algorithms")
plt.ylabel("Accuracy (%)")
plt.ylim(0, 100)

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.2f}%",
        ha='center'
    )

plt.tight_layout()

# Save graph in static folder
plt.savefig("static/accuracy_graph.png")

plt.close()

print("Accuracy graph saved successfully!")

# SAVE BEST MODEL

joblib.dump(
    best_model,
    "model/thyroid_model.pkl"
)

print("\nModel saved successfully!")