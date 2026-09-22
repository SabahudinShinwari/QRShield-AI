# QRShield AI 3.0

**Secure QR Code Encryption and ML-Based Phishing URL Analysis**

An educational full-stack cybersecurity project developed by **Sabahudin Shinwari**. QRShield AI combines password-protected QR codes, QR scanning and decryption, structural URL inspection, and a trained machine-learning model for identifying phishing-like URL patterns.

The application uses a **React and TypeScript frontend**, a **Python Flask backend**, and a **scikit-learn classifier**.

> **Security disclaimer:** QRShield AI is an educational prototype, not an audited security service. Its URL analysis does not guarantee that a website is safe or malicious. Do not use the public demo to process genuinely sensitive information.

## 🌐 Live Demo

**Website:** https://qr-shield-ai-g8wo.vercel.app

**Backend API:** https://qrshield-ai-backend.onrender.com

**API health check:** https://qrshield-ai-backend.onrender.com/api/health

The React frontend is hosted on Vercel, and the Flask backend is hosted on Render.

**Note:** The free Render instance may become inactive after periods of inactivity. The first API request can take longer while the backend starts.

---

## ✨ Features

### 1. Secure QR Code Encryption

- Encrypt short text messages using AES-256-GCM.
- Derive encryption keys from passwords using scrypt.
- Generate encrypted QR codes.
- Download QR codes as PNG images.
- Copy encrypted payloads.
- Keep the password separate from the QR payload.

### 2. QR Scanning and Decryption

- Upload PNG or JPEG QR images.
- Scan QR codes using a camera with user permission.
- Extract encrypted QSE1 payloads.
- Decrypt messages using the correct password.
- Reject incorrect passwords or modified encrypted payloads through authenticated decryption.

### 3. Structural URL Analysis

Inspect URL characteristics without visiting the destination website.

The rule-based inspector examines URL structure and identifies indicators that may warrant additional caution.

**Limitations:**

- Does not visit the destination.
- Does not follow redirects.
- Does not check live threat-intelligence feeds.
- Does not verify website ownership.
- Does not certify a URL as safe.

### 4. Machine-Learning Phishing Detection

QRShield AI includes a trained URL-only phishing-pattern classifier.

**Model:** Logistic regression using lexical URL features.

**Dataset:** UCI PhiUSIIL Phishing URL (Website), Dataset 967.

**Implementation:**

- Extracts lexical features from submitted URLs.
- Uses a trained scikit-learn model.
- Runs inference on the Flask backend.
- Does not visit the destination website.
- Displays phishing-like, benign-like, or manual-review signals.
- Does not display model scores as calibrated real-world safety probabilities.

A provisional manual-review band is used for borderline model signals. This is an interpretation rule and does not change the original trained threshold or held-out evaluation metrics.

**Important:** Training and test results describe performance on historical data. Real-world phishing attacks may differ substantially.

### 5. Optional Gemini Explanations

The application includes an optional Gemini explanation feature.

However, **Gemini is not configured in the current public deployment**. Core QR encryption, decryption, structural URL inspection, and the local trained ML model work without Gemini.

No Gemini API key is included in this repository.

### 6. Interactive Dashboard

- API connection status.
- ML model availability.
- Session activity.
- Encryption and scanning shortcuts.
- Responsive interface.
- Light and dark themes.

Session activity displays event descriptions rather than message contents.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | CSS |
| Backend | Python, Flask |
| Production server | Gunicorn |
| Cryptography | AES-256-GCM, scrypt |
| QR generation | Python qrcode |
| QR scanning | OpenCV |
| Machine learning | scikit-learn, NumPy, SciPy, joblib |
| URL processing | Python URL analysis and tldextract |
| Frontend hosting | Vercel |
| Backend hosting | Render |
| Version control | Git and GitHub |

---

## 🏗️ System Architecture

The public application follows this structure:

```text
User's Browser
      |
      v
React + TypeScript Frontend
        (Vercel)
      |
      | HTTPS requests to /api/*
      v
Vercel API Rewrite
      |
      v
Python Flask Backend
       (Render)
      |
      +-- QR Encryption / Decryption
      |
      +-- QR Image Scanning
      |
      +-- Structural URL Analysis
      |
      +-- Trained ML Classifier
```

Vercel forwards `/api/*` requests to the Flask backend through the configuration in `frontend/vercel.json`.

The frontend does not need to store a backend API key.

---

## 📁 Repository Structure

```text
QRShield-AI/
|
|-- .github/
|   `-- workflows/
|
|-- backend/
|   |-- app.py
|   |-- crypto_core.py
|   |-- url_analysis.py
|   |-- ml_features.py
|   |-- ml_detector.py
|   |-- train_phishing_model.py
|   |-- download_dataset.py
|   |-- gemini_explainer.py
|   |-- requirements.txt
|   |-- ml_artifacts/
|   |   |-- url_model.joblib
|   |   `-- metadata.json
|   |-- ml_data/
|   `-- tests/
|
|-- frontend/
|   |-- src/
|   |   |-- App.tsx
|   |   |-- main.tsx
|   |   `-- style.css
|   |-- package.json
|   |-- vite.config.ts
|   `-- vercel.json
|
|-- docs/
|   |-- DATA_AND_MODEL.md
|   `-- ROADMAP.md
|
|-- .gitignore
|-- README.md
|-- SECURITY.md
`-- START_HERE.txt
```

The original dataset CSV, Python virtual environments, frontend dependencies, and generated build files are excluded from Git.

The trained model artifacts and model metadata are included in the repository.

---

## 🚀 Run Locally

### Prerequisites

Install:

- Python 3.11 or newer.
- Node.js compatible with the frontend's Vite version.
- Git.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SabahudinShinwari/QRShield-AI.git
cd QRShield-AI
```

