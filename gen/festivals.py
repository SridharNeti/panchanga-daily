"""Festival and vrata rules (Telugu, amanta), computed per city.

A rule = lunar month + tithi (1-30; 16-30 = Krishna) + the time of day (kala)
at which that tithi must prevail. If the tithi prevails at the kala on no day
(kshaya), the day containing most of the tithi is used; if on two days, the first.
Festival dates for vratas can follow family/sampradaya differences; the site says so.
"""
import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import engine

ANY = None


@dataclass(frozen=True)
class Rule:
    key: str
    en: str
    te: str
    masa: int | None  # 0 = Chaitra; None = every month
    tithi: int
    kala: str  # sunrise | madhyahna | aparahna | sunset | nishita | moonrise


ANNUAL = [
    Rule("ugadi", "Ugadi (Telugu New Year)", "ఉగాది", 0, 1, "sunrise"),
    Rule("rama_navami", "Sri Rama Navami", "శ్రీ రామ నవమి", 0, 9, "madhyahna"),
    Rule("akshaya_tritiya", "Akshaya Tritiya", "అక్షయ తృతీయ", 1, 3, "sunrise"),
    Rule("narasimha_jayanti", "Narasimha Jayanti", "నృసింహ జయంతి", 1, 14, "sunset"),
    Rule("hanuman_jayanti", "Hanuman Jayanti (Telugu)", "హనుమాన్ జయంతి", 1, 25, "sunrise"),
    Rule("toli_ekadashi", "Toli Ekadashi", "తొలి ఏకాదశి", 3, 11, "sunrise"),
    Rule("guru_purnima", "Guru Purnima", "గురు పౌర్ణమి", 3, 15, "sunrise"),
    Rule("naga_panchami", "Naga Panchami", "నాగ పంచమి", 4, 5, "sunrise"),
    Rule("rakhi_purnima", "Raksha Bandhan / Jandhyala Purnima", "రాఖీ పౌర్ణమి / జంధ్యాల పౌర్ణమి", 4, 15, "sunrise"),
    Rule("krishnashtami", "Sri Krishna Janmashtami", "శ్రీ కృష్ణ జన్మాష్టమి", 4, 23, "nishita"),
    Rule("vinayaka_chavithi", "Vinayaka Chavithi", "వినాయక చవితి", 5, 4, "madhyahna"),
    Rule("mahalaya_amavasya", "Mahalaya Amavasya", "మహాలయ అమావాస్య", 5, 30, "aparahna"),
    Rule("navaratri", "Sharan Navaratri begins", "శరన్నవరాత్రులు ప్రారంభం", 6, 1, "sunrise"),
    Rule("durgashtami", "Durgashtami", "దుర్గాష్టమి", 6, 8, "sunrise"),
    Rule("mahanavami", "Mahanavami", "మహర్నవమి", 6, 9, "sunrise"),
    Rule("vijayadashami", "Vijayadashami (Dasara)", "విజయదశమి (దసరా)", 6, 10, "aparahna"),
    Rule("atla_taddi", "Atla Taddi", "అట్ల తద్ది", 6, 18, "moonrise"),
    Rule("naraka_chaturdashi", "Naraka Chaturdashi", "నరక చతుర్దశి", 6, 29, "sunrise"),
    Rule("deepavali", "Deepavali", "దీపావళి", 6, 30, "sunset"),
    Rule("nagula_chavithi", "Nagula Chavithi", "నాగుల చవితి", 7, 4, "sunrise"),
    Rule("kartika_purnima", "Kartika Purnima", "కార్తీక పౌర్ణమి", 7, 15, "sunset"),
    Rule("subrahmanya_shashti", "Subrahmanya Shashti", "సుబ్రహ్మణ్య షష్ఠి", 8, 6, "sunset"),
    Rule("gita_jayanti", "Gita Jayanti", "గీతా జయంతి", 8, 11, "sunrise"),
    Rule("datta_jayanti", "Datta Jayanti", "దత్త జయంతి", 8, 15, "sunset"),
    Rule("vasanta_panchami", "Vasanta Panchami", "వసంత పంచమి", 10, 5, "sunrise"),
    Rule("ratha_saptami", "Ratha Saptami", "రథ సప్తమి", 10, 7, "sunrise"),
    Rule("bhishma_ekadashi", "Bhishma Ekadashi", "భీష్మ ఏకాదశి", 10, 11, "sunrise"),
    Rule("maha_shivaratri", "Maha Shivaratri", "మహా శివరాత్రి", 10, 29, "nishita"),
    Rule("holi", "Holi Purnima", "హోళీ పౌర్ణమి", 11, 15, "sunrise"),
]

MONTHLY = [
    Rule("ekadashi", "Ekadashi", "ఏకాదశి", ANY, 11, "sunrise"),
    Rule("ekadashi", "Ekadashi", "ఏకాదశి", ANY, 26, "sunrise"),
    Rule("pradosham", "Pradosham", "ప్రదోషం", ANY, 13, "sunset"),
    Rule("pradosham", "Pradosham", "ప్రదోషం", ANY, 28, "sunset"),
    # Monthly Shashti (Skanda/Subrahmanya) vrata: Shukla Shashti; Panchami-yukta Shashti
    # is preferred, so the first day on which Shashti prevails at sunset.
    Rule("shashti", "Shashti (Subrahmanya vratam)", "షష్ఠి (సుబ్రహ్మణ్య వ్రతం)", ANY, 6, "sunset"),
    Rule("sankashti", "Sankashti Chaturthi", "సంకష్టహర చతుర్థి", ANY, 19, "moonrise"),
    Rule("masa_shivaratri", "Masa Shivaratri", "మాస శివరాత్రి", ANY, 29, "nishita"),
    Rule("purnima", "Purnima", "పౌర్ణమి", ANY, 15, "sunrise"),
    Rule("amavasya", "Amavasya", "అమావాస్య", ANY, 30, "sunrise"),
]

