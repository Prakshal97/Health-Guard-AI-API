def get_pollution_data():
    pollution = {
        "pm25": 92,
        "pm10": 160,
        "no2": 42,
        "location": "Mumbai",
    }

    return pollution
def get_daily_pollution_readings():
    daily_data = []

    for hour in range(24):
        reading = {
            "hour": hour,
            "pm25": 80 + hour,   # fake generated data
            "pm10": 150 + (hour // 2)
        }
        daily_data.append(reading)

    return daily_data
