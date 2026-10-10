"""Sankalpam line for a given city and moment.

Fixed preamble and place portion come from family tradition (PLACE below);
the time portion (samvatsara ... vasara) is filled from the panchanga at the
moment of the karma, because tithi/masa can change during the day.
Gotra and name are never generated: relatives say their own.
"""
import datetime as dt

import engine
import labels as L

PREAMBLE = {
    "te": "మమ ఉపాత్త సమస్త దురితక్షయ ద్వారా శ్రీ పరమేశ్వర ముద్దిశ్య శ్రీ పరమేశ్వర ప్రీత్యర్థం "
          "శుభే శోభనే ముహూర్తే ఆద్య బ్రహ్మణః ద్వితీయ పరార్ధే {kalpa} కలియుగే ప్రథమ పాదే",
    "en": "mama upaatta samasta durita kshaya dwaaraa sri parameshwara muddisya sri parameshwara preetyartham "
          "shubhe shobhane muhoorte aadya brahmanah dwiteeya paraardhe {kalpa} kaliyuge prathama paade",
}
# Standard kalpa/manvantara wording (confirmed with the family 2026-10-10).
KALPA = {"te": "శ్వేతవరాహ కల్పే వైవస్వత మన్వంతరే", "en": "shvetavaraaha kalpe vaivasvata manvantare"}

US = {
    "te": "క్రౌంచ ద్వీపే రమణక వర్షే ఉత్తర అమెరికాయాం మిసిసిపీ మిస్సోరీ అలబామా ఇల్లినాయ్ ఇత్యాది "
          "షోడశ జీవనదీ పరివృతే",
    "en": "krauncha dweepe ramanaka varshe uttara americaayaam mississippi missouri alabama illinois ityaadi "
          "shodasha jeevanadee parivrute",
}
# TODO(confirm with Hyderabad relatives).
HYDERABAD = {
    "te": "జంబూద్వీపే భరతవర్షే భరతఖండే మేరోః దక్షిణ దిగ్భాగే శ్రీశైలస్య వాయవ్య ప్రదేశే "
          "కృష్ణా గోదావర్యోః మధ్య ప్రదేశే",
    "en": "jamboodweepe bharata varshe bharata khande meroh dakshina digbhaage srisailasya vaayavya pradeshe "
          "krishnaa godaavaryoh madhya pradeshe",
}
# Other Indian cities: the common all-India portion; the regional part varies by family.
BHARATA = {
    "te": "జంబూద్వీపే భరతవర్షే భరతఖండే మేరోః దక్షిణ దిగ్భాగే",
    "en": "jamboodweepe bharata varshe bharata khande meroh dakshina digbhaage",
}
PLACE = {"lombard": US, "naperville": US, "normal": US, "dallas": US, "hyderabad": HYDERABAD,
         "mumbai": BHARATA, "kolkata": BHARATA, "bengaluru": BHARATA, "chennai": BHARATA}

SAMVATSARA_PHRASE = {"te": "అస్మిన్ వర్తమాన వ్యావహారిక చాంద్రమానేన {} నామ సంవత్సరే",
                     "en": "asmin vartamaana vyaavahaarika chaandramaanena {} naama samvatsare"}
AYANA = {"te": ["ఉత్తరాయణే", "దక్షిణాయనే"], "en": ["uttaraayane", "dakshinaayane"]}
RITU = {"te": ["వసంత ఋతౌ", "గ్రీష్మ ఋతౌ", "వర్ష ఋతౌ", "శరదృతౌ", "హేమంత ఋతౌ", "శిశిర ఋతౌ"],
        "en": ["vasanta rutau", "greeshma rutau", "varsha rutau", "sharad rutau", "hemanta rutau", "shishira rutau"]}
