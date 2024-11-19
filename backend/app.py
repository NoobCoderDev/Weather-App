from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
from config import API_KEY
import logging

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

def get_weather_data(location, days=3):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={location}&days={days}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_historical_data(location, start_date, end_date):
    url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={location}&dt={start_date}&end_dt={end_date}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_current_location_data(lat, lon):
    url= f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

@app.route('/')
@app.route('/current_weather')
def current_dashboard():
    return render_template('current_dashboard.html')

@app.route('/forcast_weather')
def forecast_dashboard():
    return render_template('forecast_dashboard.html')

@app.route('/historical_weather')
def historical_dashboard():
    return render_template('historical_dashboard.html')

@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    location = data.get('location', 'London')
    data_type = data.get('dataType', 'current')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    days = data.get('days')

    if data_type == 'current':
        weather_data = get_weather_data(location, days=days)
        if weather_data:
            return jsonify({
                'current': weather_data['current'],
                'location': weather_data['location']
            })
    elif data_type == 'forecast':
        weather_data = get_weather_data(location, days=days)
        if weather_data:
            return jsonify({
                'forecast': weather_data['forecast']['forecastday'],
                'location': weather_data['location']
            })
    elif data_type == 'historical':
        weather_data = get_historical_data(location, start_date, end_date)
        if weather_data:
            return jsonify({
                'historical': weather_data['forecast']['forecastday'],
                'location': weather_data['location']
            })

    return jsonify({'error': 'Unable to fetch weather data'}), 400

@app.route('/get_weather', methods=['GET'])
def get_weather_for_current_location():
    # Extract latitude and longitude from query parameters
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    try:
        weather_data = get_current_location_data(lat, lon)
        if weather_data is None:
            return jsonify({"error": "Failed to fetch weather data"}), 500
        return jsonify(weather_data)
    except Exception as e:
        logging.exception("An error occurred while processing the request")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)