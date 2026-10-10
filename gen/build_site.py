"""Build display-ready daily data for the website.

python gen/build_site.py auto    -> site data for 2026-10-01 .. +24 months, calendar feeds for -7 days .. +12 months
python gen/build_site.py 2026-10-01 2027-12-31          -> site/data/<city>/<yyyy-mm>.json
python gen/build_site.py 2026-10-10 2026-11-30 --inline OUT.html
    -> a single preview page with the data embedded (no fetch needed)
"""
import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

import engine
import festivals
import ics
import labels as L
import sankalpam

ROOT = Path(__file__).resolve().parent.parent
MON = {"en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
       "te": ["జన", "ఫిబ్ర", "మార్చి", "ఏప్రి", "మే", "జూన్", "జూలై", "ఆగ", "సెప్టెం", "అక్టో", "నవం", "డిసెం"]}


def clock(iso: str, day: dt.date, lang: str) -> str:
    """'10:50 AM' / 'ఉ. 10:50'; adds the date when it is not `day`."""
    t = dt.datetime.fromisoformat(iso)
    if lang == "te":
        h = t.hour
        part = "తె." if 3 <= h < 6 else "ఉ." if h < 12 and h >= 6 else "మ." if h < 16 and h >= 12 \
            else "సా." if h < 19 and h >= 16 else "రా."
        s = f"{part} {t.hour % 12 or 12}:{t.minute:02d}"
    else:
        s = f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"
    if t.date() != day:
        s += f" ({MON[lang][t.month - 1]} {t.day})"
    return s


def span(w, day, lang):
    return f"{clock(w['start'], day, lang)} – {clock(w['end'], day, lang)}"


def tithi_name(i, lang):
    return L.AMAVASYA[lang] if i == 29 else L.TITHI[lang][i % 15]


def karana_name(k, lang):
    if k == 0:
        return L.KARANA_FIXED[lang][0]
    if k >= 57:
        return L.KARANA_FIXED[lang][k - 56]
    return L.KARANA_MOVABLE[lang][(k - 1) % 7]


def with_paksha(i, lang):
    if i in (14, 29):
        return tithi_name(i, lang)
    return f"{L.PAKSHA[lang][0 if i < 15 else 1]} {tithi_name(i, lang)}"


def day_view(city, day, fest_keys, lang, d):
    masa = (L.ADHIKA[lang] + " " if d["adhika"] else "") + L.MASA[lang][d["masa"]]
    limbs = []
    for key, fn in (("tithi", with_paksha), ("nakshatra", lambda i, l: L.NAKSHATRA[l][i]),
                    ("yoga", lambda i, l: L.YOGA[l][i]), ("karana", karana_name)):
        limbs.append({"key": key, "items": [{"name": fn(s["index"], lang), "until": clock(s["end"], day, lang)}
                                             for s in d[key]]})
    seen, sk = set(), []
    for when, iso in (("pratah", d["sunrise"]), ("madhyahnika", d["midday"]), ("sayam", d["sunset"])):
        text = sankalpam.build(city, day, dt.datetime.fromisoformat(iso), lang, d)
        time_part = text.split(", ", 3)[3]
        if time_part in seen:
            sk[-1]["when"].append(when)
            continue
        seen.add(time_part)
        sk.append({"when": [when], "at": clock(iso, day, lang), "time": time_part, "full": text})
    return {
        "header": {
            "samvatsara": L.SAMVATSARA[lang][d["samvatsara"]],
            "ayana": L.AYANA[lang][d["ayana"]],
            "ritu": L.RITU[lang][d["ritu"]],
            "masa": masa,
            "paksha": L.PAKSHA[lang][d["paksha"]],
            "tithi": tithi_name(d["tithi"][0]["index"], lang),
            "vara": L.VARA[lang][d["vara"]],
        },
        "limbs": limbs,
        "sun": {
            "sunrise": clock(d["sunrise"], day, lang),
            "sunset": clock(d["sunset"], day, lang),
            "midday": clock(d["midday"], day, lang),
            "moonrise": d["moonrise"] and clock(d["moonrise"], day, lang),
            "moonset": d["moonset"] and clock(d["moonset"], day, lang),
            "sun_rasi": L.RASI[lang][d["sun_rasi"]],
            "moon_rasi": L.RASI[lang][d["moon_rasi"]],
        },
        "avoid": {
            "rahu_kalam": span(d["rahu_kalam"], day, lang),
            "yamagandam": span(d["yamagandam"], day, lang),
            "gulika_kalam": span(d["gulika_kalam"], day, lang),
            "durmuhurtam": [span(w, day, lang) for w in d["durmuhurtam"]],
            "varjyam": [span(w, day, lang) for w in d["varjyam"]],
        },
        "good": {
            "brahma_muhurta": span(d["brahma_muhurta"], day, lang),
            "abhijit": span(d["abhijit"], day, lang),
            "amrita_kalam": [span(w, day, lang) for w in d["amrita_kalam"]],
        },
        "festivals": [festivals.NAMES[k][0 if lang == "en" else 1] for k in fest_keys],
        "sankalpam": sk,
    }


