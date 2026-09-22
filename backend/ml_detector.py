"""Offline phishing-*pattern* classifier. No model means honest unavailability.

Only load joblib artifacts produced locally by the QRShield training script.
Never load a model supplied by a user or from an untrusted URL: joblib uses pickle.
"""
import json
from pathlib import Path

from ml_features import lexical_features

ARTIFACT_DIR = Path(__file__).resolve().parent / 'ml_artifacts'
MODEL_FILE = ARTIFACT_DIR / 'url_model.joblib'
META_FILE = ARTIFACT_DIR / 'metadata.json'


class ModelUnavailable(RuntimeError):
    pass


def model_status() -> dict:
    if not (MODEL_FILE.is_file() and META_FILE.is_file()):
        return {'ready': False, 'mode': 'untrained', 'message': 'No trained model installed. Run the documented training command on the UCI dataset.'}
    try:
        metadata = json.loads(META_FILE.read_text(encoding='utf-8'))
        if metadata.get('artifact_schema') != 1 or metadata.get('dataset') != 'UCI PhiUSIIL 967':
            raise ValueError('Invalid model metadata')
    except (OSError, ValueError, TypeError):
        return {'ready': False, 'mode': 'invalid', 'message': 'Model metadata invalid; retrain from the documented dataset.'}
    return {'ready': True, 'mode': 'offline-trained-ml', 'message': 'Locally trained URL-only classifier available.', 'dataset': metadata['dataset']}


def classify_signal(score: float, threshold: float, review_width: float = 0.10) -> str:
    """Provisional abstention for borderline positive scores, not a new trained threshold.

    The trained cutoff remains unchanged. Scores just above it request human review
    instead of being asserted to be phishing-like. This band requires future
    validation on representative external data; it is NOT a calibrated risk measure.
    """
    if not 0.0 <= score <= 1.0 or not 0.0 < threshold < 1.0:
        raise ValueError('Invalid model values')
    if score < threshold:
        return 'benign-like'
    if score < min(round(threshold + review_width, 10), 1.0):
        return 'review-required'
    return 'phishing-like'


def predict_pattern(url: str) -> dict:
    """Called only after explicit button click and validation; never visit URL."""
    import joblib
    status = model_status()
    if not status['ready']:
        raise ModelUnavailable(status['message'])
    features = lexical_features(url)
    try:
        pipeline = joblib.load(MODEL_FILE)
        metadata = json.loads(META_FILE.read_text(encoding='utf-8'))
        threshold = float(metadata['decision_threshold'])
        probability = float(pipeline.predict_proba([features])[0, 1])
        if not 0.0 <= probability <= 1.0 or not 0.0 < threshold < 1.0:
            raise ValueError('Invalid model values')
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        raise ModelUnavailable('Model artifact cannot be read. Retrain locally.') from exc
    return {
        'signal': classify_signal(probability, threshold),
        'method': 'Offline logistic regression on lexical URL features (UCI PhiUSIIL 967).',
        'review_policy': 'Provisional: model scores from threshold to threshold + 0.10 require manual review; the trained threshold and its test metrics are unchanged.',
        'dataset': metadata['dataset'],
        'disclaimer': ('A model pattern is not a safety or maliciousness verdict. Training data is historical; '
                       'false negatives and false positives are possible. No website or threat feed was queried.'),
    }
