import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from xgboost import XGBClassifier


# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("dataset/flood.csv")

print("="*60)
print("Dataset Loaded Successfully")
print("="*60)

print(df.head())


# -----------------------------
# Features and Target
# -----------------------------
X = df.drop("flood", axis=1)
y = df["flood"]


# -----------------------------
# Train Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining Samples :", len(X_train))
print("Testing Samples :", len(X_test))


# -----------------------------
# Models
# -----------------------------
models = {

    "Decision Tree":
        DecisionTreeClassifier(random_state=42),

    "Random Forest":
        RandomForestClassifier(random_state=42),

    "KNN":
        KNeighborsClassifier(),

    "XGBoost":
        XGBClassifier(
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42
        )

}


best_accuracy = 0
best_model = None
best_model_name = ""


print("\n"+"="*60)
print("MODEL TRAINING")
print("="*60)


for name, model in models.items():

    print("\n-----------------------------------")
    print(name)
    print("-----------------------------------")

    model.fit(X_train, y_train)

    prediction = model.predict(X_test)

    accuracy = accuracy_score(y_test, prediction)

    print("Accuracy :", round(accuracy*100,2),"%")

    print("\nConfusion Matrix")

    print(confusion_matrix(y_test,prediction))

    print("\nClassification Report")

    print(classification_report(y_test,prediction))

    if accuracy > best_accuracy:

        best_accuracy = accuracy
        best_model = model
        best_model_name = name



print("\n"+"="*60)
print("BEST MODEL")
print("="*60)

print("Model :",best_model_name)
print("Accuracy :",round(best_accuracy*100,2),"%")


os.makedirs("models",exist_ok=True)

joblib.dump(best_model,"models/flood_model.pkl")

print("\nModel Saved Successfully!")