"""Dataset downloader test uses in-memory ZIP only. NO UCI network in tests."""
from io import BytesIO
from zipfile import ZipFile


def test_uci_archive_extracts_only_expected_csv(monkeypatch, tmp_path):
    import download_dataset
    archive = BytesIO()
    with ZipFile(archive, 'w') as zf:
        zf.writestr('PhiUSIIL_Phishing_URL_Dataset.csv', 'URL,label\nhttps://example.org,1\n')
        zf.writestr('../../should_not_write.txt', 'unsafe')
    monkeypatch.setattr(download_dataset, 'DEST', tmp_path / 'ml_data' / 'PhiUSIIL_Phishing_URL_Dataset.csv')
    class Response:
        def __enter__(self):
            return BytesIO(archive.getvalue())
        def __exit__(self, *args):
            return False
    monkeypatch.setattr(download_dataset, 'urlopen', lambda *a, **k: Response())
    download_dataset.main()
    assert download_dataset.DEST.read_text() == 'URL,label\nhttps://example.org,1\n'
    assert not (tmp_path / 'should_not_write.txt').exists()