### Step 2 — Start the Backend

Open a terminal in VS Code.

**Windows PowerShell:**

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

The backend should be available at:

http://127.0.0.1:5000

### Step 3 — Start the Frontend

Open a **second terminal** from the repository's root directory.

```powershell
cd frontend
npm install
npm run dev
```

Open:

http://127.0.0.1:5173

Vite forwards local `/api` requests to the Flask development server.

**Note:** The trained model artifacts are already included. You do not need to retrain the model simply to run the application.

---

## 🧠 Dataset and Model Training

QRShield AI uses:

**PhiUSIIL Phishing URL (Website)**  
UCI Machine Learning Repository — Dataset 967

Dataset reference:

https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

The full CSV is not committed to GitHub.

To reproduce the model training process, open a terminal in `backend/` and run:

```powershell
python download_dataset.py
python train_phishing_model.py
```

The training process generates:

```text
backend/ml_artifacts/url_model.joblib
backend/ml_artifacts/metadata.json
```

The metadata records information about the dataset, training configuration, evaluation, and limitations.

The training approach uses URL-derived lexical features and separates data by registered domain to reduce overlap between training and evaluation groups.

Threshold selection is performed on validation data, followed by evaluation on held-out test data.

**Evaluation limitations:** This is a historical, dataset-based evaluation. It is not an external, prospective, or production security validation.

For further details, see:

[Data and Model Documentation](docs/DATA_AND_MODEL.md)

---

## 🧪 Testing

The project includes backend tests and a frontend production build.

### Backend Tests

From the `backend/` directory:

```powershell
python -m pytest -q
```

**Last locally reported result:** 47 tests passed.

### Frontend Build

From the `frontend/` directory:

```powershell
npm run build
```

The frontend production build was completed successfully before deployment.

The public deployment was also manually checked for:

- Frontend loading.
- Backend API connectivity.
- Encrypted QR generation.
- QR payload scanning and authenticated decryption.
- Structural URL analysis.
- Trained ML inference.

These checks confirm the tested workflows, not the absence of all defects or security vulnerabilities.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend and model availability |
| GET | `/api/ml/status` | ML model status |
| POST | `/api/encrypt` | Encrypt text and generate a QR code |
| POST | `/api/scan` | Extract payload from a QR image |
| POST | `/api/decrypt` | Decrypt an encrypted payload |
| POST | `/api/analyze` | Analyze URL structure |
| POST | `/api/ml/predict` | Run trained URL classification |
| POST | `/api/ai/explain` | Optional Gemini explanation |

The Gemini endpoint requires configuration and is not enabled in the public demo.

---

## ☁️ Deployment

### Backend — Render

The Flask backend is deployed as a Python Web Service.

**Root Directory:**

```text
backend
```

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Frontend — Vercel

The frontend is deployed from the same GitHub repository.

**Framework Preset:** Vite

**Root Directory:**

```text
frontend
```

**Build Command:**

```bash
npm run build
```

**Output Directory:**

```text
dist
```

The `frontend/vercel.json` file forwards `/api/*` requests to the hosted Render backend.

The current deployment does not require a Gemini API key.

---

## 🔐 Privacy and Security Limitations

Please read these limitations before using or modifying this project.

1. **Not end-to-end encryption:** The browser sends plaintext messages and passwords to the Flask backend for encryption or decryption. On the public website, the backend runs on Render.

2. **Hosted processing:** QR images and submitted URLs are also sent to the backend for their respective operations.

3. **HTTPS:** The public website communicates with its hosted backend through HTTPS. This does not eliminate the need to trust the backend and hosting infrastructure.

4. **Password security:** Weak encryption passwords can be vulnerable to offline guessing attacks.

5. **Not a phishing verdict:** Structural checks and machine-learning predictions can produce false positives and false negatives.

6. **No independent security audit:** The application has not undergone a comprehensive production security assessment.

7. **No guaranteed infrastructure privacy:** Session activity is designed not to store message contents, but this should not be interpreted as a guarantee about all hosting-provider logs or infrastructure.

8. **No sensitive information:** Do not submit real credentials, confidential messages, or genuinely sensitive QR codes to the public demo.

For additional information, read [SECURITY.md](SECURITY.md).

---

## 📚 Dataset Attribution

Arvind Prasad and Shalini Chandra.

*PhiUSIIL Phishing URL (Website).* UCI Machine Learning Repository, 2024. Dataset 967.

The UCI dataset listing identifies its license as CC BY 4.0.

The dataset is attributed to its original creators. QRShield AI does not claim ownership of the source dataset.

---

## 👨‍💻 Author

**Sabahudin Shinwari**

Computer Science (Data Science)  
Albukhary International University, Malaysia

**GitHub:** https://github.com/SabahudinShinwari

**Live Project:** https://qr-shield-ai-g8wo.vercel.app

---

## ⚠️ Disclaimer

QRShield AI is intended for education, research, and portfolio demonstration.

It is not a commercial security product, an independently audited encryption service, or a replacement for established phishing protection tools.

**Developed by Sabahudin Shinwari.**