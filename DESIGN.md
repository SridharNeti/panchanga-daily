# Panchanga Daily: design (draft 2026-10-10)

## Goal
A free static site showing today's panchanga for a chosen city. It includes a one-question daily puzzle, a daily summary on relatives' iPhones, and the same data for the Home Assistant dashboard. Built with Claude; runs with no Claude/API at runtime.

## Architecture
```
GitHub repo (public, AGPL-3.0 because PyJHora/Swiss Ephemeris are AGPL)
 ├─ gen/        Python + PyJHora: precompute 400 days × N cities
 │    → site/data/<city>/<yyyy-mm>.json
 │    → site/cal/<city>.ics          (iPhone calendar subscription)
 ├─ site/       plain HTML/CSS/JS, PWA manifest, no framework, no server
 └─ .github/workflows/
      build.yml   weekly: regenerate data, deploy to GitHub Pages
      notify.yml  daily ~5:30 AM per region: post summary to Telegram/ntfy (optional)
```
- **Hosting:** GitHub Pages, free for a public repo. URL is `<user>.github.io/panchanga-daily`, and a custom domain is optional. Cloudflare Pages is the alternative if the repo must stay private.
- **Why precompute:** no server, instant load, works offline, and the iPhone calendar has a year of data ahead.
- **Home Assistant:** a REST sensor reads `data/<city>/<month>.json`, so there is one engine for the site and the dashboard.

## Cities (v1)
Each city has its own timezone and sunrise. Tithi follows the sunrise rule; amanta (Telugu) months.

| City | Lat, Lon | Timezone |
|---|---|---|
| Lombard, IL | 41.888, -88.008 | America/Chicago |
| Naperville, IL | 41.750, -88.154 | America/Chicago |
| Normal, IL | 40.514, -88.991 | America/Chicago |
| Dallas, TX | 32.777, -96.797 | America/Chicago |
| Hyderabad | 17.385, 78.487 | Asia/Kolkata |

Use IANA timezones (DST handled), not fixed offsets.

## What a day shows (in this order)
1. **Samvatsara:**
   - Parabhava now. Plavanga from Ugadi, 2027-04-07 (computed for both Hyderabad and Lombard).
   - Uses the 60-year cycle and changes at Chaitra Shukla Pratipada.
2. **Ayana:**
   - Dakshinayana now. Uttarayana from Makara Sankranti (Sun enters sidereal Capricorn by sunrise on 2027-01-15 in Hyderabad).
   - Dakshinayana again from Karkataka Sankranti (around 2027-07-17).
3. **Ritu (lunar, Telugu style):**
   - Vasanta: Chaitra–Vaishakha
   - Grishma: Jyeshtha–Ashadha
   - Varsha: Shravana–Bhadrapada
   - Sharad: Ashvayuja–Kartika (starts 2026-10-11)
   - Hemanta: Margashira–Pushya
   - Shishira: Magha–Phalguna
4. **Masa:**
   - Amanta. Adhika/Nija masa labels needed (2026 had Adhika Jyeshtha).
   - Optional purnimanta name for North-Indian friends.
5. **Paksha:** Shukla / Krishna.
6. **Tithi** (with end time) and **Vara**.
- Then the five limbs, Sun and Moon, times to avoid, good times, festivals and vratas (below).
- **The five limbs:** tithi, nakshatra (with pada), yoga, karana. Each shows its end time; a second entry appears if it changes during the day.
- **Sun and Moon:** sunrise, sunset, moonrise, moonset; Moon sign.
- **Times to avoid:** Rahu kalam, Yamagandam, Gulika kalam, Durmuhurtham, Varjyam.
- **Good times:** Abhijit muhurta, Amrita kalam, Brahma muhurta.
- **Festivals and vratas:**
  - Ekadashi, Pradosham, Sankashti, Amavasya, Purnima, Masa Shivaratri.
  - Navaratri, Ugadi, Sankranti, Deepavali and similar.
  - Rule table in `gen/festivals.py`, validated by hand against a published Telugu panchangam. Its text is not copied.
- **Language:** English / తెలుగు toggle (Noto Sans Telugu); all labels from one translation table.
- **Own rules only (decided 2026-10-10):** every city shows its locally computed date; no "In India" notes.
- **Elders first:** large text, high contrast, dark mode, no ads/analytics/cookies.
- **Disclaimer:** "Computed (Lahiri, sunrise rule) for <city>. For vrata decisions follow your family priest/panchangam." 
- **Puzzle of the day:**
  - One question generated from that day's data, e.g. "Why does Navaratri start tomorrow, not today?"
  - Streak kept in localStorage.
  - Seed for the later Jyotish Quest.

## Sandhyavandanam helpers
- **Times:** Pratah sandhya, i.e. sunrise (arghya before it); Madhyahnika, i.e. local midday; Sayam sandhya, i.e. sunset.
- **Ready-made sankalpam line** in Telugu script, Sanskrit locatives:
  "…శ్రీ పరాభవ నామ సంవత్సరే, దక్షిణాయనే, శరదృతౌ, ఆశ్వయుజ మాసే, శుక్ల పక్షే, ప్రతిపద్యాం, భాను వాసరే, చిత్రా నక్షత్రే…"
  - The place portion (dvipa/desha) is left to family tradition.
  - A Telugu/Sanskrit reader must proofread the grammar tables.

