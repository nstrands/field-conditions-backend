from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os
import base64
from requests.auth import HTTPBasicAuth


app = Flask(__name__)
CORS(app)

ASTRO_APP_ID = os.getenv('ASTRO_APP_ID')
ASTRO_APP_SECRET = os.getenv('ASTRO_APP_SECRET')

@app.route('/moon-phase', methods=['POST'])
def moon_phase():
    data = request.json
    observer = data['observer']

    url = "https://api.astronomyapi.com/api/v2/bodies/phase/moon"
    params = {
        "latitude": observer["latitude"],
        "longitude": observer["longitude"],
        "from_date": observer["date"],
        "to_date": observer["date"]
    }

    auth = HTTPBasicAuth(ASTRO_APP_ID, ASTRO_APP_SECRET)
    response = requests.get(url, params=params, auth=auth)
    return jsonify(response.json())




@app.route('/moon-rise-set', methods=['POST'])
def moon_rise_set():
    data = request.json
    observer = data['observer']

    url = "https://api.astronomyapi.com/api/v2/rise-set/moon"
    params = {
        "latitude": observer["latitude"],
        "longitude": observer["longitude"],
        "date": observer["date"]
    }

    auth = HTTPBasicAuth(ASTRO_APP_ID, ASTRO_APP_SECRET)
    response = requests.get(url, params=params, auth=auth)
    return jsonify(response.json())






if __name__ == '__main__':
    app.run(debug=True)
