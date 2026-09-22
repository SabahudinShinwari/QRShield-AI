# Security Policy — QRShield AI 3.0

## Project Status

QRShield AI is an educational cybersecurity and portfolio project.

Live demo: https://qr-shield-ai-g8wo.vercel.app

The React frontend is hosted on Vercel, and the Python Flask backend is hosted on Render using Gunicorn.

**This application has not undergone an independent security audit. It is not a commercial security service. Do not use the public demo for sensitive information.**

## Encryption and Privacy

- Messages and passwords are sent over HTTPS to the hosted Flask backend for encryption and decryption.
- Encryption uses AES-256-GCM with password-based key derivation using scrypt.
- The password is not embedded in the generated QR payload.
- This is not end-to-end encryption because the backend processes plaintext and passwords.
- Weak passwords may be vulnerable to offline guessing.
- QR images are uploaded to the backend for scanning.
- Submitted URLs are sent to the backend for analysis.
- Session activity is designed to display non-sensitive event labels, but this does not guarantee that hosting infrastructure retains no request information.

Do not submit real passwords, confidential messages, private QR codes, or sensitive URLs to the public demo.

## URL Analysis and Machine Learning

The structural URL inspector and trained machine-learning classifier analyze URL features without visiting the destination website.

They do not perform live threat-feed checks, website ownership verification, or comprehensive security scanning.

**A prediction is not proof that a URL is safe or malicious.** False positives and false negatives are possible.

The model was evaluated on historical data and has not been independently validated for production phishing detection.

## Model and Dataset Security

The repository includes trained model artifacts and metadata but excludes the full training dataset.

Only load model files from trusted sources. Joblib uses pickle-based serialization, which can execute malicious code when loading untrusted files.

## Optional Gemini Feature

Gemini explanations are optional and are not configured in the current public deployment.

If configured later, API keys must remain in backend environment variables, never in frontend code or GitHub.

## Public Deployment Limitations

The public application has not been comprehensively tested for all production security threats.

Additional work would be required for sensitive or high-risk use, including security testing, abuse prevention, request limits, upload handling, monitoring, and privacy review.

Do not run Flask's development server directly as a public production service.

## Reporting Vulnerabilities

Please report security concerns privately to the repository maintainer through an appropriate private contact channel.

Do not post passwords, API keys, confidential messages, malicious files, or sensitive vulnerability details in public GitHub issues.

This is an educational project; no formal security response time is guaranteed.

## Responsible Use

QRShield AI is intended for learning, research, and portfolio demonstration. It is not a replacement for established encryption services or phishing protection tools.