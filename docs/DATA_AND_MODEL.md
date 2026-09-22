# QRShield local URL classifier — dataset + model card

## Origin and license

UCI Machine Learning Repository, dataset ID 967: **PhiUSIIL Phishing URL (Website)**, by Arvind Prasad and Shalini Chandra (2024), https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset . The UCI dataset page lists 235,795 rows, with 134,850 legitimate and 100,945 phishing URLs, and a CC BY 4.0 license. Attribute the original authors and repository when using or sharing the dataset. Dataset contains full URLs that could refer to real-world malicious websites: DO NOT click, crawl, resolve, or upload them to unrelated services. The code downloads only the official dataset archive once, never visits included URLs, and excludes the CSV from the Git ZIP.

The dataset contains website-derived attributes. **We do not use those at all**, because a QR scan supplies only the URL. The training CSV reader uses exactly `URL` and `label`. Original labels: `0 = phishing`, `1 = legitimate`; internal labels: `1 = phishing`, `0 = benign`. Invalid URLs, exact duplicates and identical URLs with conflicting labels are removed. The training script records dropped counts, a SHA-256 of the source CSV and class counts.

## Feature availability and reproducibility

`ml_features.py` is the *single* feature function used by both training and inference. Its features are URL length, hostname/path lengths, scheme, domain-level count, IP-host indicator, explicit user-info, port, digits and special-character counts, percent encoding, path depth, Punycode, URL lexical token count, entropy, and the existing offline rule count. No DNS/WHOIS, certificate validation, page fetch, network reputation or third-party data.

Model: scikit-learn `DictVectorizer` -> `StandardScaler(with_mean=False)` -> `LogisticRegression(class_weight='balanced', random_state=42, max_iter=700)`. We split with `GroupShuffleSplit` using *registered domain* groups from offline tldextract suffix data: 20% test, then 20% of remaining train/validation pool (approximately 64/16/20). Train/validation/test domain groups cannot overlap. The classifier sees training rows only, a phishing-recall-weighted F2 threshold is selected only from validation data, and final precision/recall/F1/balanced accuracy/confusion matrix/AUPRC/AUC are computed on the unseen test set once. The exact split sizes and chosen threshold are in generated metadata.

### Honest evaluation status

**No real PhiUSIIL dataset could be downloaded or fitted within the artifact-generation environment. No actual held-out metrics or final model weights are included in this ZIP.** Unit/smoke tests use synthetic `.invalid` URLs to verify feature extraction and trainer execution only, never to claim model quality. To obtain publishable *within-dataset* results, run the real downloader and trainer on your machine and inspect `ml_artifacts/metadata.json`. Report class counts and all confusion-matrix cells. Do not claim a number until the command succeeds with the real source dataset.

### Limits / deployment considerations

- Historical dataset and possible collection artifacts may bias the model; group-disjoint tests reduce one source of leakage but are not independent temporal or external validation. New phishing techniques and false negatives remain possible.
- The classifier is **not a threat-intelligence service**, cannot validate website safety, and does not follow redirects or query a reputation provider. No probability is shown in the UI: logistic-regression scores have not been calibrated to real-world phishing prevalence.
- An IP, short link or unknown domain might be misclassified, and a benign-looking phishing URL may fool both rules and ML. Keep the independent structural warning panel and advise verification out of band.
- The model artifact uses joblib/pickle. Only load model files created by your own local training run. Do not add user-upload model functionality or download arbitrary `joblib` artifacts. Dataset and trained artifacts are ignored by Git by default.
- No current performance claim, production security audit, permissioned public hosting, or provider billing are included. Google Gemini remains an independent opt-in optional explanation component and may be unavailable for the user's Restricted Google project.
