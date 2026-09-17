"""Observe the host filename boundary using only uniquely owned probe files."""
import json
from pathlib import Path
import uuid

here = Path(__file__).resolve().parent
records = []
for length in (259, 260, 261):
    prefix = "q1-resumed-correction-path-" + uuid.uuid4().hex + "-"
    name_length = length - len(str(here)) - 1
    path = here / (prefix + "x" * (name_length - len(prefix)))
    record = {"path": str(path), "characters": len(str(path))}
    try:
        with path.open("xb") as stream:
            stream.write(b"Actual bounded filesystem filename probe.\n")
        record["created_and_read"] = path.read_bytes() == b"Actual bounded filesystem filename probe.\n"
    except OSError as error:
        record.update(error=repr(error), errno=error.errno, winerror=getattr(error, "winerror", None))
    finally:
        if path.exists():
            path.unlink()
    records.append(record)
with (here / "q1-resumed-correction-path-limit.json").open("x", encoding="utf-8") as stream:
    json.dump(records, stream, indent=2)
print(json.dumps(records, indent=2))
