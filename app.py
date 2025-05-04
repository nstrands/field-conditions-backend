from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

ASTRO_APP_ID = os.getenv('ASTRO_APP_ID')
ASTRO_APP_SECRET = os.getenv('ASTRO_APP_SECRET')

@app.route('/moon-phase', methods=['POST'])
def moon_phase():
    data = request.json
    resp = requests.post(
        'https://api.astronomyapi.com/api/v2/studio/moon-phase',
        json=data,
        auth=(ASTRO_APP_ID, ASTRO_APP_SECRET)
    )
    return jsonify(resp.json())

@app.route('/moon-rise-set', methods=['POST'])
def moon_rise_set():
    data = request.json
    resp = requests.post(
        'https://api.astronomyapi.com/api/v2/studio/moon-rise-set',
        json=data,
        auth=(ASTRO_APP_ID, ASTRO_APP_SECRET)
    )
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(debug=True)
