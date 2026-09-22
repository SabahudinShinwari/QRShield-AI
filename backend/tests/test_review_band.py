"""Behavior checks for provisional review zone; not model performance claims."""
import pytest
from ml_detector import classify_signal


def test_current_examples_are_not_falsely_called_safe():
    assert classify_signal(0.2606, 0.20) == 'review-required'
    assert classify_signal(0.2437, 0.20) == 'review-required'
    assert classify_signal(0.0055, 0.20) == 'benign-like'
    assert classify_signal(0.0048, 0.20) == 'benign-like'


def test_threshold_edges_and_high_signal():
    assert classify_signal(0.1999, 0.20) == 'benign-like'
    assert classify_signal(0.20, 0.20) == 'review-required'
    assert classify_signal(0.30, 0.20) == 'phishing-like'


def test_invalid_scores_fail():
    with pytest.raises(ValueError):
        classify_signal(float('nan'), 0.2)
