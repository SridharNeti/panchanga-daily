"""iCalendar feeds: one all-day event per day (daily) or per festival day (festivals).

Alarm at 6 AM device-local time. iPhone keeps it when "Remove Alerts" is off;
Google Calendar ignores feed alarms (users set a default notification instead).
"""
import datetime as dt

SITE = "https://sridharneti.github.io/panchanga-daily/"
NAME = {"en": "Panchangam", "te": "పంచాంగం"}
SHORT_PAKSHA = {"en": ["Sh.", "Kr."], "te": ["శు.", "బ."]}  # Telugu calendars: శుద్ధ / బహుళ


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Fold to 75 octets without splitting a UTF-8 character."""
    out, cur = [], b""
    for ch in line:
        b = ch.encode()
        if len(cur) + len(b) > (75 if not out else 74):
            out.append(cur.decode())
            cur = b""
        cur += b
    out.append(cur.decode())
    return "\r\n ".join(out)


def title(view: dict, raw_tithi: int, lang: str) -> str:
    h = view["header"]
    tithi = h["tithi"] if raw_tithi in (14, 29) else f"{SHORT_PAKSHA[lang][0 if raw_tithi < 15 else 1]} {h['tithi']}"
    nak = view["limbs"][1]["items"][0]["name"]
    fest = [f for f in view["festivals"] if f != h["tithi"]]  # "Amavasya" already shown as the tithi
    return " · ".join([tithi, nak] + fest)


def notes(view: dict, lang: str, ui: dict) -> str:
    h, a, g, s = view["header"], view["avoid"], view["good"], view["sun"]
    lines = [" · ".join(h[k] for k in ("samvatsara", "ayana", "ritu", "masa", "paksha", "tithi", "vara"))]
    if view["festivals"]:
        lines.append("🪔 " + ", ".join(view["festivals"]))
    lines.append("")
    for limb in view["limbs"]:
        items = "; ".join(f"{i['name']} {ui['until'](i['until'])}" for i in limb["items"])
        lines.append(f"{ui[limb['key']]}: {items}")
    lines += ["", f"{ui['sunrise']} {s['sunrise']} · {ui['sunset']} {s['sunset']}",
              f"{ui['rahu_kalam']}: {a['rahu_kalam']}", f"{ui['yamagandam']}: {a['yamagandam']}",
              f"{ui['gulika_kalam']}: {a['gulika_kalam']}"]
    if a["durmuhurtam"]:
        lines.append(f"{ui['durmuhurtam']}: {', '.join(a['durmuhurtam'])}")
    if a["varjyam"]:
        lines.append(f"{ui['varjyam']}: {', '.join(a['varjyam'])}")
    lines += [f"{ui['abhijit']}: {g['abhijit']}"]
    if g["amrita_kalam"]:
        lines.append(f"{ui['amrita_kalam']}: {', '.join(g['amrita_kalam'])}")
    lines += ["", SITE]
    return "\n".join(lines)


UI = {
    "en": {"until": lambda t: f"until {t}", "tithi": "Tithi", "nakshatra": "Nakshatra", "yoga": "Yoga",
           "karana": "Karana", "sunrise": "Sunrise", "sunset": "Sunset", "rahu_kalam": "Rahu kalam",
           "yamagandam": "Yamagandam", "gulika_kalam": "Gulika", "durmuhurtam": "Durmuhurtam",
           "varjyam": "Varjyam", "abhijit": "Abhijit", "amrita_kalam": "Amrita kalam"},
    "te": {"until": lambda t: f"{t} వరకు", "tithi": "తిథి", "nakshatra": "నక్షత్రం", "yoga": "యోగం",
           "karana": "కరణం", "sunrise": "సూర్యోదయం", "sunset": "సూర్యాస్తమయం", "rahu_kalam": "రాహు కాలం",
           "yamagandam": "యమగండం", "gulika_kalam": "గుళిక", "durmuhurtam": "దుర్ముహూర్తం",
           "varjyam": "వర్జ్యం", "abhijit": "అభిజిత్", "amrita_kalam": "అమృత కాలం"},
}


def feed(city, city_label: str, days: dict, lang: str, festivals_only: bool) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    kind = "festivals" if festivals_only else "daily"
    calname = f"{NAME[lang]} · {city_label}" + (" · పండుగలు" if festivals_only and lang == "te"
                                                 else " · Festivals" if festivals_only else "")
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//panchanga-daily//EN", "CALSCALE:GREGORIAN",
           "METHOD:PUBLISH", f"X-WR-CALNAME:{_esc(calname)}", f"X-WR-TIMEZONE:{city.tz}",
           "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for iso, day in sorted(days.items()):
        view = day[lang]
        if festivals_only and not view["festivals"]:
            continue
        d = dt.date.fromisoformat(iso)
        summary = ", ".join(view["festivals"]) if festivals_only else title(view, day["quiz"]["tithi"], lang)
        out += ["BEGIN:VEVENT", f"UID:{iso}-{city.slug}-{lang}-{kind}@panchanga-daily", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d + dt.timedelta(1):%Y%m%d}",
                f"SUMMARY:{_esc(summary)}", f"DESCRIPTION:{_esc(notes(view, lang, UI[lang]))}",
                f"URL:{SITE}", "TRANSP:TRANSPARENT",
                "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(summary)}", "TRIGGER:PT6H", "END:VALARM",
                "END:VEVENT"]
    out.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in out) + "\r\n"
