import requests, tarfile
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, dest_dir: Path) -> Path:
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = url.split('/')[-1]
    dest = dest_dir / filename

    if dest.exists():
        print(f"Console > {filename} bereits vorhanden, überspringe Download.")
        return dest

    response = requests.get(url, stream=True)
    response.raise_for_status()
    total = int(response.headers.get('content-length', 0))

    with open(dest, 'wb') as f, tqdm(desc=f"Downloading {filename}", total=total, unit='B', unit_scale=True, unit_divisor=1024) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
            bar.update(len(chunk))

    print(f"Console > Download abgeschlossen: {dest}")
    return dest

def extract_tarball(tar_path: Path, extract_to: Path) -> Path:
    tar_path = Path(tar_path)
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    name = tar_path.name.lower()
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        mode = "r:gz"
    elif name.endswith(".tar.bz2"):
        mode = "r:bz2"
    elif name.endswith(".tar"):
        mode = "r:"
    else:
        raise ValueError(f"Unsupported archive format: {tar_path}")

    print(f"Console > Entpacke {tar_path.name} nach {extract_to} ...")
    with tarfile.open(tar_path, mode) as tar:
        tar.extractall(path=extract_to)

    dirs = [d for d in extract_to.iterdir() if d.is_dir()]
    if len(dirs) == 1:
        return dirs[0]
    return extract_to