def build(start: dt.date, end: dt.date):
    """{city: {iso: {"en": view, "te": view, "quiz": raw}}}"""
    data = {}
    for city in engine.CITIES:
        fest = festivals.compute(city, start, end)
        days = {}
        for i in range((end - start).days + 1):
            day = start + dt.timedelta(i)
            d = engine.compute_day(day, city)
            days[day.isoformat()] = {
                "en": day_view(city, day, fest[day.isoformat()], "en", d),
                "te": day_view(city, day, fest[day.isoformat()], "te", d),
                "quiz": {"tithi": d["tithi"][0]["index"], "nakshatra": d["nakshatra"][0]["index"],
                         "masa": d["masa"], "ritu": d["ritu"], "vara": d["vara"]},
            }
        data[city.slug] = days
        print(city.slug, len(days), "days")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start", help="YYYY-MM-DD or 'auto'")
    ap.add_argument("end", nargs="?")
    ap.add_argument("--inline", help="write a single preview HTML with embedded data")
    ap.add_argument("--ics-dir", help="where to write calendar feeds (default site/cal)")
    a = ap.parse_args()
    today = dt.date.today()
    if a.start == "auto":
        start = dt.date(2026, 10, 1)
        end = dt.date(today.year + 2, today.month, 1) - dt.timedelta(1)
        ics_from, ics_to = today - dt.timedelta(7), today + dt.timedelta(365)
    else:
        start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
        ics_from, ics_to = start, end
    a.start, a.end = start.isoformat(), end.isoformat()
    data = build(start, end)
    meta = {"cities": [{"slug": c.slug, "name": c.name} for c in engine.CITIES],
            "labels": {k: getattr(L, k) for k in ("TITHI", "NAKSHATRA", "MASA", "RITU", "VARA")} | {
                "AMAVASYA": L.AMAVASYA},
            "range": [a.start, a.end]}
    cal = Path(a.ics_dir) if a.ics_dir else ROOT / "site" / "cal"
    cal.mkdir(parents=True, exist_ok=True)
    for c in engine.CITIES:
        for lang in ("te", "en"):
            label = L.CITY_TE[c.slug] if lang == "te" else c.name
            for fest_only in (False, True):
                name = f"{c.slug}-{lang}-{'festivals' if fest_only else 'daily'}.ics"
                window = {k: v for k, v in data[c.slug].items() if ics_from.isoformat() <= k <= ics_to.isoformat()}
                (cal / name).write_text(ics.feed(c, label, window, lang, fest_only), newline="")
    print("wrote calendar feeds to", cal)
    app = (ROOT / "site" / "app.html").read_text()
    if a.inline:
        html = app
        blob = json.dumps({"meta": meta, "days": data}, ensure_ascii=False, separators=(",", ":"))
        html = html.replace("<!--INLINE-DATA-->", f"<script>window.PANCHANGA = {blob};</script>")
        Path(a.inline).write_text(html)
        print("wrote", a.inline, round(len(html) / 1e6, 2), "MB")
        return
    out = ROOT / "site" / "data"
    for slug, days in data.items():
        by_month = defaultdict(dict)
        for iso, v in days.items():
            by_month[iso[:7]][iso] = v
        for month, v in by_month.items():
            p = out / slug / f"{month}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(v, ensure_ascii=False, separators=(",", ":")))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))
    head, body = app.split("</style>", 1)
    page = ('<!doctype html>\n<html lang="te">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</style>\n</head>\n<body>" + body.replace("<!--INLINE-DATA-->", "") + "</body>\n</html>\n")
    (ROOT / "site" / "index.html").write_text(page)
    print("wrote", out)


if __name__ == "__main__":
    main()
