"""Download official UCI dataset 967 to local data/; no URLs are opened.

Run from backend: python download_dataset.py
If download is blocked, manually fetch the ZIP from the UCI link in README.
Only the dataset CSV is extracted, with untrusted archive paths ignored.
"""
from pathlib import Path
import io
from urllib.request import urlopen, Request
from zipfile import ZipFile

DATASET_URL = 'https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip'
DEST = Path(__file__).resolve().parent / 'ml_data' / 'PhiUSIIL_Phishing_URL_Dataset.csv'
MAX_DOWNLOAD = 60 * 1024 * 1024
MAX_EXTRACTED = 100 * 1024 * 1024


def main():
    if DEST.is_file():
        print(f'Dataset exists: {DEST}; delete it first if you want to re-download.')
        return
    print('Downloading official UCI dataset 967 (~15 MB); this uses internet once.')
    with urlopen(Request(DATASET_URL, headers={'User-Agent': 'QRShield-Research-Training/1.0'}), timeout=120) as response:
        chunks = bytearray()
        while block := response.read(1024 * 1024):
            chunks.extend(block)
            if len(chunks) > MAX_DOWNLOAD:
                raise ValueError('Unexpectedly large dataset archive; stopped.')
    with ZipFile(io.BytesIO(chunks)) as zf:
        names = [z for z in zf.infolist() if z.filename.endswith('PhiUSIIL_Phishing_URL_Dataset.csv')]
        if len(names) != 1 or names[0].file_size > MAX_EXTRACTED:
            raise ValueError('Expected original UCI dataset CSV not found or too large. Download manually from the UCI page.')
        DEST.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(names[0]) as stream, DEST.open('wb') as out:
            written = 0
            while block := stream.read(1024 * 1024):
                written += len(block)
                if written > MAX_EXTRACTED:
                    raise ValueError('Unexpectedly large extracted dataset.')
                out.write(block)
    print(f'Saved {written:,} bytes at {DEST}. Next: python train_phishing_model.py')


if __name__ == '__main__':
    main()
