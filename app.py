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
OW_API_KEY     = os.getenv("OPENWEATHER_API_KEY")
TIDES_API_KEY = os.getenv("TIDES_API_KEY")
ASTRO_ID      = os.getenv("ASTRO_APP_ID")
ASTRO_SECRET  = os.getenv("ASTRO_APP_SECRET")

def get_auth_header():
    token = base64.b64encode(f"{ASTRO_ID}:{ASTRO_SECRET}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

@app.route('/weather')
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat,lon,OW_API_KEY]):
        return jsonify({"error":"Missing params or API key"}),400
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = dict(lat=lat, lon=lon, units="imperial", appid=OW_API_KEY)
    r = requests.get(url, params=params); r.raise_for_status()
    return jsonify(r.json())

@app.route('/forecast')
def forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat,lon,OW_API_KEY]):
        return jsonify({"error":"Missing params or API key"}),400
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = dict(lat=lat, lon=lon, units="imperial", appid=OW_API_KEY)
    r = requests.get(url, params=params); r.raise_for_status()
    return jsonify(r.json())

@app.route('/air-pollution')
def air_pollution():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat,lon,OW_API_KEY]):
        return jsonify({"error":"Missing params or API key"}),400
    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = dict(lat=lat, lon=lon, appid=OW_API_KEY)
    r = requests.get(url, params=params); r.raise_for_status()
    return jsonify(r.json())

@app.route('/tides')
def tides():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not all([lat,lon,TIDES_API_KEY]):
        return jsonify({"error":"Missing params or API key"}),400
    url = "https://www.worldtides.info/api/v2?extremes"
    params = dict(lat=lat, lon=lon, key=TIDES_API_KEY)
    r = requests.get(url, params=params); r.raise_for_status()
    return jsonify(r.json())

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