MASA_STEM = {"te": ["చైత్ర", "వైశాఖ", "జ్యేష్ఠ", "ఆషాఢ", "శ్రావణ", "భాద్రపద", "ఆశ్వయుజ", "కార్తీక",
                    "మార్గశిర", "పుష్య", "మాఘ", "ఫాల్గుణ"],
             "en": ["chaitra", "vaishaakha", "jyeshtha", "aashaadha", "shraavana", "bhaadrapada", "aashvayuja",
                    "kaarteeka", "maargashira", "pushya", "maagha", "phaalguna"]}
ADHIKA = {"te": "అధిక ", "en": "adhika "}
PAKSHA = {"te": ["శుక్ల పక్షే", "కృష్ణ పక్షే"], "en": ["shukla pakshe", "krishna pakshe"]}
TITHI_STEM = {"te": ["ప్రతిపత్", "ద్వితీయా", "తృతీయా", "చతుర్థీ", "పంచమీ", "షష్ఠీ", "సప్తమీ", "అష్టమీ",
                     "నవమీ", "దశమీ", "ఏకాదశీ", "ద్వాదశీ", "త్రయోదశీ", "చతుర్దశీ", "పూర్ణిమా"],
              "en": ["pratipat", "dwiteeyaa", "triteeyaa", "chaturthee", "panchamee", "shashthee", "saptamee",
                     "ashtamee", "navamee", "dashamee", "ekaadashee", "dwaadashee", "trayodashee",
                     "chaturdashee", "poornimaa"]}
AMAVASYA = {"te": "అమావాస్యా", "en": "amaavaasyaa"}
VASARA = {"te": ["సోమ", "భౌమ", "బుధ", "గురు", "శుక్ర", "శని", "భాను"],  # Monday first
          "en": ["soma", "bhauma", "budha", "guru", "shukra", "shani", "bhaanu"]}
CLOSING = {"te": "శుభ నక్షత్రే శుభ యోగే శుభ కరణే ఏవంగుణ విశేషణ విశిష్టాయాం శుభ తిథౌ",
           "en": "shubha nakshatre shubha yoge shubha karane evamguna visheshana vishishtaayaam shubha tithau"}


def build(city: engine.City, day: dt.date, at: dt.datetime, lang: str, d: dict | None = None) -> str:
    jd = engine.jd_of(at)
    t = engine.tithi_idx(jd)
    m, adhika = engine.masa(jd)
    d = d or engine.compute_day(day, city)
    tithi = AMAVASYA[lang] if t == 29 else TITHI_STEM[lang][t % 15]
    parts = [
        PREAMBLE[lang].format(kalpa=KALPA[lang]),
        PLACE[city.slug][lang],
        SAMVATSARA_PHRASE[lang].format(L.SAMVATSARA[lang][d["samvatsara"]]),
        AYANA[lang][d["ayana"]],
        RITU[lang][m // 2],
        (ADHIKA[lang] if adhika else "") + MASA_STEM[lang][m] + (" మాసే" if lang == "te" else " maase"),
        PAKSHA[lang][0 if t < 15 else 1],
        tithi + (" తిథౌ" if lang == "te" else " tithau"),
        VASARA[lang][d["vara"]] + (" వాసరే" if lang == "te" else " vaasare"),
        CLOSING[lang],
    ]
    return ", ".join(parts)


if __name__ == "__main__":
    import sys
    from zoneinfo import ZoneInfo

    city = {c.slug: c for c in engine.CITIES}[sys.argv[1]]
    day = dt.date.fromisoformat(sys.argv[2])
    tz = ZoneInfo(city.tz)
    d = engine.compute_day(day, city)
    for label, iso in [("Pratah (sunrise)", d["sunrise"]), ("Madhyahnika (midday)", d["midday"]),
                       ("Sayam (sunset)", d["sunset"])]:
        at = dt.datetime.fromisoformat(iso)
        print(f"--- {label} {at:%H:%M}")
        for lang in ("en", "te"):
            print(build(city, day, at, lang).split(", ", 3)[3])
