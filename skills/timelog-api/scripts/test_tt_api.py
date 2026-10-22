"""Self-check for tt_api.empty_slots (stdlib only): python3 test_tt_api.py"""
from tt_api import empty_slots

e = lambda id, project, description="", running=False: {
    "id": id, "date": "2026-10-20", "start": "s", "end": None if running else "e",
    "durationSeconds": 60, "project": project, "description": description, "running": running,
}
report = {"entries": [
    e("a", "TT"), e("b", "tt", "  "), e("c", "TT", "done"),
    e("d", "TT", running=True), e("e", "MAX"), e("f", None),
]}
assert [s["id"] for s in empty_slots(report, "TT")] == ["a", "b"]
assert empty_slots(report, "nope") == []
print("ok")