SPECIAL = {
    "varalakshmi": ("Varalakshmi Vratam", "వరలక్ష్మీ వ్రతం"),
    "vaikuntha_ekadashi": ("Vaikuntha Ekadashi (Mukkoti)", "వైకుంఠ ఏకాదశి (ముక్కోటి)"),
    "bhogi": ("Bhogi", "భోగి"),
    "makara_sankranti": ("Makara Sankranti", "మకర సంక్రాంతి"),
    "kanuma": ("Kanuma", "కనుమ"),
}
NAMES = {r.key: (r.en, r.te) for r in ANNUAL + MONTHLY} | SPECIAL


def _kala(fr, kala, city):
    midnight, sr, ss, sr_next, ss_prev = fr
    day = ss - sr
    return {
        "sunrise": sr,
        "madhyahna": sr + 2.5 * day / 5,  # middle of the 3rd fifth of daytime
        "aparahna": sr + 3.5 * day / 5,  # middle of the 4th fifth
        "sunset": ss,
        "nishita": (ss + sr_next) / 2,
        "moonrise": engine.moonrise_in(sr, sr_next, city),
    }[kala]


def compute(city: engine.City, start: dt.date, end: dt.date) -> dict[str, list[str]]:
    """{iso date: [festival keys]} for start..end inclusive."""
    days = [start + dt.timedelta(i) for i in range((end - start).days + 1)]
    pad = [start - dt.timedelta(2), start - dt.timedelta(1)] + days + [end + dt.timedelta(1), end + dt.timedelta(2)]
    frames = {d: engine.frame(d, city) for d in pad}
    tz = ZoneInfo(city.tz)
    out = {d.isoformat(): [] for d in days}

    def day_of(jd):
        for d in pad:
            _, sr, _, sr_next, _ = frames[d]
            if sr <= jd < sr_next:
                return d
        return None

    def add(d, key):
        if d and d.isoformat() in out and key not in out[d.isoformat()]:
            out[d.isoformat()].append(key)

    segs = engine.segments(engine.tithi_idx, frames[pad[0]][1], frames[pad[-1]][3])
    for t, a, b in segs:
        tithi = t + 1
        m, adhika = engine.masa((a + b) / 2)
        for rule in ANNUAL + MONTHLY:
            if rule.tithi != tithi or (rule.masa is not None and (rule.masa != m or adhika)):
                continue
            if (rule.key, m) in (("masa_shivaratri", 10), ("shashti", 8)) and not adhika:
                continue  # replaced by the annual festival
            hits = [d for d in pad if (k := _kala(frames[d], rule.kala, city)) is not None and a <= k < b]
            add(hits[0] if hits else day_of((a + b) / 2), rule.key)
        if tithi == 11:  # Shukla Ekadashi while the Sun is in Dhanus
            d = day_of(a) if day_of(a) == day_of(b) else day_of(b)
            if 240 <= engine.sun(frames[d][1]) < 270:
                add(d, "vaikuntha_ekadashi")

    # Varalakshmi: last Friday in Shravana Shukla up to Purnima (Shukla 8-15 at sunrise).
    fridays = [d for d in days if d.weekday() == 4]
    for d in fridays:
        sr = frames[d][1]
        m, adhika = engine.masa(sr)
        if m == 4 and not adhika and 7 <= engine.tithi_idx(sr) <= 14:
            nxt = d + dt.timedelta(7)
            if not (nxt in frames and engine.masa(frames[nxt][1]) == (4, False)
                    and 7 <= engine.tithi_idx(frames[nxt][1]) <= 14):
                add(d, "varalakshmi")

    # Makara Sankranti: Sun enters sidereal Makara; after sunset -> next day.
    for d in days:
        _, sr, ss, sr_next, _ = frames[d]
        if engine.sun(sr) < 270 <= engine.sun(sr_next):
            a, b = sr, sr_next
            while b - a > 1e-4:
                mid = (a + b) / 2
                if engine.sun(mid) < 270:
                    a = mid
                else:
                    b = mid
            sd = d + dt.timedelta(1) if b > ss else d
            add(sd - dt.timedelta(1), "bhogi")
            add(sd, "makara_sankranti")
            add(sd + dt.timedelta(1), "kanuma")
    return out


if __name__ == "__main__":
    import sys

    city = {c.slug: c for c in engine.CITIES + [engine.City("pittsburgh", "Pittsburgh", 40.4406, -79.9959,
                                                                     "America/New_York")]}[sys.argv[1]]
    s, e = (dt.date.fromisoformat(x) for x in sys.argv[2:4])
    skip = {"ekadashi", "pradosham", "purnima", "amavasya", "sankashti", "masa_shivaratri"}
    show_all = len(sys.argv) > 4
    for d, keys in compute(city, s, e).items():
        keys = [k for k in keys if show_all or k not in skip]
        if keys:
            print(d, dt.date.fromisoformat(d).strftime("%a"), " | ".join(NAMES[k][0] for k in keys))
