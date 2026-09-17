# 🛡️ UPI Fraud Transaction Detection System

A powerful Machine Learning-based web application to detect fraudulent UPI transactions in real-time. This system uses a **Random Forest Classifier** trained on transaction behaviors to identify potential fraud with high accuracy.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.0%2B-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🏗️ System Architecture

The system follows a modern Client-Server architecture:
- **Frontend**: A responsive Web UI (HTML/CSS/JS) for user interaction.
- **Backend**: A high-performance FastAPI server.
- **ML Engine**: A trained Random Forest model with specialized encoders for categorical features.

```mermaid
graph TD
    User([User]) <-->|Interacts| UI[Frontend Web UI]
    UI <-->|JSON Requests| API[FastAPI Backend]
    API <-->|Load/Predict| Model[ML Model & Encoders]
    
    subgraph "Backend Logic"
    API -->|1. Receive Data| Pre[Preprocessing]
    Pre -->|2. Encode Features| Enc[Encoders]
    Enc -->|3. Predict| RF[Random Forest Model]
    RF -->|4. Return Result| API
    end
```

### 🧠 Model Training Pipeline

```mermaid
graph LR
    Dataset[(Dataset CSV)] -->|Load| Pandas[Pandas DataFrame]
    Pandas -->|Feature Selection| Clean[Clean Data]
    Clean -->|Label Encoding| Encoder[Feature Encoders]
    Encoder -->|Transform| X[Processed Features]
    X -->|Split| TrainTest[Train/Test Sets]
    TrainTest -->|Fit| RF[Random Forest]
    RF -->|Serialize| Artifacts[model.pkl & encoders.pkl]
```

---

## 🔄 Workflow

### 1. Batch Prediction (CSV Upload)
Perfect for analyzing large datasets of transactions at once.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Model

    User->>Frontend: Uploads CSV File
    Frontend->>Backend: POST /upload_csv
    Backend->>Backend: Read & Clean CSV
    Backend->>Backend: Vectorized Encoding
    Backend->>Model: Batch Predict
    Model-->>Backend: Probabilities & Labels
    Backend-->>Frontend: JSON Response (Frauds only)
    Frontend-->>User: Display Fraud Table
```

### 2. Single Transaction Check
For real-time verification of individual transactions.

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend
    participant API as Backend
    participant Model

    User->>UI: Enter Transaction Details
    UI->>API: POST /predict (JSON)
    API->>API: Preprocess & Encode
    API->>Model: Predict Probability
    Model-->>API: Result (Legit/Fraud)
    API-->>UI: JSON Response
    UI-->>User: Show Danger/Safe Alert
```

1. User enters details (Amount, Type, Bank, etc.).
2. System predicts **Legit** or **Fraud** instantly.
3. Displays a risk probability score (e.g., "98% Risk").

---

## 🚀 Features
- **Real-time Fraud Detection**: Instant analysis of single transactions.
- **Batch Processing**: Upload GBs of transaction logs (CSV) and get results in seconds.
- **High Accuracy**: Handles class imbalance using weighted Random Forest.
- **Premium UI**: Glassmorphism design with responsive tables and animations.
- **Smart Validation**: Automatically validates CSV headers and data types.

---

## 📂 Project Structure

```
upi_fraud_detection/
├── backend/
│   ├── main.py              # FastAPI Server & Logic
│   └── (Served Static Files)
├── frontend/
│   ├── index.html           # Web Interface
│   ├── style.css            # Premium Styling
│   └── script.js            # Frontend Logic (API Calls)
├── train_model.py           # ML Training Script
├── requirements.txt         # Dependencies
├── model.pkl                # Trained Model (Artifact)
├── encoders.pkl             # Feature Encoders (Artifact)
└── README.md                # Documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher installed.

### 1. Clone the Repository
```bash
git clone https://github.com/Gitali7/UPI-FRAUD-TRANSACTION-DETECTION-USING-MACHINE-LEARNING.git
cd UPI-FRAUD-TRANSACTION-DETECTION-USING-MACHINE-LEARNING
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Training the Model
(Optional if `model.pkl` is already present)
Ensure your dataset `upi_transactions_2024.csv` is in the root directory.
```bash
python train_model.py
```
*Wait for "Model saved as model.pkl"*

### 4. Run the Application
Navigate to the backend folder and start the server:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 7012 --reload
The server will start at `http://127.0.0.1:7012`.

---

## 🎨 Usage

1. **Open Browser**: Go to [http://127.0.0.1:7012](http://127.0.0.1:7012).
2. **Batch Mode**:
   - Click "Batch Upload".
   - Drag & Drop your `transactions.csv`.
   - View the table of detected high-risk transactions.
3. **Single Mode**:
   - Switch to "Single Check".
   - Fill in the transaction details.
   - Click "Detect Fraud" to see the result.


