"""Synthetic fixture ONLY: pipeline smoke test, NEVER deployed or reported as performance."""
from pathlib import Path
import random
import json

from train_phishing_model import train


def test_training_pipeline_uses_real_code_but_only_fixture(tmp_path, monkeypatch):
    import train_phishing_model
    # 480 independently grouped, invented non-routable .invalid domains.
    randomizer = random.Random(42)
    rows = []
    for i in range(480):
        for j in range(3):
            if i % 2:
                url = f'http://verify-{i}.example.invalid/login/{j}?account=1'
                label = '0'   # UCI means phishing
            else:
                url = f'https://normal-{i}.example.invalid/docs/{j}'
                label = '1'   # UCI means legitimate
            rows.append((url, label))
    randomizer.shuffle(rows)
    csv_path = tmp_path / 'fixture.csv'
    csv_path.write_text('URL,label\n' + '\n'.join(f'{u},{y}' for u,y in rows), encoding='utf-8')
    monkeypatch.setattr(train_phishing_model, 'domain_group', lambda u: u.split('/')[2])
    output = tmp_path / 'artifacts'
    data = train(csv_path, output_dir=output)
    assert data['dataset'] == 'UCI PhiUSIIL 967'
    assert (output / 'url_model.joblib').is_file()
    assert (output / 'metadata.json').is_file()
    assert set(data['test_metrics']['confusion_matrix']) == {'tn','fp','fn','tp'}
    # This is an implementation smoke test; fixture labels are synthetic, no reported score.
