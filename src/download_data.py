
import hashlib
import shutil
import urllib.request

from load_database import DATA_PATH


DATA_URL = (
    "https://zenodo.org/records/16737523/files/"
    "Erasmus_2014-2023_aggregate_NUTS.csv?download=1"
)

DATA_MD5 = "048259d0c7fad5e792e13d0642aee0d8"


def md5sum(path):
    digest = hashlib.md5()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def ensure_dataset(path=DATA_PATH):
    if path.is_file() and md5sum(path) == DATA_MD5:
        print("Dataset already present, checksum OK.")
        return

    print("Downloading dataset from Zenodo...")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")

    try:
        with urllib.request.urlopen(
            DATA_URL, timeout=120
        ) as response:
            with tmp.open("wb") as file:
                shutil.copyfileobj(response, file)

        if md5sum(tmp) != DATA_MD5:
            raise ValueError("Dataset checksum mismatch.")

        tmp.replace(path)
        print("Dataset downloaded and verified.")

    except Exception as error:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"Dataset download failed: {error}"
        ) from error


if __name__ == "__main__":
    ensure_dataset()
