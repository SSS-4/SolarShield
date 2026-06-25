# SolarShield

https://solarshield-live.streamlit.app

**A real-time space weather mission impact estimator built on live public data.**

SolarShield pulls live data from NOAA and NASA, cross-references it with the
current satellite catalog, and estimates the risk that current space weather
poses to satellites in orbit — atmospheric drag increase, radiation exposure,
and communication disruption — alongside a live aurora forecast and an
incoming-CME estimate.

---

## ⚠️ Scope & honesty

SolarShield is an **educational risk estimator**, not a validated operational
forecasting system. Risk scores are physics-based **approximations** intended
for situational awareness and learning, not for real mission decisions. CME
arrival times use a simple constant-speed model and are estimates accurate to
within several hours. The aurora map is NOAA's official OVATION forecast,
displayed directly. For authoritative space weather forecasts, consult
[NOAA's Space Weather Prediction Center](https://www.swpc.noaa.gov).

---

## What it does

- **Live solar parameters** — Kp index, solar flare class, Bz component, proton
  flux, and total IMF strength, color-coded by severity
- **Satellite risk assessment** — estimates drag increase, radiation score, and
  communication disruption for satellites in a selected group
- **Incoming CME detection** — flags Earth-directed coronal mass ejections and
  estimates arrival time and storm intensity
- **Recent solar flares** — the last 7 days of flare activity from NASA DONKI
- **Atmospheric drag model** — how current conditions increase drag by altitude
- **Live aurora forecast** — NOAA OVATION aurora probability on a 3D globe

## Data sources

- [NOAA SWPC](https://www.swpc.noaa.gov) — solar wind, Kp, flares, proton flux, aurora
- [NASA DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/) — flare and CME events
- [CelesTrak](https://celestrak.org) — live satellite orbital data (TLEs)

## How the risk models work

- **Drag increase** — approximates upper-atmosphere expansion from geomagnetic
  activity (Kp) and its effect on satellites by altitude
- **Radiation score** — combines proton flux, flare intensity, and orbit
  (altitude and inclination) into a 0–100 exposure estimate
- **Communication disruption** — estimates link-degradation probability from
  Kp, flare class, and the Bz component

These are simplified models for educational use, not operational-grade physics.

## Tech stack

Python · Streamlit · Plotly · SGP4 · NumPy · Pandas

## Running locally
```
pip install -r requirements.txt
streamlit run solar_shield.py
```
## Author

Built by Salim Saad · Aerospace Engineering · [github.com/SSS-4](https://github.com/SSS-4)

## License

MIT
