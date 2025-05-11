from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# API credentials from env
OPENWEATHER_API_KEY     = os.getenv("OPENWEATHER_API_KEY")
TIDES_API_KEY = os.getenv("TIDES_API_KEY")
ASTRO_ID      = os.getenv("ASTRO_APP_ID")
ASTRO_SECRET  = os.getenv("ASTRO_APP_SECRET")

def get_auth_header():
    token = base64.b64encode(f"{ASTRO_ID}:{ASTRO_SECRET}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

# in app.py, replace your existing /weather and /forecast with the two functions below

@app.route('/weather')
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat, lon, OPENWEATHER_API_KEY]):
        return jsonify({"error": "Missing params or API key"}), 400

    # call One Call 3.0 but only pull the 'current' block
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly,daily,alerts",
        "units": "imperial",
        "appid": OPENWEATHER_API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json().get("current", {})

    # reshape to match your front-end’s expectations:
    return jsonify({
        "weather": data.get("weather", []),
        "main": {
            "temp": data.get("temp"),
            "humidity": data.get("humidity")
        },
        "wind": {
            "speed": data.get("wind_speed"),
            "deg": data.get("wind_deg")
        },
        "rain": data.get("rain", {}),              # e.g. {"1h": 0.15}
        "sys": {
            "sunrise": data.get("sunrise"),         # UNIX timestamp
            "sunset": data.get("sunset")
        }
    })


@app.route('/forecast')
def forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat, lon, OPENWEATHER_API_KEY]):
        return jsonify({"error": "Missing params or API key"}), 400

    # call One Call 3.0 but only pull the 'daily' block
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "current,minutely,hourly,alerts",
        "units": "imperial",
        "appid": OPENWEATHER_API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    daily = r.json().get("daily", [])

    # build a list so your front-end’s `forecast.list[i].main.temp_max` still works
    forecast_list = []
    for day in daily[:8]:   # up to 8 days
        temps = day.get("temp", {})
        forecast_list.append({
            "main": {
                "temp_max": temps.get("max"),
                "temp_min": temps.get("min")
            }
        })

    return jsonify({"list": forecast_list})


@app.route('/air-pollution')
def air_pollution():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat,lon,OPENWEATHER_API_KEY]):
        return jsonify({"error":"Missing params or API key"}),400
    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = dict(lat=lat, lon=lon, appid=OPENWEATHER_API_KEY)
    r = requests.get(url, params=params); r.raise_for_status()
    return jsonify(r.json())

@app.route('/tides')
def tides():
    lat  = request.args.get('lat')
    lon  = request.args.get('lon')
    date = request.args.get('date', 'today')    # YYYY-MM-DD or "today"
    days = request.args.get('days')              # optional integer 1–7

    if not all([lat, lon, TIDES_API_KEY]):
        return jsonify({"error": "Missing params or API key"}), 400

    # build v3 parameters: include both heights & extremes
    params = {
        "lat": lat,
        "lon": lon,
        "key": TIDES_API_KEY,
        "heights": "",      # flag to return the height time‐series
        "extremes": "",     # flag to return low/high tide events
        "date": date
    }
    if days:
        params["days"] = days

    url = "https://www.worldtides.info/api/v3"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return jsonify(resp.json())

@app.route('/moon-phase', methods=['POST'])
def moon_phase():
    data = request.json.get('observer') or {}
    url = "https://api.astronomyapi.com/api/v2/bodies/positions"
    # AstronomyAPI body for phase
    payload = {
      "observedAt": data.get("date"),
      "latitude": data.get("latitude"),
      "longitude": data.get("longitude"),
      "format": "JSON"
    }
    headers = get_auth_header()
    r = requests.post("https://api.astronomyapi.com/api/v2/bodies/phase", 
                      json=payload, headers=headers)
    r.raise_for_status()
    return jsonify(r.json())

@app.route('/moon-rise-set', methods=['POST'])
def moon_rise_set():
    data = request.json.get('observer') or {}
    payload = {
      "observedAt": data.get("date"),
      "latitude": data.get("latitude"),
      "longitude": data.get("longitude")
    }
    headers = get_auth_header()
    r = requests.post("https://api.astronomyapi.com/api/v2/bodies/positions", 
                      json=payload, headers=headers)
    r.raise_for_status()
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(debug=True)
