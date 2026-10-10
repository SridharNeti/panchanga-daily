"""Print one day's panchanga: python gen/show.py lombard 2026-10-10 [te]"""
import datetime as dt
import sys

import engine
import labels as L


def name(table, i, lang):
    return table[lang][i]


def tithi_name(i, lang):
    return L.AMAVASYA[lang] if i == 29 else L.TITHI[lang][i % 15]


def karana_name(k, lang):
    if k == 0:
        return L.KARANA_FIXED[lang][0]
    if k >= 57:
        return L.KARANA_FIXED[lang][k - 56]
    return L.KARANA_MOVABLE[lang][(k - 1) % 7]


def hm(iso):
    t = dt.datetime.fromisoformat(iso)
    return t.strftime("%b %d %H:%M")


city = {c.slug: c for c in engine.CITIES}[sys.argv[1]]
day = dt.date.fromisoformat(sys.argv[2])
lang = sys.argv[3] if len(sys.argv) > 3 else "en"
d = engine.compute_day(day, city)
masa = (L.ADHIKA[lang] + " " if d["adhika"] else "") + L.MASA[lang][d["masa"]]
print(f"{city.name} {d['date']}")
print(f"{L.SAMVATSARA[lang][d['samvatsara']]} | {L.AYANA[lang][d['ayana']]} | {L.RITU[lang][d['ritu']]} | {masa} | "
      f"{L.PAKSHA[lang][d['paksha']]} | {tithi_name(d['tithi'][0]['index'], lang)} | {L.VARA[lang][d['vara']]}")
for key, fn in [("tithi", tithi_name), ("nakshatra", lambda i, l: L.NAKSHATRA[l][i]),
                ("yoga", lambda i, l: L.YOGA[l][i]), ("karana", karana_name)]:
    print(f"  {key:9}: " + "; ".join(f"{fn(s['index'], lang)} until {hm(s['end'])}" for s in d[key]))
print(f"  sunrise {hm(d['sunrise'])}  sunset {hm(d['sunset'])}  midday {hm(d['midday'])}  "
      f"moonrise {d['moonrise'] and hm(d['moonrise'])}  moonset {d['moonset'] and hm(d['moonset'])}")
print(f"  Sun in {L.RASI[lang][d['sun_rasi']]}, Moon in {L.RASI[lang][d['moon_rasi']]}")
for k in ("rahu_kalam", "yamagandam", "gulika_kalam", "abhijit", "brahma_muhurta"):
    print(f"  {k:15}: {hm(d[k]['start'])} - {hm(d[k]['end'])[-5:]}")
print("  durmuhurtam    : " + ", ".join(f"{hm(w['start'])} - {hm(w['end'])[-5:]}" for w in d["durmuhurtam"]))
