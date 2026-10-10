# Panchanga Daily

A daily Telugu/English panchangam for US and Indian cities, with a calendar subscription for phones.

**Site:** https://sridharneti.github.io/panchanga-daily/

## What it shows
- **Opening line:** samvatsaram, ayanam, rutuvu, masam, paksham, tithi, varam.
- **The limbs:** tithi, nakshatram, yogam, karanam, each with its end time.
- **Sun and Moon:** sunrise, sunset, moonrise.
- **Times to avoid:** Rahu kalam, Yamagandam, Gulika, Durmuhurtam, Varjyam.
- **Good times:** Brahma muhurta, Abhijit, Amrita kalam.
- **Festivals and vratas.**
- **The day's sankalpam,** split by sandhya when the tithi changes.
- **A daily question.**

**Cities:** Lombard, Naperville, Normal, Dallas, Hyderabad, Mumbai, Kolkata, Bengaluru, Chennai.

## How it works
- **Engine:** `gen/` computes everything with Swiss Ephemeris (built-in Moshier ephemeris).
  - Lahiri ayanamsa; sunrise rule; amanta months.
  - Festival rules are in `gen/festivals.py`.
- **Monthly build:** a GitHub Actions workflow precomputes about two years of daily data (`site/data/`) and twelve months of calendar feeds (`site/cal/*.ics`), then deploys to GitHub Pages.
  - Nothing runs on a server.

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python gen/build_site.py auto      # writes site/index.html, site/data, site/cal
.venv/bin/python gen/show.py lombard 2026-10-11 te
```

## Accuracy
- **Checked against a published temple calendar for October 2026.**
  - Sunrise and the kalams agree within 1 minute.
  - Tithi, nakshatra and varjyam agree within 1–3 minutes.
- **Festival and vrata dates can differ by tradition.** For vratas, follow your family priest.

## License
- **This project:** GNU AGPL v3 (see `LICENSE`).
- **Swiss Ephemeris** (via pyswisseph) is © Astrodienst AG and used under the AGPL option of its dual license.
