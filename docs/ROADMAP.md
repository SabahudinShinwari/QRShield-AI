# QRShield AI v3 — progress and remaining work

## Source code included

- v2 encryption, QR generation, image/webcam scan, decryption and independent URL structural rules retained.
- A real-data-only UCI PhiUSIIL CSV downloader and deterministic lexical feature extraction.
- Reproducible logistic regression pipeline, deduplication/conflict removal, registered-domain-disjoint train/validation/test split, validation-only threshold, held-out metrics and metadata.
- Explicit local `/api/ml/predict` route with 503 when no trained model exists; no invented predictions; independent AI panel in React.
- Existing Gemini consent feature remains optional, not required for local ML.

## Important work on the user's PC

1. `python -m pip install -r requirements.txt` from `backend` (v3 has new ML packages).
2. `python download_dataset.py` (official UCI data); if needed download from UCI manually.
3. `python train_phishing_model.py`; inspect generated `metadata.json` and verify domain/group split metrics.
4. Restart Flask; check `GET /api/health` shows `ml.ready: true` and local ML button becomes enabled.
5. Run full `python -m pytest -q` and frontend `npm run build`; perform UI tests on Windows browser, scanner/camera and wrong passwords.
6. Perform independent external / newer phishing dataset evaluation before claiming generalized performance.
7. Before public hosting: hardened image decode, rate limits, auth/CSRF protections, privacy impact review, HTTPS, monitoring and security audit.
8. Capture real screenshots/recording, document real evaluation results, then publish cleaned GitHub repository and LinkedIn post.

**Gemini project previously returned 403 Restricted. Never describe Gemini explanation as working until project access is restored and verified.**
