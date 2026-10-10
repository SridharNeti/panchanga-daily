"""Panchanga engine on Swiss Ephemeris (built-in Moshier ephemeris, no data files).

Conventions (match common Telugu panchangams; verify before publishing):
- Lahiri ayanamsa, sidereal Sun/Moon.
- Sunrise/sunset = upper limb with standard refraction.
- Day runs sunrise to next sunrise; tithi/vara of the day = at sunrise.
- Amanta lunar months named by the Sun's rasi at the starting new moon.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
NAK = 360 / 27

# Weekday (Mon=0) -> 1-based eighth of daytime.
RAHU = [2, 7, 5, 6, 4, 3, 8]
YAMAGANDA = [4, 3, 2, 1, 7, 6, 5]
GULIKA = [6, 5, 4, 3, 2, 1, 7]
# Weekday -> list of (day|night, 1-based muhurta of 15). TODO: validate against a printed panchangam.
DURMUHURTA = [[("day", 9), ("day", 12)], [("day", 4), ("night", 7)], [("day", 8)],
              [("day", 6), ("day", 12)], [("day", 4), ("day", 9)], [("day", 1), ("day", 2)], [("day", 14)]]


# Start of Varjyam / Amrita kalam in ghatis (of 60) from the start of each nakshatra;
# each lasts 4 ghatis, scaled to the nakshatra's actual length. Mula has two Varjyams.
VARJYAM_GHATI = [[50], [24], [30], [40], [14], [21], [30], [20], [32], [30], [20], [18], [21], [20], [14],
                 [14], [10], [14], [20, 56], [24], [20], [10], [10], [18], [16], [24], [30]]
AMRITA_GHATI = [42, 48, 54, 52, 38, 35, 54, 44, 56, 54, 44, 42, 45, 44, 38, 38, 34, 38, 44, 48, 44, 34, 34,
                42, 40, 48, 54]


@dataclass(frozen=True)
class City:
    slug: str
    name: str
    lat: float
    lon: float
    tz: str


CITIES = [
    City("lombard", "Lombard, IL", 41.8800, -88.0078, "America/Chicago"),
    City("naperville", "Naperville, IL", 41.7508, -88.1535, "America/Chicago"),
    City("normal", "Normal, IL", 40.5142, -88.9906, "America/Chicago"),
    City("dallas", "Dallas, TX", 32.7767, -96.7970, "America/Chicago"),
    City("raleigh", "Raleigh, NC", 35.7796, -78.6382, "America/New_York"),
    City("hyderabad", "Hyderabad", 17.3850, 78.4867, "Asia/Kolkata"),
    City("mumbai", "Mumbai", 19.0760, 72.8777, "Asia/Kolkata"),
    City("kolkata", "Kolkata", 22.5726, 88.3639, "Asia/Kolkata"),
    City("bengaluru", "Bengaluru", 12.9716, 77.5946, "Asia/Kolkata"),
    City("chennai", "Chennai", 13.0827, 80.2707, "Asia/Kolkata"),
]


def sun(jd: float) -> float:
    return swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]


def moon(jd: float) -> float:
    return swe.calc_ut(jd, swe.MOON, FLAGS)[0][0]


def elong(jd: float) -> float:
    return (moon(jd) - sun(jd)) % 360


def tithi_idx(jd):  # 0..29
    return int(elong(jd) // 12)


def karana_idx(jd):  # 0..59
    return int(elong(jd) // 6)


def nak_idx(jd):  # 0..26
    return int(moon(jd) // NAK)


def yoga_idx(jd):  # 0..26
    return int(((moon(jd) + sun(jd)) % 360) // NAK)


def _boundary(f, a, b, tol=1 / 1440 / 4):
    """f(a) != f(b): earliest time in (a, b] that already has f(b)'s value."""
    va = f(a)
    while b - a > tol:
        m = (a + b) / 2
        if f(m) == va:
            a = m
        else:
            b = m
    return b


def segments(f, start, end, step=1 / 24):
    """[(value, starts, ends)] covering [start, end]; first start/last end may lie outside."""
    v, t = f(start), start
    while f(t - step) == v:
        t -= step
    s = _boundary(f, t - step, t)
    out, t = [], start
    while True:
        while f(t + step) == v:
            t += step
        e = _boundary(f, t, t + step)
        out.append((v, s, e))
        if e >= end:
            return out
        s, t, v = e, e, f(e)


def new_moon(jd: float, direction: int) -> float:
    """Nearest new moon before (-1) or after (+1) jd."""
    t = jd
    while True:
        t2 = t + direction
        e1, e2 = elong(t), elong(t2)
        crossed = (e2 < e1) if direction > 0 else (e2 > e1)
        if crossed:
            a, b = sorted((t, t2))
            while b - a > 1e-5:
                m = (a + b) / 2
                if elong(m) > 180:
                    a = m
                else:
                    b = m
            return b
        t = t2


