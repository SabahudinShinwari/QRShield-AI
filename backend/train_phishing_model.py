"""Train reproducible URL-only ML on UCI PhiUSIIL (dataset ID 967).

Usage: python train_phishing_model.py --csv ml_data/PhiUSIIL_Phishing_URL_Dataset.csv
This program never visits URLs. Dataset label 0=phishing, 1=legitimate;
our internal binary label 1=phishing. Webpage-derived columns are NEVER used.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from functools import lru_cache

import joblib
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml_features import lexical_features
from ml_detector import ARTIFACT_DIR
from url_analysis import URLInputError

SEED = 42


@lru_cache(maxsize=1)
def _extractor():
    import tldextract
    return tldextract.TLDExtract(suffix_list_urls=())


def domain_group(url: str) -> str:
    """Offline PSL snapshot: group every subdomain of a registered domain together."""
    from urllib.parse import urlsplit
    hostname = (urlsplit(url).hostname or '').strip('.').lower()
    extracted = _extractor()(hostname)
    return (getattr(extracted, 'top_domain_under_public_suffix', '') or
            getattr(extracted, 'registered_domain', '') or hostname)


def load_clean_csv(path: Path, limit: int | None = None):
    """Reject conflicting labels; remove URL duplicates; ignore every other CSV column."""
    unique: dict[str, int] = {}
    conflicts: set[str] = set()
    invalid = 0
    total = 0
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    with path.open('r', encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {'URL', 'label'} <= set(reader.fieldnames):
            raise ValueError('Expected UCI PhiUSIIL CSV columns URL and label; do not use unrelated datasets.')
        for record in reader:
            total += 1
            url = record['URL'].strip()
            label = str(record['label']).strip()
            if label not in ('0', '1'):
                invalid += 1
                continue
            try:
                lexical_features(url)
            except (URLInputError, ValueError, UnicodeError):
                invalid += 1
                continue
            if url in conflicts:
                continue
            y = 1 if label == '0' else 0
            if url in unique and unique[url] != y:
                unique.pop(url)
                conflicts.add(url)
            else:
                unique[url] = y
            if limit and total >= limit:
                break
    if len(unique) < 1000:
        raise ValueError('Need at least 1,000 unique valid URLs: this is not a demo-data training tool.')
    classes = Counter(unique.values())
    if min(classes.get(0, 0), classes.get(1, 0)) < 100:
        raise ValueError('Need at least 100 samples per class. Check dataset and labels.')
    urls = list(unique)
    labels = np.array([unique[u] for u in urls], dtype=int)
    groups = np.array([domain_group(u) for u in urls])
    return urls, labels, groups, {'rows_seen': total, 'valid_unique': len(unique),
                                  'invalid_rows': invalid, 'conflicting_urls_dropped': len(conflicts),
                                  'sha256': digest.hexdigest(), 'labels': dict(classes)}


def split_groups(urls, labels, groups):
    indices = np.arange(len(urls))
    outer = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=SEED)
    train_val_i, test_i = next(outer.split(indices, labels, groups))
    inner = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=SEED + 1)
    tr_rel, val_rel = next(inner.split(train_val_i, labels[train_val_i], groups[train_val_i]))
    train_i, val_i = train_val_i[tr_rel], train_val_i[val_rel]
    for name, subset in [('train', train_i), ('validation', val_i), ('test', test_i)]:
        if len(set(labels[subset])) != 2:
            raise ValueError(f'{name} split contains one class only. Add more distinct domains.')
    assert not (set(groups[train_i]) & set(groups[val_i]))
    assert not (set(groups[train_i]) & set(groups[test_i]))
    assert not (set(groups[val_i]) & set(groups[test_i]))
    return train_i, val_i, test_i


def measurements(y, scores, threshold):
    pred = (scores >= threshold).astype(int)
    tn, fp, fn, tp = map(int, confusion_matrix(y, pred, labels=[0, 1]).ravel())
    return {
        'samples': int(len(y)), 'phishing_count': int(sum(y)), 'threshold': float(threshold),
        'precision_phishing': round(float(precision_score(y, pred, zero_division=0)), 5),
        'recall_phishing': round(float(recall_score(y, pred, zero_division=0)), 5),
        'f1_phishing': round(float(f1_score(y, pred, zero_division=0)), 5),
        'balanced_accuracy': round(float(balanced_accuracy_score(y, pred)), 5),
        'average_precision': round(float(average_precision_score(y, scores)), 5),
        'roc_auc': round(float(roc_auc_score(y, scores)), 5),
        'confusion_matrix': {'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp},
    }


def train(csv_path: Path, limit: int | None = None, output_dir: Path = ARTIFACT_DIR):
    urls, y, groups, quality = load_clean_csv(csv_path, limit)
    train_i, val_i, test_i = split_groups(urls, y, groups)
    print(f"Usable URLs: {len(urls)}; distinct domain groups: {len(set(groups))}", flush=True)
    x_train = [lexical_features(urls[i]) for i in train_i]
    x_val = [lexical_features(urls[i]) for i in val_i]
    x_test = [lexical_features(urls[i]) for i in test_i]
    pipeline = Pipeline([
        ('features', DictVectorizer(sparse=True)),
        ('scale', StandardScaler(with_mean=False)),
        ('classifier', LogisticRegression(max_iter=700, class_weight='balanced', random_state=SEED)),
    ])
    pipeline.fit(x_train, y[train_i])
    val_scores = pipeline.predict_proba(x_val)[:, 1]
    # Select on validation only, not held-out test; F2 weights phishing recall.
    thresholds = np.arange(0.20, 0.81, 0.05)
    from sklearn.metrics import fbeta_score
    threshold = float(max(thresholds, key=lambda t: (fbeta_score(y[val_i], val_scores >= t, beta=2, zero_division=0), t)))
    validation = measurements(y[val_i], val_scores, threshold)
    test = measurements(y[test_i], pipeline.predict_proba(x_test)[:, 1], threshold)
    metadata = {
        'artifact_schema': 1, 'dataset': 'UCI PhiUSIIL 967',
        'dataset_url': 'https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset',
        'dataset_license': 'CC BY 4.0 (UCI page)', 'training_utc': datetime.now(timezone.utc).isoformat(),
        'data_quality': quality, 'row_limit': limit, 'split': 'domain-group disjoint; train approximately 64%, validation 16%, test 20%',
        'split_counts': {'train': len(train_i), 'validation': len(val_i), 'test': len(test_i)},
        'features': list(x_train[0]), 'estimator': 'DictVectorizer + LogisticRegression',
        'decision_threshold': threshold, 'validation_metrics': validation, 'test_metrics': test,
        'limits': ('URL lexical features only; historical labels, possible data biases, grouped holdout is not a temporal or '
                   'external test; cannot verify site safety; probabilities not calibrated.'),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_dir / 'url_model.joblib')
    (output_dir / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps({'model_saved_to': str(output_dir), 'threshold': threshold,
                      'validation_metrics': validation, 'test_metrics': test}, indent=2), flush=True)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=Path('ml_data/PhiUSIIL_Phishing_URL_Dataset.csv'))
    parser.add_argument('--limit', type=int, default=None, help='Optional first N rows for faster experimentation; report this limitation.')
    args = parser.parse_args()
    if not args.csv.is_file():
        parser.error(f'Dataset not found: {args.csv}. Download it from UCI 967 and extract the original CSV here.')
    train(args.csv, args.limit)


if __name__ == '__main__':
    main()
