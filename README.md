# QRShield AI 3.0

**A local, educational QR encryption + offline URL-phishing research workspace** by Sabahudin Shinwari. Professional navy/blue/violet React UI; no green. **No subscription, Gemini key, or cloud inference is needed for the local ML feature.** This is not an audited security service, real-time threat feed or safety guarantee.

## What works, and what needs a one-time training step

| Capability | Status |
|---|---|
| AES-256-GCM/scrypt message encryption; QR PNG and copyable payload | Implemented; original `crypto_core.py` preserved |
| Image/webcam QR scanning; correct/wrong-password decryption | Implemented |
| Offline structural URL warnings | Implemented (rules, not AI) |
| Local phishing-pattern ML | Training/inference code and UI implemented. **No trained model ships in this ZIP.** Download the real dataset and run training below. |
| Optional Gemini explanation | Original consent-only feature retained. The previously discussed Google project returned `403 PERMISSION_DENIED` / Restricted; Gemini is **not** needed for this version. |
| Publicly hosted production service | Not implemented; localhost prototype only |

No fabricated dataset, classifier scores, success percentages or threat probabilities are presented. A locally trained model is enabled **only** when the artifacts are present. When the model is unavailable, the app explains how to train it; it does **not** fall back to made-up predictions.

## Prerequisites

- Windows PowerShell, Python **3.11+** and Node.js **20.19+ or 22.12+**.
- Internet **once** to install dependencies and download the research dataset. Inference is offline.
- Extract this ZIP and open `QRShield-AI-v3` in VS Code.

### 1. Backend terminal (VS Code → Terminal → New Terminal)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

If you already have a `.venv`, skip creating it, but **run pip install again** because version 3 adds scikit-learn, joblib and tldextract.

### 2. Get the authentic dataset (one-time; ~15 MB download)

```powershell
python download_dataset.py
```

This downloads **UCI PhiUSIIL Phishing URL (Website), dataset 967**, and extracts `backend/ml_data/PhiUSIIL_Phishing_URL_Dataset.csv`. If the automatic download fails, open the [official UCI dataset page](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset), download its ZIP manually, extract the CSV, and place it in `backend/ml_data/` using the exact filename above. **Do not put the extracted dataset or key material on GitHub.** The dataset is separately licensed under CC BY 4.0 by the UCI listing; see `docs/DATA_AND_MODEL.md`.

**Labels are counterintuitive:** original UCI `0 = phishing`, `1 = legitimate`. The training script explicitly converts them to our internal `1 = phishing`, `0 = benign`.

### 3. Train and evaluate the actual model

```powershell
python train_phishing_model.py
```

Wait for `model_saved_to` and genuine `validation_metrics` / `test_metrics` in the terminal. Outputs:

- `backend/ml_artifacts/url_model.joblib` — locally produced model (never load an untrusted joblib file).
- `backend/ml_artifacts/metadata.json` — dataset SHA-256, class counts, split sizes, selected threshold, real held-out precision, recall, F1, confusion matrix, average precision, AUC and limitations.

The script reads only raw `URL` and `label` from the official CSV. It extracts lexical features directly from the submitted URL, with **no DNS, page fetches, certificates, redirects, external API requests or webpage-derived columns**. It removes exact duplicates and conflicting labels, groups URL records by registered domain (bundled public-suffix snapshot), makes disjoint train/validation/test splits, fits a logistic-regression classifier, chooses its threshold on **validation only** using F2, and reports metrics on untouched held-out test groups.

This is a **historical, in-dataset evaluation, not an external/time-based validation**. Its estimates can be biased and can fail on unseen attack types. The UI deliberately reports only *phishing-like* or *benign-like pattern* with a warning; no invented or uncalibrated safety percentage.

### 4. Start the backend

```powershell
python app.py
```

Leave the terminal open. Expected: `http://127.0.0.1:5000`.

### 5. Start the frontend in a SECOND terminal

```powershell
cd frontend
npm install
npm run dev
```

