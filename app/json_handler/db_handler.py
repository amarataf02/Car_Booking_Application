from typing import List, Dict, Any, Optional
from .json_store import JSONStore

class GenericRepo:
    def __init__(self, store: JSONStore):
        self.store = store

    def list(self) -> List[Dict[str, Any]]:
        d = self.store.read()
        return [{"id": int(k), **v} for k, v in d.get("items", {}).items()]

    def get(self, id_: int) -> Optional[Dict[str, Any]]:
        d = self.store.read()
        v = d.get("items", {}).get(str(id_))
        return {"id": id_, **v} if v else None

    def insert(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        d = self.store.read()
        d.setdefault("_meta", {}).setdefault("seq", 0)
        d.setdefault("items", {})
        d["_meta"]["seq"] += 1
        new_id = d["_meta"]["seq"]
        d["items"][str(new_id)] = doc
        self.store.write(d)
        return {"id": new_id, **doc}

    def delete(self, id_: int) -> bool:
        d = self.store.read()
        k = str(id_)
        if k in d.get("items", {}):
            del d["items"][k]
            self.store.write(d)
            return True
        return False