## Daily stotram (add-on, phase 2)
- **Content:** one shloka a day, in Telugu and Devanagari, with a short meaning and when to recite.
  - Matched to the day: Shani on Saturday, Shiva on Pradosham/Monday, Vishnu on Ekadashi, Devi in Navaratri, plus general ones such as the post-meal netra shloka.
- **Texts:** traditional shlokas are public domain.
- **Meanings:** written fresh for this site. Never copied from WhatsApp forwards, books or sites (their translations are copyrighted).
- **Audio "read aloud":**
  - **Recommended:** a family elder records each shloka once (best pronunciation, no licensing).
  - **Fallback:** the browser's built-in speech (Telugu voice quality varies by phone).
  - Pre-generated audio from an open TTS model is an option only after checking that model's license.
- **Curation:** stotram list kept in `content/stotras/*.md`, reviewed by the family before going live.

## Calendar feed details
- **Feeds per city:**
  - `<city>-daily.ics`: one all-day event per day.
  - `<city>-festivals.ics`: festivals/vratas only, for people who find daily alerts noisy.
- **Event title:** "Śu. Pratipada · Swati · Navaratri begins" (Telugu title in the Telugu feed). The description holds the full day plus a site link.
- **Alarm:** VALARM TRIGGER:PT6H on the all-day event, which means 6 AM device-local.
  - iPhone honours it only if "Remove Alerts" is off.
  - Google Calendar ignores feed alarms, so Android users set "default notification for all-day events" on that calendar once.
- **Coverage:** rolling 24 months ahead, so the feed keeps working for a year even if the build stops.
- **Gotcha:** GitHub disables scheduled workflows after 60 days with no repo activity.
  - The weekly build commits regenerated data, which keeps it alive.
  - A monthly check reminds us to verify it.
- **Refresh:** iPhone refreshes subscriptions periodically; Google every ~8–24 h. Fine because data is precomputed.
- **Subscribe page `/subscribe`:**
  - City and language picker.
  - Buttons: iPhone (`webcal://`), Android/Google (`https://calendar.google.com/calendar/r?cid=…`), Outlook.
  - Short illustrated steps (incl. Remove Alerts), a QR code, and "how to unsubscribe".
  - You send relatives just this one link by any messenger or email.

## Push to relatives' iPhones (no app to build)
1. **Primary: calendar subscription (`.ics`).**
   - Relative taps a `webcal://…/cal/hyderabad.ics` link once.
   - They get one all-day event per day, e.g. "Ashvayuja Śu. Pratipada · Swati · Navaratri begins".
   - An alarm fires at 6 AM local time.
   - No app, no account, nothing to run. Updates through the calendar refresh.
   - Note: iOS has a "Remove Alerts" toggle for subscribed calendars, which must be off.
2. **Optional: Telegram channel.**
   - A free bot, posted by the daily GitHub Action.
   - Relatives join the channel. Good for a short message plus a site link.
3. **Optional: ntfy app** (free, topic-based) as an alternative to Telegram.
- **Not WhatsApp:** its Business API costs money and needs approval. Forwarding the Telegram text by hand works.

## Conventions chosen
- **Sunrise:** upper limb + refraction (matches phone weather apps and most online panchangams). The "disc-centre" traditional sunrise is ~3–5 min later.

## Licensing
- **AGPL code (PyJHora, Swiss Ephemeris):** keep the repo public under AGPL.
- **Festival data:** no copied panchangam text or data.
- **Personal data:** no family charts or birth data anywhere.

## Milestones
1. Generator for 1 city with JSON output, checked against a known panchangam for 10 dates.
2. Static page and GitHub Pages deploy.
3. `.ics` feed and a test on your iPhone.
4. More cities, Telugu labels, festivals.
5. Puzzle, Telegram (optional), Home Assistant card.

## Validation log
- **2026-10-10:** compared with the SV Temple Pittsburgh 2026–27 calendar (October, 31 days); differences are ours minus temple.
  - Sunrise, sunset, Rahu kalam, Yamagandam, Gulika: 0 to +1 min (rounding).
  - Tithi end: −2 to +1 min (mean −1.5). Nakshatra end: −3 to −1 min (mean −2.0, n=20).
  - Likely an ephemeris or ΔT convention difference; within the usual spread between printed panchangams.
- **Not yet validated:** Varjyam (temple lists it, so it's the next check), festivals, durmuhurtam (temple doesn't list it).
- **Temple "Yoga Sid/Amr/Mar"** is Amrita-Siddha/Marana yoga (Anandadi type), not the 27 nitya yogas.
- **Script:** `validation/compare_svt.py`. Raw temple text stays in `validation/raw/` (gitignored, their copyright).
- **2026-10-10 festivals** (`gen/festivals.py`, Oct 2026 – Apr 2027): checked against the dates the temple prints.
  - Same date: Vijayadashami Oct 20, Vaikuntha Ekadashi Dec 20, Ratha Saptami Feb 13, Ugadi Apr 7.
  - **Sankranti differs:**
    - Ingress is 2027-01-14 21:10 IST, which is 9:40 AM CST.
    - Local rule puts Makara Sankranti on Jan 14 in the US and Jan 15 in India.
    - The temple uses Jan 15 (the India date).
  - **Kartika Purnima:** the temple's Nov 25 is Pancharatra Kartika Deepam (Krittika-based), a different rule.