If opening a terminal from the project root, the commands above work. If you're already in `backend`, run `cd ..\frontend` instead. Open **http://127.0.0.1:5173/**.

On the **AI analysis** screen, enter a complete URL → **Inspect URL locally** → **Analyze with local ML**. The second button is enabled only after successfully training a model and starting/restarting Flask. Click it explicitly; decryption/QR scanning never auto-submit URLs for classification.

For later sessions you only need to activate the backend environment and start Flask, then start Vite separately. You do **not** need to retrain on every launch.

## Testing

```powershell
# backend terminal from backend/
python -m pytest -q

# frontend terminal from frontend/
npm run build
```

**Build-environment disclosure:** the updated standalone cryptography/rule/ML tests passed in the artifact environment (the Flask-dependent tests were skipped here because Flask could not be downloaded). The TypeScript source passed syntax-transpilation checks; a complete Vite production build could not be executed in this environment because npm packages were not available. **User's previous 34 passing tests apply to v2, not a complete verification of this v3 archive.** Re-run both commands above on your PC before publishing and verify the real dataset download/training.

## Endpoints

| Method and route | Function |
|---|---|
| `GET /api/health` | API availability and honest `ml.ready` model status |
| `GET /api/ml/status` | Model installed / untrained / invalid state |
| `POST /api/ml/predict` | `{"url":"https://..."}`; **503 if untrained**, URL-only local inference otherwise |
| `POST /api/analyze` | Independent offline structural rules; never visits the link |
| `POST /api/encrypt` | QSE1 encrypted payload and QR PNG |
| `POST /api/scan` | Uploaded PNG/JPEG -> decoded QR payload |
| `POST /api/decrypt` | Password + QSE1 -> plaintext or authentication error |
| `POST /api/ai/explain` | Optional Gemini, requires consent and an authorized key; no link sent without opt-in |

## Boundaries and privacy

- Original `crypto_core.py` is unchanged. Passwords and messages reach local Flask over localhost HTTP; **not end-to-end encryption**. A QR contains encrypted content, salt and nonce, **never the password**. Password sharing must occur separately. Weak passwords remain vulnerable to offline guessing.
- The model processes the submitted URL on the Flask host. It **does not contact the target URL**. The model and original rule inspector can both produce false positives/negatives; a benign-like prediction cannot certify a site as safe.
- Browser activity displays non-sensitive event labels in tab memory only. No stored URL, password or plaintext in the activity feed. Don't publish real sensitive URLs in issues or screenshots.
- Gemini is independent and entirely optional. It requires a permitted project and explicit consent and shares only hostname/scheme/rule findings. A key's *presence* does not confirm its access works.
- Flask development server, scanning, public-hosting controls and general security have **not** been audited; do not expose directly to the Internet. See `SECURITY.md`.

## Repository layout

```text
QRShield-AI-v3/
  backend/
    app.py                 Flask routes + existing crypto/scan APIs
    crypto_core.py         unchanged original AES-GCM / scrypt
    url_analysis.py        existing offline structural rules
    ml_features.py         deterministic lexical features, no destination visits
    ml_detector.py         optional offline model loader / inference
    train_phishing_model.py reproducible UCI training + group holdout + metrics
    download_dataset.py    official UCI archive downloader
    ml_data/                dataset directory (CSV ignored by Git)
    ml_artifacts/           trained model + JSON (ignored by Git)
    tests/                  existing and new integration/smoke tests
  frontend/src/            existing original React screens + local ML panel
  docs/DATA_AND_MODEL.md   methods, data citation, model card and limitations
  SECURITY.md
  .github/workflows/ci.yml
```

**Data attribution:** Arvind Prasad and Shalini Chandra, *PhiUSIIL Phishing URL (Website)*, UCI Machine Learning Repository (2024), [dataset 967](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset), CC BY 4.0 as listed by UCI. The model and metrics you generate belong to *your run*; they are not claimed as independently validated or security certified.
