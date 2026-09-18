from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import os
import io
import numpy as np

app = FastAPI(title="UPI Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Model & Encoders ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "encoders.pkl")

model = None
encoders = None

if os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH):
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    print("Model and Encoders loaded successfully.")
else:
    print("WARNING: Model and/or Encoders not found. Please run train_model.py first.")


# --- Request Body Schema ---
class Transaction(BaseModel):
    transaction_type: str
    amount: float
    merchant_category: str
    sender_bank: str
    receiver_bank: str
    device_type: str
    network_type: str


# --- Helper to encode a single value safely ---
def safe_encode(encoder, value):
    try:
        return encoder.transform([str(value)])[0]
    except ValueError:
        return 0


# --- Single Transaction Prediction ---
@app.post("/predict")
def predict_fraud(transaction: Transaction):

    if model is None or encoders is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded."
        )

    try:
        features = pd.DataFrame([{
            "transaction type": safe_encode(
                encoders["transaction type"],
                transaction.transaction_type
            ),
            "amount (INR)": transaction.amount,
            "merchant_category": safe_encode(
                encoders["merchant_category"],
                transaction.merchant_category
            ),
            "sender_bank": safe_encode(
                encoders["sender_bank"],
                transaction.sender_bank
            ),
            "receiver_bank": safe_encode(
                encoders["receiver_bank"],
                transaction.receiver_bank
            ),
            "device_type": safe_encode(
                encoders["device_type"],
                transaction.device_type
            ),
            "network_type": safe_encode(
                encoders["network_type"],
                transaction.network_type
            )
        }])

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]

        result = "Fraudulent" if prediction == 1 else "Legitimate"

        return {
            "prediction": result,
            "is_fraud": int(prediction),
            "fraud_probability": round(float(probability), 4)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --- CSV Upload & Batch Prediction ---
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):

    if model is None or encoders is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded."
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Clean headers
        df.columns = df.columns.str.strip()

        feature_cols = [
            "transaction type",
            "amount (INR)",
            "merchant_category",
            "sender_bank",
            "receiver_bank",
            "device_type",
            "network_type"
        ]

        missing = [
            col for col in feature_cols
            if col not in df.columns
        ]

        if missing:
            found_cols = list(df.columns)

            raise HTTPException(
                status_code=400,
                detail=f"CSV missing columns: {missing}. Found: {found_cols}"
            )

        # Copy dataframe
        X = df.copy()

        # Encode categorical columns
        for col in [
            "transaction type",
            "merchant_category",
            "sender_bank",
            "receiver_bank",
            "device_type",
            "network_type"
        ]:

            if col in encoders:
                le = encoders[col]

                mapping = {
                    label: idx
                    for idx, label in enumerate(le.classes_)
                }

                X[col] = (
                    X[col]
                    .astype(str)
                    .map(mapping)
                    .fillna(0)
                    .astype(int)
                )

        # Select features
        X_final = X[feature_cols]

        # Predict
        predictions = model.predict(X_final)
        probabilities = model.predict_proba(X_final)[:, 1]

        # Attach results
        df["isFraud_pred"] = predictions
        df["fraud_prob"] = probabilities

        # Filter fraudulent transactions
        fraud_df = df[
            df["isFraud_pred"] == 1
        ].copy()

        # Columns to display
        display_cols = [
            "transaction id",
            "transaction type",
            "amount (INR)",
            "sender_bank",
            "fraud_prob"
        ]

        final_display_cols = [
            col for col in display_cols
            if col in df.columns
        ]

        if "fraud_prob" not in final_display_cols:
            final_display_cols.append("fraud_prob")

        frauds_list = fraud_df[
            final_display_cols
        ].to_dict(orient="records")

        # Format probability
        for fraud in frauds_list:
            fraud["fraud_prob"] = (
                f"{round(fraud['fraud_prob'] * 100, 2)}%"
            )

        return {
            "message": "Analysis Complete",
            "total_processed": len(df),
            "fraud_count": len(frauds_list),
            "frauds": frauds_list
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}"
        )


# --- Local Development ---
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=7012
    )
