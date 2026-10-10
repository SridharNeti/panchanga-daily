"""Compare our engine with SV Temple Pittsburgh calendar (October 2026).

Raw text (temple's copyrighted calendar) stays in validation/raw/, which is not committed.
"""
import datetime as dt
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, "gen")
import engine  # noqa: E402

PIT = engine.City("pittsburgh", "Pittsburgh, PA", 40.4406, -79.9959, "America/New_York")
TZ = ZoneInfo(PIT.tz)
text = open("validation/raw/svt-oct-2026.txt").read()
blocks = re.split(r"\s(?=SR \d)", text)[1:]


def parse_t(s, day):
    """'7:25 A' (+ optional 'Oct 2') -> datetime."""
    m = re.match(r"\s*(\d+):(\d+)\s*([AP])\s*(?:(Sep|Oct|Nov)\s*(\d+))?", s)
    h, mi, ap = int(m[1]), int(m[2]), m[3]
    h = h % 12 + (12 if ap == "P" else 0)
    d = day
    if m[4]:
        d = dt.date(2026, {"Sep": 9, "Oct": 10, "Nov": 11}[m[4]], int(m[5]))
    return dt.datetime.combine(d, dt.time(h, mi), TZ)


def ours_end(segs, after):
    """End time of our segment that ends nearest to `after`."""
    ends = [dt.datetime.fromisoformat(s["end"]) for s in segs]
    return min(ends, key=lambda e: abs((e - after).total_seconds()))


def diff(a, b):
    return round((a - b).total_seconds() / 60)


rows = []
for i, b in enumerate(blocks[:31]):
    day = dt.date(2026, 10, 1) + dt.timedelta(i)
    o = engine.compute_day(day, PIT)
    r = {}
    m = re.search(r"SR (\d+:\d+ [AP]) SS (\d+:\d+ [AP])", b)
    r["sunrise"] = diff(dt.datetime.fromisoformat(o["sunrise"]), parse_t(m[1], day))
    r["sunset"] = diff(dt.datetime.fromisoformat(o["sunset"]), parse_t(m[2], day))
    for key, ok in (("RK", "rahu_kalam"), ("YA", "yamagandam"), ("GK", "gulika_kalam")):
        m = re.search(key + r" (\d+:\d+ [AP])\s*-\s*(\d+:\d+ [AP])", b)
        r[key] = diff(dt.datetime.fromisoformat(o[ok]["start"]), parse_t(m[1], day)) if m else None
    m = re.search(r"(?:[KS]-[A-Za-z]+|Amavasya|Pournami|P[uū]r[nṇ]im[aā])\s+(\d+:\d+\s*[AP](?:\s*(?:Sep|Oct|Nov)\s*\d+)?)", b)
    if m:
        t = parse_t(m[1], day)
        r["tithi_end"] = diff(ours_end(o["tithi"], t), t)
    m = re.search(r"\n(?!Amavasya|Pournami|[KS]-)([A-Z][A-Za-zāīūṣśṛṇ]+)\s*(?:\n?\([A-Za-z]+\))?\s+(\d+:\d+\s*[AP](?:\s*(?:Sep|Oct|Nov)\s*\d+)?)\n(?:.*\n)*?Yoga", b)
    if m:
        t = parse_t(m[2], day)
        r["nak_end"] = diff(ours_end(o["nakshatra"], t), t)
    vs = []
    for m in re.finditer(r"VA (\d+:\d+\s*[AP])(?:\s*(?:Sep|Oct|Nov)\s*\d+)?\s*-\s*(\d+:\d+\s*[AP](?:\s*(?:Sep|Oct|Nov)\s*\d+)?)", b):
        te = parse_t(m[2], day)
        if te < dt.datetime.fromisoformat(o["sunrise"]):
            te += dt.timedelta(1)
        ends = [dt.datetime.fromisoformat(w["end"]) for w in o["varjyam"]]
        vs.append(diff(min(ends, key=lambda e: abs((e - te).total_seconds())), te) if ends else None)
    r["varjyam_end"] = ",".join(str(v) for v in vs) if vs else None
    rows.append((day, r))

keys = ["sunrise", "sunset", "RK", "YA", "GK", "tithi_end", "nak_end", "varjyam_end"]
print("minutes (ours - temple)")
print("date       " + " ".join(f"{k:>9}" for k in keys))
for day, r in rows:
    print(f"{day} " + " ".join(f"{r.get(k) if r.get(k) is not None else '-':>11}" for k in keys))
