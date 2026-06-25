# ============================================
# SolarShield — Space Weather Mission Impact Analyzer
# Author: Salim Saad
# GitHub: github.com/SSS-4
# License: MIT
# Built: 2026
# ============================================

import streamlit as st
import os
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from sgp4.api import Satrec, jday

st.set_page_config(
    page_title="SolarShield",
    page_icon="\u2600\ufe0f",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
  [data-testid="stAppViewContainer"] { background: #070B12; }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  .ss-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 32px; border-bottom: 0.5px solid #16202E; background: #070B12;
  }
  .ss-logo { font-size: 18px; font-weight: 600; color: #4FC3F7; letter-spacing: 3px; }
  .ss-logo em { color: #6A8CAE; font-style: normal; font-weight: 300; }
  .ss-tagline { font-size: 12px; color: #3E5267; letter-spacing: 0.05em; }

  .metric-card {
    background: #0C131D; border: 0.5px solid #16202E;
    border-radius: 6px; padding: 16px 16px 14px; margin-bottom: 8px;
    position: relative; overflow: hidden;
  }
  .metric-card .accent {
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
  }
  .metric-label {
    font-size: 10px; color: #3E5267; margin-bottom: 8px;
    letter-spacing: 0.1em; text-transform: uppercase;
  }
  .metric-value {
    font-size: 24px; font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
  }
  .metric-sub { font-size: 11px; margin-top: 4px; letter-spacing: 0.03em; }

  .panel-header {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; background: #0C131D;
    border: 0.5px solid #16202E; border-radius: 6px 6px 0 0;
    border-bottom: 1px solid #1C2A3C;
  }
  .panel-header .ph-icon { font-size: 13px; color: #4FC3F7; }
  .panel-header .ph-title {
    font-size: 10px; color: #6A8CAE; letter-spacing: 0.14em;
    text-transform: uppercase; font-weight: 500;
  }
  .panel-body {
    border: 0.5px solid #16202E; border-top: none;
    border-radius: 0 0 6px 6px; padding: 14px 14px 4px;
    margin-bottom: 18px; background: #090F18;
  }
</style>
""", unsafe_allow_html=True)

def panel_header(icon, title):
    """Render an ops-console style section header strip."""
    st.markdown(f"""
    <div class="panel-header">
      <span class="ph-icon">{icon}</span>
      <span class="ph-title">{title}</span>
    </div>""", unsafe_allow_html=True)

# ============================================================
# WELCOME / DISCLAIMER GATE
# ============================================================
if 'entered' not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.markdown("""
    <style>
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      .welcome-wrap {
        min-height: 78vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
        animation: fadeIn 1.4s ease-out;
      }
      .welcome-logo {
        font-size: 46px; font-weight: 600; color: #4FC3F7;
        letter-spacing: 8px; margin-bottom: 4px;
      }
      .welcome-logo em { color: #6A8CAE; font-style: normal; font-weight: 300; }
      .welcome-sub {
        font-size: 14px; color: #6A8CAE; letter-spacing: 0.06em;
        margin-bottom: 36px;
      }
      .welcome-disclaimer {
        max-width: 540px; background: #0C131D;
        border: 0.5px solid #16202E; border-left: 3px solid #E8C547;
        border-radius: 6px; padding: 18px 22px; margin-bottom: 32px;
      }
      .welcome-disclaimer .dh {
        font-size: 11px; color: #E8C547; letter-spacing: 0.12em;
        text-transform: uppercase; margin-bottom: 8px; font-weight: 500;
      }
      .welcome-disclaimer .dt {
        font-size: 13px; color: #8FA6BD; line-height: 1.6;
      }
    </style>
    <div class="welcome-wrap">
      <div class="welcome-logo">SOLAR<em>SHIELD</em></div>
      <div class="welcome-sub">space weather mission impact analyzer</div>
      <div class="welcome-disclaimer">
        <div class="dh">&#9888; simulator &amp; estimator only</div>
        <div class="dt">
          SolarShield is an educational space-weather <b>risk estimator</b> built
          on live public data from NOAA and NASA. It is <b>not a validated
          operational forecasting system</b> and must not be used for real mission
          decisions. For authoritative forecasts, consult NOAA's Space Weather
          Prediction Center.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("Enter SolarShield  \u2192", use_container_width=True):
            st.session_state.entered = True
            st.rerun()
    st.stop()

# ============================================================
# DATA FETCHERS
# ============================================================

@st.cache_data(ttl=300)
def fetch_solar_wind():
    try:
        url  = "https://services.swpc.noaa.gov/products/solar-wind/mag-5-minute.json"
        r    = requests.get(url, timeout=15)
        data = r.json()
        latest = data[-1]
        return {'bz': float(latest[3]), 'bt': float(latest[6]), 'time': latest[0]}
    except:
        return {'bz': 0, 'bt': 0, 'time': 'unavailable'}

@st.cache_data(ttl=300)
def fetch_kp_index():
    try:
        url  = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        r    = requests.get(url, timeout=15)
        data = r.json()
        return float(data[-1][1])
    except:
        return 0.0

@st.cache_data(ttl=300)
def fetch_xray_flux():
    try:
        url  = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"
        r    = requests.get(url, timeout=15)
        data = r.json()
        if data:
            latest = data[-1]
            return {
                'class':     latest.get('max_class', 'A1.0'),
                'intensity': float(latest.get('max_xrlong', 1e-9)),
                'time':      latest.get('begin_time', 'unknown')
            }
    except:
        pass
    return {'class': 'A1.0', 'intensity': 1e-9, 'time': 'unknown'}

@st.cache_data(ttl=300)
def fetch_proton_flux():
    try:
        url  = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
        r    = requests.get(url, timeout=15)
        data = r.json()
        if data:
            return float(data[-1].get('flux', 0.1))
    except:
        pass
    return 0.1

@st.cache_data(ttl=300)
def fetch_recent_flares():
    try:
        end   = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
        url   = (f"https://api.nasa.gov/DONKI/FLR?"
                 f"startDate={start.strftime('%Y-%m-%d')}"
                 f"&endDate={end.strftime('%Y-%m-%d')}"
                 f"&api_key=DEMO_KEY")
        r    = requests.get(url, timeout=15)
        data = r.json()
        return data[:10] if data else []
    except:
        return []

@st.cache_data(ttl=3600)
def fetch_tles(group='stations'):
    """
    Read the daily TLE snapshot saved locally by the GitHub Actions job
    (fetch_tles.py). This avoids calling CelesTrak from Streamlit's
    rate-limited cloud IP. If the local file is missing (e.g. running
    before the first scheduled fetch), fall back to a direct CelesTrak
    request as a last resort.
    """
    import os
    path = os.path.join("data", f"{group}.tle")
    # Primary: read the pre-fetched local snapshot
    try:
        with open(path) as f:
            text = f.read()
        if len(text) > 100:
            lines = text.strip().splitlines()
            sats  = []
            for i in range(0, len(lines)-2, 3):
                sats.append((lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()))
            return sats
    except Exception:
        pass
    # Fallback: try CelesTrak directly (works locally; may be blocked on cloud)
    try:
        url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle"
        r = requests.get(url, timeout=30, headers={'User-Agent': 'SolarShield/1.0'})
        if r.status_code == 200 and len(r.text) > 100:
            lines = r.text.strip().splitlines()
            sats  = []
            for i in range(0, len(lines)-2, 3):
                sats.append((lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()))
            return sats
    except Exception:
        pass
    return []

def get_tle_freshness():
    """Read when the TLE snapshot was last updated, for honest labeling."""
    try:
        with open(os.path.join("data", "last_updated.txt")) as f:
            return f.read().strip()
    except Exception:
        return "live (direct)"

# ============================================================
# RISK MODELS
# ============================================================

def flare_class_to_number(flare_class):
    scale = {'A': 1e-8, 'B': 1e-7, 'C': 1e-6, 'M': 1e-5, 'X': 1e-4}
    if not flare_class or len(flare_class) < 2:
        return 1e-9
    letter = flare_class[0].upper()
    try:
        number = float(flare_class[1:])
    except:
        number = 1.0
    return scale.get(letter, 1e-9) * number

def compute_drag_increase(kp, altitude_km):
    kp_factor  = np.exp(0.5 * kp)
    alt_factor = np.exp(-(altitude_km - 200) / 100)
    return min((kp_factor - 1) * alt_factor * 100, 500)

def compute_radiation_risk(proton_flux, flare_intensity, altitude_km, inclination_deg):
    proton_score = min(np.log10(max(proton_flux, 0.1) + 1) * 20, 40)
    flare_score  = min(np.log10(max(flare_intensity, 1e-9) / 1e-9) * 5, 30)
    orbit_score  = min((altitude_km / 1000) * 5 + (inclination_deg / 90) * 10, 30)
    return min(proton_score + flare_score + orbit_score, 100)

def compute_comm_disruption(kp, flare_class, bz):
    kp_prob    = min(kp * 8, 50)
    flare_prob = min(np.log10(flare_class_to_number(flare_class) / 1e-9 + 1) * 8, 30)
    bz_prob    = min(max(-bz, 0) * 2, 20)
    return min(kp_prob + flare_prob + bz_prob, 100)

def get_satellite_orbit(l2):
    try:
        inclination = float(l2[8:16])
        mean_motion = float(l2[52:63])
        mu  = 398600.4418
        n   = mean_motion * 2 * np.pi / 86400
        a   = (mu / n**2) ** (1/3)
        return a - 6371, inclination
    except:
        return 400, 51.6

def assess_satellite_risk(name, l1, l2, kp, proton_flux, flare_data, solar_wind):
    altitude, inclination = get_satellite_orbit(l2)
    flare_class     = flare_data.get('class', 'A1.0')
    flare_intensity = flare_class_to_number(flare_class)
    bz              = solar_wind.get('bz', 0)
    drag_pct  = compute_drag_increase(kp, altitude)
    rad_score = compute_radiation_risk(proton_flux, flare_intensity, altitude, inclination)
    comm_pct  = compute_comm_disruption(kp, flare_class, bz)
    overall   = (drag_pct/5 + rad_score + comm_pct) / 3
    if overall >= 70:   risk_level = 'CRITICAL'
    elif overall >= 45: risk_level = 'HIGH'
    elif overall >= 20: risk_level = 'MEDIUM'
    else:               risk_level = 'LOW'
    return {
        'name': name, 'altitude': altitude, 'inclination': inclination,
        'drag_pct': drag_pct, 'rad_score': rad_score, 'comm_pct': comm_pct,
        'overall': overall, 'risk_level': risk_level,
    }

def get_status(kp, flare_class, proton_flux, bz):
    fi = flare_class_to_number(flare_class)
    if kp >= 7 or fi >= 1e-4 or proton_flux >= 1000 or bz <= -20:
        return 'SEVERE STORM', '#FF5555'
    elif kp >= 5 or fi >= 1e-5 or proton_flux >= 100 or bz <= -10:
        return 'MODERATE STORM', '#FF9E40'
    elif kp >= 3 or fi >= 1e-6 or proton_flux >= 10:
        return 'MINOR ACTIVITY', '#E8C547'
    return 'QUIET', '#3FB97D'

@st.cache_data(ttl=1800)
def fetch_cme_data():
    """Fetch coronal mass ejection (CME) data from NASA DONKI."""
    try:
        end   = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
        url   = (f"https://api.nasa.gov/DONKI/CMEAnalysis?"
                 f"startDate={start.strftime('%Y-%m-%d')}"
                 f"&endDate={end.strftime('%Y-%m-%d')}"
                 f"&mostAccurateOnly=true&speed=500&halfAngle=45"
                 f"&catalog=ALL&api_key=DEMO_KEY")
        r    = requests.get(url, timeout=15)
        data = r.json()
        return data if data else []
    except:
        return []

def predict_cme_arrival(cme):
    """Estimate CME Earth-arrival using a constant-speed model (an estimate)."""
    try:
        speed    = float(cme.get('speed', 500))
        distance = 149597870
        travel_h = distance / (speed * 3600)
        start_str = cme.get('startTime', '')
        if not start_str:
            return None
        start_time = datetime.strptime(
            start_str[:19], '%Y-%m-%dT%H:%M:%S'
        ).replace(tzinfo=timezone.utc)
        arrival    = start_time + timedelta(hours=travel_h)
        now        = datetime.now(timezone.utc)
        hours_away = (arrival - now).total_seconds() / 3600
        if speed >= 2000:   predicted_kp = 8
        elif speed >= 1500: predicted_kp = 7
        elif speed >= 1000: predicted_kp = 6
        elif speed >= 750:  predicted_kp = 5
        elif speed >= 500:  predicted_kp = 4
        else:               predicted_kp = 3
        return {'speed': speed, 'arrival': arrival, 'hours_away': hours_away,
                'predicted_kp': predicted_kp, 'start_time': start_time}
    except:
        return None

@st.cache_data(ttl=1800)
def fetch_aurora_data():
    """Fetch NOAA OVATION aurora forecast (real NOAA forecast product)."""
    try:
        url  = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
        r    = requests.get(url, timeout=15)
        data = r.json()
        coords = data.get('coordinates', [])
        lats, lons, probs = [], [], []
        for i, point in enumerate(coords):
            if i % 5 != 0:
                continue
            lon, lat, prob = point[0], point[1], point[2]
            if prob > 5:
                if lon > 180:
                    lon -= 360
                lats.append(lat); lons.append(lon); probs.append(prob)
        return {'lats': lats, 'lons': lons, 'probs': probs,
                'forecast_time': data.get('Forecast Time', 'unknown')}
    except:
        return {'lats': [], 'lons': [], 'probs': [], 'forecast_time': 'unavailable'}

# ============================================================
# MAIN APP
# ============================================================

now_str = datetime.now(timezone.utc).strftime('%H:%M UTC')
st.markdown(f"""
<div class="ss-nav">
  <div class="ss-logo">SOLAR<em>SHIELD</em></div>
  <div class="ss-tagline">space weather mission impact analyzer
    &nbsp;&nbsp;&middot;&nbsp;&nbsp;
    <span style="color:#3FB97D;">&#9679; LIVE</span>
    <span style="color:#3E5267;">&nbsp;{now_str}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='padding: 20px 32px 0;'>", unsafe_allow_html=True)

with st.spinner("Fetching live space weather data from NOAA & NASA..."):
    solar_wind  = fetch_solar_wind()
    kp          = fetch_kp_index()
    flare_data  = fetch_xray_flux()
    proton_flux = fetch_proton_flux()
    flares      = fetch_recent_flares()

status, status_color = get_status(kp, flare_data['class'], proton_flux, solar_wind['bz'])

st.markdown(f"""
<div style="background:#0C131D; border:0.5px solid {status_color};
     border-radius:6px; padding:14px 20px; margin-bottom:20px;
     display:flex; align-items:center; justify-content:space-between;">
  <span style="font-size:13px; color:{status_color}; font-weight:600;
        letter-spacing:0.08em;">
    &#9679; SPACE WEATHER STATUS: {status}
  </span>
  <span style="font-size:11px; color:#3E5267; letter-spacing:0.05em;">
    Updated {now_str} &middot; Source: NOAA SWPC &middot; NASA DONKI
  </span>
</div>
""", unsafe_allow_html=True)

# ---- CME Arrival Predictor ----
with st.spinner("Checking for incoming CMEs..."):
    cmes = fetch_cme_data()

incoming = []
for cme in cmes:
    pred = predict_cme_arrival(cme)
    if pred and pred['hours_away'] > 0:
        incoming.append(pred)
incoming.sort(key=lambda x: x['hours_away'])

if incoming:
    next_cme    = incoming[0]
    kp_pred     = next_cme['predicted_kp']
    cme_color   = '#FF5555' if kp_pred >= 7 else '#FF9E40' if kp_pred >= 5 else '#E8C547'
    storm_label = ('SEVERE storm' if kp_pred >= 7 else
                   'STRONG storm' if kp_pred >= 5 else 'Minor storm')
    hrs         = next_cme['hours_away']
    arrival_str = next_cme['arrival'].strftime('%b %d, %H:%M UTC')
    st.markdown(f"""
    <div style="background:#0C131D; border:0.5px solid {cme_color};
         border-left:3px solid {cme_color};
         border-radius:6px; padding:14px 20px; margin-bottom:20px;">
      <span style="font-size:13px; color:{cme_color}; font-weight:600;
            letter-spacing:0.06em;">&#9888; INCOMING CME DETECTED</span>
      <span style="font-size:12px; color:#C8D6E5; margin-left:16px;">
        Arrival in {hrs:.0f} h ({arrival_str}) &middot;
        {next_cme['speed']:.0f} km/s &middot;
        Predicted Kp {kp_pred} ({storm_label})
      </span>
      <div style="font-size:10px; color:#3E5267; margin-top:6px;
           letter-spacing:0.04em;">
        Constant-speed estimate &middot; NASA DONKI
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:#0C131D; border:0.5px solid #1C2A3C;
         border-left:3px solid #3FB97D;
         border-radius:6px; padding:14px 20px; margin-bottom:20px;">
      <span style="font-size:13px; color:#3FB97D; font-weight:600;
            letter-spacing:0.06em;">&#9679; NO INCOMING CMEs</span>
      <span style="font-size:12px; color:#3E5267; margin-left:16px;">
        No Earth-directed coronal mass ejections detected in the last 7 days
      </span>
    </div>
    """, unsafe_allow_html=True)

# ---- Live parameters panel ----
panel_header("\u25C9", "live solar parameters")
st.markdown('<div class="panel-body">', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
kp_col     = '#FF5555' if kp>=7 else '#FF9E40' if kp>=5 else '#E8C547' if kp>=3 else '#3FB97D'
bz_col     = '#FF5555' if solar_wind['bz']<=-20 else '#FF9E40' if solar_wind['bz']<=-10 else '#E8C547' if solar_wind['bz']<=-5 else '#3FB97D'
prot_col   = '#FF5555' if proton_flux>=1000 else '#FF9E40' if proton_flux>=100 else '#E8C547' if proton_flux>=10 else '#3FB97D'
kp_label   = 'Severe storm' if kp>=7 else 'Strong storm' if kp>=5 else 'Minor storm' if kp>=3 else 'Quiet'
bz_label   = 'Storm driver' if solar_wind['bz']<=-10 else 'Elevated' if solar_wind['bz']<=-5 else 'Normal'
prot_label = 'Radiation storm' if proton_flux>=1000 else 'Elevated' if proton_flux>=10 else 'Normal'

for col, label, value, sub, color in [
    (c1, 'Kp Index',     f"{kp:.1f}",                  kp_label, kp_col),
    (c2, 'Solar Flare',  flare_data['class'],          flare_data['time'][:10] if flare_data['time'] != 'unknown' else 'No recent flare', '#4FC3F7'),
    (c3, 'Bz Component', f"{solar_wind['bz']:.1f} nT", bz_label, bz_col),
    (c4, 'Proton Flux',  f"{proton_flux:.1f} pfu",     prot_label, prot_col),
    (c5, 'Bt Field',     f"{solar_wind['bt']:.1f} nT", 'Total IMF strength', '#C8D6E5'),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="accent" style="background:{color};"></div>
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="color:{color};">{value}</div>
          <div class="metric-sub" style="color:{color};">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---- Main columns ----
col_left, col_right = st.columns([1.2, 1])

with col_left:
    panel_header("\u25C8", "satellite risk assessment")
    st.markdown('<div class="panel-body">', unsafe_allow_html=True)

    group_map  = {
        "Space Stations": "stations",
        "Starlink":       "starlink",
        "Weather Sats":   "weather",
        "GPS":            "gps-ops",
        "Galileo":        "galileo",
    }
    group_name = st.selectbox("Satellite group", list(group_map.keys()), label_visibility="collapsed")
    group_id   = group_map[group_name]

    with st.spinner("Computing satellite risk..."):
        sat_data = fetch_tles(group_id)
        risks    = []
        for name, l1, l2 in sat_data:
            try:
                risks.append(assess_satellite_risk(name, l1, l2, kp, proton_flux, flare_data, solar_wind))
            except:
                continue
        risks.sort(key=lambda x: x['overall'], reverse=True)

    critical = sum(1 for r in risks if r['risk_level']=='CRITICAL')
    high     = sum(1 for r in risks if r['risk_level']=='HIGH')
    medium   = sum(1 for r in risks if r['risk_level']=='MEDIUM')
    low      = sum(1 for r in risks if r['risk_level']=='LOW')

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Critical", critical)
    mc2.metric("High",     high)
    mc3.metric("Medium",   medium)
    mc4.metric("Low",      low)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    if risks:
        df = pd.DataFrame([{
            'Satellite':  r['name'],
            'Alt (km)':   f"{r['altitude']:.0f}",
            'Risk':       r['risk_level'],
            'Drag +%':    f"{r['drag_pct']:.0f}%",
            'Radiation':  f"{r['rad_score']:.0f}/100",
            'Comm Loss':  f"{r['comm_pct']:.0f}%",
            'Score':      f"{r['overall']:.0f}",
        } for r in risks[:15]])
        st.dataframe(df, use_container_width=True, height=360)

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    panel_header("\u25B0", "risk distribution")
    st.markdown('<div class="panel-body">', unsafe_allow_html=True)
    if risks:
        colors = {'CRITICAL':'#FF5555','HIGH':'#FF9E40','MEDIUM':'#E8C547','LOW':'#3FB97D'}
        fig    = go.Figure()
        for level, color in colors.items():
            subset = [r for r in risks if r['risk_level']==level][:5]
            if subset:
                fig.add_trace(go.Bar(
                    name=level,
                    x=[r['name'][:12] for r in subset],
                    y=[r['overall'] for r in subset],
                    marker_color=color,
                    text=[f"{r['overall']:.0f}" for r in subset],
                    textposition='auto',
                ))
        fig.update_layout(
            barmode='group', height=200,
            paper_bgcolor='#090F18', plot_bgcolor='#090F18',
            font=dict(color='#C8D6E5', size=10, family='JetBrains Mono'),
            margin=dict(l=0, r=0, t=6, b=0),
            legend=dict(bgcolor='#0C131D', bordercolor='#16202E', borderwidth=0.5),
            xaxis=dict(gridcolor='#16202E'),
            yaxis=dict(gridcolor='#16202E', title='Risk score'),
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    panel_header("\u2600", "recent solar flares \u00b7 7 days")
    st.markdown('<div class="panel-body">', unsafe_allow_html=True)
    if flares:
        flare_rows = []
        for f in flares[:8]:
            cls  = f.get('classType', '?')
            time = f.get('beginTime', '')[:16] if f.get('beginTime') else ''
            fi   = flare_class_to_number(cls)
            sev  = 'X-class' if fi>=1e-4 else 'M-class' if fi>=1e-5 else 'C-class' if fi>=1e-6 else 'Minor'
            flare_rows.append({'Class': cls, 'Time (UTC)': time, 'Severity': sev})
        st.dataframe(pd.DataFrame(flare_rows), use_container_width=True, height=200)
    else:
        st.success("No significant flares in the past 7 days.")
    st.markdown('</div>', unsafe_allow_html=True)

    panel_header("\u2248", "atmospheric drag vs altitude")
    st.markdown('<div class="panel-body">', unsafe_allow_html=True)
    altitudes   = np.linspace(200, 800, 100)
    drag_values = [compute_drag_increase(kp, a) for a in altitudes]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=altitudes, y=drag_values, mode='lines',
        line=dict(color='#4FC3F7', width=2),
        fill='tozeroy', fillcolor='rgba(79,195,247,0.08)',
    ))
    fig2.add_vline(x=400, line_dash='dash', line_color='#3E5267',
                   annotation_text='ISS ~400km', annotation_font_color='#3E5267')
    fig2.update_layout(
        height=170, paper_bgcolor='#090F18', plot_bgcolor='#090F18',
        font=dict(color='#C8D6E5', size=10, family='JetBrains Mono'),
        margin=dict(l=0, r=0, t=6, b=0),
        xaxis=dict(title='Altitude (km)', gridcolor='#16202E'),
        yaxis=dict(title='Drag +%', gridcolor='#16202E'),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Aurora Probability Map ----
panel_header("\u25D0", "live aurora forecast \u00b7 NOAA OVATION (~30 min ahead)")
st.markdown('<div class="panel-body">', unsafe_allow_html=True)

with st.spinner("Fetching live aurora forecast..."):
    aurora = fetch_aurora_data()

if aurora['lats']:
    fig_aurora = go.Figure()
    fig_aurora.add_trace(go.Scattergeo(
        lat=aurora['lats'], lon=aurora['lons'], mode='markers',
        marker=dict(
            size=4, color=aurora['probs'],
            colorscale=[[0, 'rgba(0,90,120,0.3)'], [0.5, 'rgba(0,200,180,0.7)'], [1, 'rgba(150,255,220,1)']],
            cmin=0, cmax=100,
            colorbar=dict(
                title=dict(text='Aurora %', font=dict(color='#6A8CAE')),
                tickfont=dict(color='#6A8CAE')),
        ),
        hovertemplate="Aurora probability: %{marker.color:.0f}%<br>%{lat:.0f}\u00b0, %{lon:.0f}\u00b0<extra></extra>",
    ))
    fig_aurora.update_geos(
        projection_type="orthographic",
        showland=True, landcolor="#0C131D",
        showocean=True, oceancolor="#070B12",
        showcoastlines=True, coastlinecolor="#1C2A3C",
        bgcolor="#090F18",
    )
    fig_aurora.update_layout(
        height=420, paper_bgcolor="#090F18",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_aurora, use_container_width=True)
    st.markdown(f"""
    <div style="font-size:11px; color:#3E5267; margin-top:4px;
         letter-spacing:0.04em;">
      Forecast time {aurora['forecast_time']} &middot; NOAA OVATION product, displayed directly. Drag the globe to rotate.
    </div>""", unsafe_allow_html=True)
else:
    st.info("Aurora forecast data is currently unavailable from NOAA.")
st.markdown('</div>', unsafe_allow_html=True)

# ---- Methodology & footer ----
st.markdown("""
<div style="background:#0C131D; border:0.5px solid #16202E; border-radius:6px;
     padding:14px 20px; margin-top:8px;">
  <div style="font-size:10px; color:#3E5267; letter-spacing:0.12em;
       text-transform:uppercase; margin-bottom:8px; font-weight:500;">
    methodology & scope
  </div>
  <div style="font-size:12px; color:#6A8CAE; line-height:1.6;">
    SolarShield is an integrated space-weather risk <b>estimator</b> built on
    live public data. It is <b>not a validated forecasting system</b>.
    Risk scores combine reasonable physics-based approximations of atmospheric
    drag, radiation exposure, and communication disruption &mdash; intended for
    situational awareness and educational use, not operational mission decisions.
    CME arrival times use a constant-speed model and are estimates accurate to
    within several hours. The aurora forecast is NOAA's official OVATION product,
    displayed directly. For authoritative forecasts, consult NOAA's Space Weather
    Prediction Center directly.
  </div>
</div>
<div style="text-align:center; padding:16px; font-size:11px; color:#27384A;
     letter-spacing:0.05em;">
  SolarShield &middot; Live data: NOAA SWPC &middot; NASA DONKI &middot; CelesTrak &middot; Built by Salim Saad &middot; github.com/SSS-4
</div>""", unsafe_allow_html=True)
