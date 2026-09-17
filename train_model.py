import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import joblib
import os

def train_model():
    dataset_path = 'upi_transactions_2024.csv'
    print(f"Loading dataset from {dataset_path}...")
    
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Please place the file in this directory.")
        # Create a dummy file for demonstration if it doesn't exist? 
        # No, better to warn user. But to allow me to proceed with verification, 
        # I might need to mock it if I were testing, but I'll trust the user to provide it.
        return

    df = pd.read_csv(dataset_path)

    # --- Preprocessing ---
    print("Preprocessing data...")
    
    # 1. Select relevant options
    # Based on the user's columns, we extract meaningful features
    features = [
        'transaction type', 
        'amount (INR)', 
        'merchant_category', 
        'sender_bank', 
        'receiver_bank', 
        'device_type', 
        'network_type'
    ]
    
    target = 'fraud_flag'

    # Check if columns exist
    missing_cols = [col for col in features + [target] if col not in df.columns]
    if missing_cols:
        print(f"Error, missing columns in CSV: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    X = df[features].copy()
    y = df[target]

    # 2. handle Categorical encoders
    categorical_cols = [
        'transaction type', 
        'merchant_category', 
        'sender_bank', 
        'receiver_bank', 
        'device_type', 
        'network_type'
    ]
    
    encoders = {}
    
    for col in categorical_cols:
        le = LabelEncoder()
        # Handle potential non-string types by converting to string
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
    
    # Save encoders
    joblib.dump(encoders, 'encoders.pkl')
    print("Encoders saved to encoders.pkl")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Training ---
    print("Training Random Forest Classifier (with Class Balancing)...")
    # 'class_weight="balanced"' fixes the issue where model ignores the minority Class (Fraud)
    clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    # --- Evaluation ---
    print("Evaluating model...")
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("-" * 30)
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("-" * 30)

    # --- Save ---
    print("Saving model...")
    joblib.dump(clf, 'model.pkl')
    print("Model saved as model.pkl")

if __name__ == "__main__":
    train_model()
