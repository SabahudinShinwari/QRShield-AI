# Security policy — QRShield AI 3.0

**Local educational prototype only. Not an audited application or public security product.** Never expose Flask's development server to the Internet.

- Crypto: original AES-256-GCM + scrypt implementation preserved. Browser sends plaintext and password to the local Flask backend over localhost HTTP; not end-to-end encryption. Password is not embedded in the QR, but weak passwords can be guessed offline. No sender authentication or built-in password-sharing channel.
- URL rules and local ML: analyze string features without visiting the destination, DNS lookups or redirects. They are not site-verification mechanisms and can miss phishing. ML requires real dataset training; if no model is installed, the endpoint returns unavailable rather than a fake result.
- Training: download dataset from the official UCI repository; full URLs can be sensitive/malicious. Do not visit them. Dataset and model metadata stay local and are excluded by Git. **Only load joblib files produced by your own training script**, since pickle-based loading is unsafe on untrusted files.
- Optional Gemini: separate from the ML classifier. It requires explicit per-request consent and passes only URL hostname, scheme and structural findings (not URL path/query/password/message). Key remains a backend environment variable. A configured key does not imply project access; previously user project was Restricted. Provider privacy/retention review needed before public hosting.
- Session activity: ephemeral event labels only, no stored passwords/messages/URLs. QR decoding has resource and malicious-file attack surfaces not comprehensively hardened. Public deployment needs image isolation, rate limits, auth, CSRF controls, origin validation, HTTPS, secret-management, logs/privacy review and independent audit.

Report privately to the repository maintainer via a verified contact address. Do not paste malicious links, private QR codes, passwords, trained model files from untrusted sources, or API keys into public issues.
