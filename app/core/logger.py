from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / "data"
LOG_FILE = LOG_DIR / "app.log"
_FMT = "%(asctime)s %(levelname)s %(name)s - %(message)s"

def init_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root.setLevel(logging.INFO)
    fmt = logging.Formatter(_FMT)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)