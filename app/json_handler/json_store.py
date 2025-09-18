from pathlib import Path
from typing import Dict, Any
import json, os, tempfile
from filelock import FileLock

class JSONStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = FileLock(str(path) + ".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._atomic_write({"_meta": {"seq": 0}, "items": {}})

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        tmp = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, dir=str(self.path.parent), encoding="utf-8") as tf:
                json.dump(data, tf, indent=2, ensure_ascii=False)
                tmp = tf.name
            os.replace(tmp, self.path)
        finally:
            if tmp and os.path.exists(tmp):
                try: os.remove(tmp)
                except OSError: pass

    def read(self) -> Dict[str, Any]:
        with self.lock:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)

    def write(self, data: Dict[str, Any]) -> None:
        with self.lock:
            self._atomic_write(data)
