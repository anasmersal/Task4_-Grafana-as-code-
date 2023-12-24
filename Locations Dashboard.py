import requests
import json

# Grafana API information
grafana_url = "http://13.36.129.244:3000/api"
api_key = "glsa_ujOLMc1pKrU3G2M1zDxgZmttrMpZyEyJ_dfef7a78"

base_url = "http://13.36.129.244:3000/d/fecf7328-2ec2-48e5-97d8-69af5fc0c645/esps-dashboard?orgId=1&viewPanel="
datasource_uid = "df212e37-2603-4ca2-aca2-e0f9e3d299b0"


# Function to calculate the region based on location
def calculate_region(location):
    return (location - 1) // 10 + 1


# Function to calculate the location based on ESP ID
def calculate_location(esp_id):
    return (esp_id - 1) // 4 + 1


# Function to create gauge panel JSON with overrides
def create_gauge_panel(panel_title, esp_ids, grid_x, grid_y, datasource_uid):
    panel = {
        "type": "gauge",
        "title": panel_title,
        "gridPos": {"x": grid_x, "y": grid_y, "w": 30, "h": 10},
        "datasource": {
            "uid": datasource_uid,  # Replace with your datasource UID
            "type": "influxdb",
        },
        "id": 2,
        "targets": [
            {
                "datasource": {
                    "type": "influxdb",
                    "uid": datasource_uid,  # Replace with your datasource UID
                },
                "refId": "A",
                "query": f'from(bucket: "ESP")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "ESP_data")\r\n  |> filter(fn: (r) => r["ESP_ID"] == "{esp_ids[0]}" or r["ESP_ID"] == "{esp_ids[1]}" or r["ESP_ID"] == "{esp_ids[2]}" or r["ESP_ID"] == "{esp_ids[3]}")\r\n  |> filter(fn: (r) => r["_field"] == "vibration" or r["_field"] == "pump_pressure" or r["_field"] == "power" or r["_field"] == "motor_temp" or r["_field"] == "flow_rate")\r\n  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)\r\n  |> yield(name: "mean")',
            }
        ],
        "fieldConfig": {
            "defaults": {
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "red", "value": 2000},
                    ],
                },
                "color": {"mode": "thresholds"},
            },
            "overrides": [],  # Initialize an empty list for overrides
        },
        "options": {
            "reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""},
            "orientation": "auto",
            "showThresholdLabels": False,
            "showThresholdMarkers": True,
            "minVizWidth": 75,
            "minVizHeight": 75,
        },
        "pluginVersion": "10.2.2",
    }
    # List of fields to override
    fields_to_override = [
        "vibration",
        "pump_pressure",
        "power",
        "motor_temp",
        "flow_rate",
        # Add other fields you want to override here
    ]
    # List of fields and their corresponding colors
    field_colors = {
        "vibration": "red",
        "pump_pressure": "orange",
        "power": "dark-blue",
        "motor_temp": "semi-dark-yellow",
        "flow_rate": None,
        # Add other fields with their respective colors
    }

    for esp_id in esp_ids:
        location = calculate_location(esp_id)
        region = calculate_region(location)

        for field_name, color in field_colors.items():
            override = {
                "matcher": {
                    "id": "byName",
                    "options": f'{field_name} {{ESP_ID="{esp_id}", Location="Location_{location}", Region="Region_{region}", topic="ESP_data/Region_{region}/Location_{location}/{esp_id}/{field_name}"}}',
                },
                "properties": [
                    {
                        "id": "links",
                        "value": [
                            {
                                "title": f"ESP {esp_id}",
                                "url": f"{base_url}{esp_id}",
                                "targetBlank": True,
                            }
                        ],
                    },
                ],
            }

            if color:
                override["properties"].append(
                    {
                        "id": "color",
                        "value": {
                            "mode": "fixed",
                            "fixedColor": color,
                        },
                    }
                )

            panel["fieldConfig"]["overrides"].append(override)

    return panel


# Create dashboard with 100 panels
dashboard_title = "Locations Dashboard"
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
# Create panels for 100 locations with the desired layout
grid_x_positions = [0, 12, 0, 12] * 25  # Alternating X positions for gauges
grid_y_positions = [0, 0, 6, 6] * 25  # Alternating Y positions for gauges

# Create panels for 100 locations
for i in range(1, 101):
    esp_ids = [
        i * 4 - 3,
        i * 4 - 2,
        i * 4 - 1,
        i * 4,
    ]  # Generate ESP IDs for each panel

    # Use the alternating grid positions for each gauge in a panel
    panel = create_gauge_panel(
        f"Location {i}",
        esp_ids,
        grid_x_positions[i - 1],
        grid_y_positions[i - 1],
        datasource_uid,
    )
    dashboard_definition["dashboard"]["panels"].append(panel)

# Make API request to create the dashboard
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

create_dashboard_url = f"{grafana_url}/dashboards/db"
response = requests.post(
    create_dashboard_url, headers=headers, json=dashboard_definition
)

if response.status_code == 200:
    print("Dashboard created successfully!")
else:
    print(
        f"Failed to create dashboard. Status code: {response.status_code}, Error: {response.text}"
    )
