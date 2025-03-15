"""
train_xgboost_model.py

Fixes column type issues and processes kafka_data.csv for XGBoost model training.
Handles categorical data correctly by encoding and dropping "interests".
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MultiLabelBinarizer
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
import ast
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data
CSV_FILE_PATH = "/Users/sanjojoy/Documents/MDA/data/kafka_data.csv"  # Adjust path if needed
df = pd.read_csv(CSV_FILE_PATH)

# Data Cleaning & Feature Engineering
df.dropna(inplace=True)

# Convert timestamp to numerical features
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["year"] = df["timestamp"].dt.year
df["month"] = df["timestamp"].dt.month
df["day"] = df["timestamp"].dt.day
df["hour"] = df["timestamp"].dt.hour
df.drop(columns=["timestamp", "user_id"], inplace=True)  # Remove non-useful features

# Convert "interests" from string to a list
def convert_interests(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []

df["interests"] = df["interests"].apply(convert_interests)

# Multi-label binarization for interests
mlb = MultiLabelBinarizer()
interests_encoded = pd.DataFrame(mlb.fit_transform(df["interests"]), columns=mlb.classes_)
df = df.join(interests_encoded)
df.drop(columns=["interests"], inplace=True)

# One-hot encode categorical variables
categorical_cols = ["gender", "looking_for", "children", "education_level", "occupation", "frequency_of_usage", "state"]
df = pd.get_dummies(df, columns=categorical_cols)

# Normalize numerical features
scaler = StandardScaler()
df[["age", "height"]] = scaler.fit_transform(df[["age", "height"]])

# Define target variable for classification: engagement_label = 1 if swiping_history >= 250 else 0
df["engagement_label"] = df["swiping_history"].apply(lambda x: 1 if x >= 250 else 0)

# Split data
X = df.drop(columns=["swiping_history", "engagement_label"])  # Features
y_reg = df["swiping_history"]  # Regression target
y_clf = df["engagement_label"]  # Classification target

# Debug: Verify
print("Data types in X:")
print(X.dtypes)

X_train, X_test, y_reg_train, y_reg_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
# Use a separate split for classification
X_train, X_test, y_clf_train, y_clf_test = train_test_split(X, y_clf, test_size=0.2, random_state=42)

# Train XGBoost Regression Model
xgb_reg = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1)
xgb_reg.fit(X_train, y_reg_train)
y_reg_pred = xgb_reg.predict(X_test)

# Regression Metrics
mse = mean_squared_error(y_reg_test, y_reg_pred)
r2 = xgb_reg.score(X_test, y_reg_test)
print(f"Regression Model Performance:\nMSE: {mse:.2f}, R²: {r2:.2f}")

# Train XGBoost Classification Model
xgb_clf = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
xgb_clf.fit(X_train, y_clf_train)
y_clf_pred = xgb_clf.predict(X_test)

# Classification Metrics
accuracy = accuracy_score(y_clf_test, y_clf_pred)
print(f"Classification Accuracy: {accuracy:.2%}")
print("Classification Report:\n", classification_report(y_clf_test, y_clf_pred))
conf_matrix = confusion_matrix(y_clf_test, y_clf_pred)

# Confusion Matrix Plot
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap="Blues")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# Save the models
with open("xgb_regressor.pkl", "wb") as f:
    pickle.dump(xgb_reg, f)

with open("xgb_classifier.pkl", "wb") as f:
    pickle.dump(xgb_clf, f)

print("✅ Models Saved: xgb_regressor.pkl & xgb_classifier.pkl")