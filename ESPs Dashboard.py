import requests
import json

# Grafana API information
grafana_url = "http://13.36.129.244:3000/api"
api_key = "glsa_ujOLMc1pKrU3G2M1zDxgZmttrMpZyEyJ_dfef7a78"

# Dashboard configuration
dashboard_title = "ESPs Dashboard"
dashboard_definition = {
    "dashboard": {
        "id": None,
        "title": dashboard_title,
        "panels": [],
        "schemaVersion": 22,
        "version": 0,
    },
    "folderId": 0,
    "overwrite": False,
}

sensor_ids = [f"{i}" for i in range(1, 401)]

# Loop through sensor IDs, arranging two panels in the same row
for idx, sensor_id in enumerate(sensor_ids):
    # Calculate row and column positions for each panel
    row = idx // 2  # Two panels per row
    col = idx % 2 * 12  # Each panel spans 12 units

    # InfluxDB query for each sensor
    query = f"""from(bucket: "ESP")
            |> range(start: -30d, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "ESP_data")
            |> filter(fn: (r) => r["_field"] == "vibration" or r["_field"] == "pump_pressure" or r["_field"] == "power" or r["_field"] == "motor_temp" or r["_field"] == "flow_rate")
            |> filter(fn: (r) => r["ESP_ID"] == "{sensor_id}")
            |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
            |> yield(name: "mean")"""

    panel = {
        "title": f"ESP_{sensor_id}",
        "type": "timeseries",
        "datasource": "InfluxDB",
        "id": idx + 1,
        "gridPos": {
            "x": col,
            "y": row * 8,
            "w": 12,
            "h": 8,
        },
        "options": {
            # Your existing options
        },
        "fieldConfig": {
            # Your existing field configurations
        },
        "targets": [
            {
                "query": query,
                "format": "time_series",
                "interval": "",
                "legendFormat": "{{ metric }}",
                "refId": "A",
            }
        ],
    }
    dashboard_definition["dashboard"]["panels"].append(panel)

# Create dashboard using Grafana API
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

response = requests.post(
    f"{grafana_url}/dashboards/db",
    headers=headers,
    data=json.dumps(dashboard_definition),
)

if response.status_code == 200:
    print("Dashboard created successfully.")
else:
    print(
        f"Error creating dashboard. Status code: {response.status_code}, Error: {response.text}"
    )