def masa(jd: float):
    """(masa index 0=Chaitra, is_adhika) for the amanta month containing jd."""
    s1 = int(sun(new_moon(jd, -1)) // 30)
    s2 = int(sun(new_moon(jd, +1)) // 30)
    return (s1 + 1) % 12, s1 == s2


def _rise_set(jd0: float, body: int, city: City, rise: bool):
    flag = swe.CALC_RISE if rise else swe.CALC_SET
    res, t = swe.rise_trans(jd0, body, flag, (city.lon, city.lat, 0), 1013.25, 15, swe.FLG_MOSEPH)
    return t[0] if res == 0 else None


def jd_of(d: dt.datetime) -> float:
    u = d.astimezone(dt.timezone.utc)
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)


def local(jd: float, tz: ZoneInfo) -> dt.datetime:
    return (dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
            + dt.timedelta(days=jd - 2440587.5)).astimezone(tz).replace(microsecond=0)


def frame(day: dt.date, city: City):
    """(local midnight, sunrise, sunset, next sunrise, previous sunset) as UT Julian days."""
    midnight = jd_of(dt.datetime.combine(day, dt.time(0), ZoneInfo(city.tz)))
    sr = _rise_set(midnight, swe.SUN, city, True)
    ss = _rise_set(sr, swe.SUN, city, False)
    sr_next = _rise_set(ss, swe.SUN, city, True)
    ss_prev = _rise_set(midnight - 1, swe.SUN, city, False)
    return midnight, sr, ss, sr_next, ss_prev


def moonrise_in(a: float, b: float, city: City):
    t = _rise_set(a, swe.MOON, city, True)
    return t if t is not None and t < b else None


def compute_day(day: dt.date, city: City) -> dict:
    tz = ZoneInfo(city.tz)
    midnight, sr, ss, sr_next, ss_prev = frame(day, city)
    wd = day.weekday()
    daylen, nightlen = ss - sr, sr - ss_prev
    eighth, dm, nm = daylen / 8, daylen / 15, nightlen / 15

    def eighth_part(n):
        return sr + (n - 1) * eighth, sr + n * eighth

    def window(a, b):
        return {"start": local(a, tz).isoformat(), "end": local(b, tz).isoformat()}

    def segs(f):
        return [{"index": v, "start": local(a, tz).isoformat(), "end": local(b, tz).isoformat()}
                for v, a, b in segments(f, sr, sr_next)]

    m_idx, adhika = masa(sr)
    sun_rasi = int(sun(sr) // 30)
    lunar_year = day.year - 1 if (day.month <= 4 and (m_idx >= 9 or (m_idx == 0 and adhika))) else day.year
    durm = []
    for part, n in DURMUHURTA[wd]:
        if part == "day":
            durm.append(window(sr + (n - 1) * dm, sr + n * dm))
        else:
            nm_next = (sr_next - ss) / 15
            durm.append(window(ss + (n - 1) * nm_next, ss + n * nm_next))
    varjyam, amrita = [], []
    for v, a, b in segments(nak_idx, sr - 1, sr_next + 1):
        g = (b - a) / 60
        for start in VARJYAM_GHATI[v]:
            if a + start * g < sr_next and a + (start + 4) * g > sr:
                varjyam.append(window(a + start * g, a + (start + 4) * g))
        st = AMRITA_GHATI[v]
        if a + st * g < sr_next and a + (st + 4) * g > sr:
            amrita.append(window(a + st * g, a + (st + 4) * g))
    merged = []
    for w in durm:  # adjacent muhurtas (Saturday) read better as one span
        if merged and merged[-1]["end"] == w["start"]:
            merged[-1] = {"start": merged[-1]["start"], "end": w["end"]}
        else:
            merged.append(w)
    durm = merged
    mr = _rise_set(midnight, swe.MOON, city, True)
    ms = _rise_set(midnight, swe.MOON, city, False)
    nxt_mid = midnight + 1
    return {
        "date": day.isoformat(),
        "city": city.slug,
        "samvatsara": (lunar_year - 1987) % 60,
        "ayana": 0 if sun_rasi in (9, 10, 11, 0, 1, 2) else 1,
        "ritu": m_idx // 2,
        "masa": m_idx,
        "adhika": adhika,
        "paksha": 0 if tithi_idx(sr) < 15 else 1,
        "vara": wd,
        "tithi": segs(tithi_idx),
        "nakshatra": segs(nak_idx),
        "yoga": segs(yoga_idx),
        "karana": segs(karana_idx),
        "sun_rasi": sun_rasi,
        "moon_rasi": int(moon(sr) // 30),
        "sunrise": local(sr, tz).isoformat(),
        "sunset": local(ss, tz).isoformat(),
        "midday": local((sr + ss) / 2, tz).isoformat(),
        "moonrise": local(mr, tz).isoformat() if mr and mr < nxt_mid else None,
        "moonset": local(ms, tz).isoformat() if ms and ms < nxt_mid else None,
        "rahu_kalam": window(*eighth_part(RAHU[wd])),
        "yamagandam": window(*eighth_part(YAMAGANDA[wd])),
        "gulika_kalam": window(*eighth_part(GULIKA[wd])),
        "durmuhurtam": durm,
        "varjyam": varjyam,
        "amrita_kalam": amrita,
        "abhijit": window(sr + 7 * dm, sr + 8 * dm),
        "brahma_muhurta": window(sr - 2 * nm, sr - nm),
    }
