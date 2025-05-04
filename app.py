from flask import Flask, request, jsonify
import requests
import base64
import os
from dotenv import load_dotenv

# Load credentials from .env file if present
load_dotenv()

app = Flask(__name__)

# Get credentials from environment variables
APP_ID = os.getenv("ASTRO_APP_ID")
APP_SECRET = os.getenv("ASTRO_APP_SECRET")

def get_auth_header():
    """Return the properly formatted Basic Auth header."""
    userpass = f"{APP_ID}:{APP_SECRET}"
    auth_encoded = base64.b64encode(userpass.encode()).decode()
    return {"Authorization": f"Basic {auth_encoded}"}

@app.route('/positions', methods=['GET'])
def get_positions():
    # Required query parameters from the client
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    elevation = request.args.get("elevation", "0")  # default to sea level
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    time = request.args.get("time", "00:00:00")  # default to midnight

    if not all([latitude, longitude, from_date, to_date]):
        return jsonify({"error": "Missing required query parameters."}), 400

    # Assemble request to AstronomyAPI
    url = "https://api.astronomyapi.com/api/v2/bodies/positions"
    headers = get_auth_header()
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": elevation,
        "from_date": from_date,
        "to_date": to_date,
        "time": time
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
