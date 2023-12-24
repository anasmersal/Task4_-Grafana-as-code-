import requests
import json

# Grafana API information
grafana_url = "http://13.36.129.244:3000/api"
api_key = "glsa_ujOLMc1pKrU3G2M1zDxgZmttrMpZyEyJ_dfef7a78"

base_url = "http://13.36.129.244:3000/d/ce2fe87c-c041-43c7-8a4c-c3a33bb9c237/locations-dashboard?orgId=1&viewPanel="
datasource_uid = "df212e37-2603-4ca2-aca2-e0f9e3d299b0"


# Function to generate panel for a specific region
def generate_panel(region_number, datasource_uid):
    query = {
        "refId": "A",
        "query": '// Query 1\r\nopStatus = from(bucket: "ESP")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "ESP_data")\r\n  |> filter(fn: (r) => r["_field"] == "op_status")\r\n  |> last()\r\n  |> group(columns: ["Location"])\r\n  |> sum(column: "_value")\r\n\r\n// Query 2\r\nflowRate = from(bucket: "ESP")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "ESP_data")\r\n  |> filter(fn: (r) => r["_field"] == "flow_rate")\r\n  |> last()\r\n  |> group(columns: ["Location"])\r\n  |> sum(column: "_value")\r\n\r\n// Joining both query results\r\njoin(\r\n  tables: {opStatus: opStatus, flowRate: flowRate},\r\n  on: ["Location"]\r\n)',
    }
    panel = {
        "datasource": {
            "type": "influxdb",
            "uid": datasource_uid,
        },
        "targets": [
            {
                "datasource": {
                    "type": "influxdb",
                    "uid": datasource_uid,  # Replace with your datasource UID
                },
                "refId": "A",
                "query": '// Query 1\r\nopStatus = from(bucket: "ESP")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "ESP_data")\r\n  |> filter(fn: (r) => r["_field"] == "op_status")\r\n  |> last()\r\n  |> group(columns: ["Location"])\r\n  |> sum(column: "_value")\r\n\r\n// Query 2\r\nflowRate = from(bucket: "ESP")\r\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\r\n  |> filter(fn: (r) => r["_measurement"] == "ESP_data")\r\n  |> filter(fn: (r) => r["_field"] == "flow_rate")\r\n  |> last()\r\n  |> group(columns: ["Location"])\r\n  |> sum(column: "_value")\r\n\r\n// Joining both query results\r\njoin(\r\n  tables: {opStatus: opStatus, flowRate: flowRate},\r\n  on: ["Location"]\r\n)',
            }
        ],
        "fieldConfig": {
            "defaults": {
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [{"color": "#45628c", "value": None}],
                },
                "unit": "short",
                "color": {"mode": "thresholds"},
            },
            "overrides": [
                {
                    "matcher": {
                        "id": "byName",
                        "options": f"_value_flowRate Location_{region_number}",
                    },
                    "properties": [
                        {
                            "id": "links",
                            "value": [
                                {
                                    "targetBlank": True,
                                    "title": f"Location {region_number}",
                                    "url": "{base_url}{region_number}",
                                }
                            ],
                        }
                    ],
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": f"_value_opStatus Location_{region_number}",
                    },
                    "properties": [
                        {
                            "id": "links",
                            "value": [
                                {
                                    "targetBlank": True,
                                    "title": f"Location {region_number}",
                                    "url": "{base_url}{region_number}",
                                }
                            ],
                        }
                    ],
                },
            ],
        },
        "gridPos": {"h": 7, "w": 17, "x": 0, "y": region_number * 7},
        "id": region_number,
        "options": {
            "inlineEditing": False,
            "showAdvancedTypes": True,
            "root": {
                "background": {
                    "color": {
                        "fixed": "transparent",
                    },
                    "image": {
                        "fixed": "img/bg/location.png",  # Updated background image URL
                    },
                    "size": "fill",
                },
                "border": {
                    "color": {"fixed": "dark-green"},
                },
                "elements": [],
                "name": f"Region {region_number}",
                "type": "frame",
            },
        },
        "pluginVersion": "10.2.1",
        "title": f"Region {region_number}",
        "type": "canvas",
    }

    # Generate text elements for the panel
    for i in range((region_number - 1) * 10 + 1, region_number * 10 + 1):
        row = (i - 1) // 5  # Row position
        col = (i - 1) % 5  # Column position
        top_value = 106 if row % 2 == 0 else 273  # Alternating top values

        element = {
            "background": {
                "color": {"fixed": "transparent"},
                "image": {
                    "mode": "fixed",
                    "field": "",
                    "fixed": "img/bg/8.png",  # Updated background image URL
                },
                "size": "fill",
            },
            "border": {
                "color": {"fixed": "#ffffff"},  # Updated border color
                "width": 5,  # Updated border width
            },
            "config": {
                "align": "center",
                "color": {"fixed": "#000000"},
                "size": 16,
                "text": {"fixed": f"Location {i}"},
                "valign": "middle",
            },
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {i}",
            "placement": {
                "top": top_value,
                "height": 50,
                "left": 230 + col * 210,
                "width": 100,
            },
            "type": "text",
        }

        panel["options"]["root"]["elements"].append(element)

        element_flow_rate = {
            "background": {
                "color": {
                    "field": f"_value_flowRate Location_{i}",
                    "fixed": "#D9D9D9",
                }
            },
            "border": {
                "color": {"fixed": "#ffffff"},  # Updated border color
                "width": 5,  # Updated border width
            },
            "config": {
                "align": "center",
                "color": {"fixed": "#000000"},
                "size": 20,
                "text": {
                    "field": f"_value_flowRate Location_{i}",
                    "fixed": "",
                    "mode": "field",
                },
                "valign": "middle",
            },
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {i}_1",  # Naming the element
            "placement": {
                "height": 50,  # Updated height
                "left": 208 + col * 210,  # Adjust placement as needed
                "top": top_value + 47,  # Adjust placement as needed
                "width": 72,  # Updated width
            },
            "type": "metric-value",
        }

        panel["options"]["root"]["elements"].append(element_flow_rate)

        element_op_status = {
            "background": {
                "color": {
                    "field": f"_value_opStatus Location_{i}",
                    "fixed": "#D9D9D9",
                }
            },
            "border": {
                "color": {"fixed": "#ffffff"},  # Updated border color
                "width": 5,  # Updated border width
            },
            "config": {
                "align": "center",
                "color": {"fixed": "#000000"},
                "size": 20,
                "text": {
                    "field": f"_value_opStatus Location_{i}",
                    "fixed": "",
                    "mode": "field",
                },
                "valign": "middle",
            },
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {i}_2",  # Naming the element
            "placement": {
                "height": 50,  # Updated height
                "left": 280 + col * 210,  # Adjust placement as needed
                "top": top_value + 47,  # Adjust placement as needed
                "width": 70,  # Updated width
            },
            "type": "metric-value",
        }
        panel["options"]["root"]["elements"].append(element_op_status)

        # Add _value_flowRate and _value_opStatus overrides
        override_flow_rate = {
            "matcher": {
                "id": "byName",
                "options": f"_value_flowRate Location_{i}",
            },
            "properties": [
                {
                    "id": "links",
                    "value": [
                        {
                            "targetBlank": True,
                            "title": f"Location {i}",
                            "url": f"{base_url}{i+1}",
                        }
                    ],
                }
            ],
        }
        panel["fieldConfig"]["overrides"].append(override_flow_rate)

        override_op_status = {
            "matcher": {
                "id": "byName",
                "options": f"_value_opStatus Location_{i}",
            },
            "properties": [
                {
                    "id": "links",
                    "value": [
                        {
                            "targetBlank": True,
                            "title": f"Location {i}",
                            "url": f"{base_url}{i+1}",
                        }
                    ],
                },
                {
                    "id": "color",
                    "value": {"fixedColor": "light-green", "mode": "fixed"},
                },
            ],
        }
        panel["fieldConfig"]["overrides"].append(override_op_status)
        # Adding new elements to the panel
    new_elements = [
        {
            "background": {"color": {"fixed": "transparent"}},
            "border": {"color": {"fixed": "dark-green"}},
            "config": {
                "align": "center",
                "backgroundColor": {"fixed": "#45628c"},
                "borderColor": {
                    "field": f"_value_flowRate Location_{region_number}",
                    "fixed": "transparent",
                },
                "color": {"fixed": "semi-dark-orange"},
                "text": {"mode": "field"},
                "valign": "middle",
                "width": -1,
            },
            "connections": [],
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {region_number * 10 + 1}",  # Adjust naming as needed
            "placement": {"height": 20, "left": 5, "top": 19, "width": 20},
            "type": "ellipse",
        },
        # Element 32
        {
            "background": {
                "color": {"fixed": "transparent"},
                "image": {
                    "mode": "fixed",
                    "field": "",
                    "fixed": "img/bg/8.png",  # Updated background image URL
                },
                "size": "fill",
            },
            "border": {
                "color": {"fixed": "#ffffff"},  # Updated border color
                "width": 5,  # Updated border width
            },
            "config": {
                "align": "center",
                "color": {"fixed": "#000000"},
                "size": 18,
                "text": {"fixed": "Total Flow Rate  (L/s)"},
                "valign": "middle",
            },
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {region_number * 10 + 2}",  # Adjust naming as needed
            "placement": {"height": 45, "left": 35, "top": 7, "width": 188},
            "type": "text",
        },
        # Element 33
        {
            "background": {"color": {"fixed": "transparent"}},
            "border": {"color": {"fixed": "dark-green"}},
            "config": {
                "align": "center",
                "backgroundColor": {"fixed": "#96d98d"},
                "borderColor": {
                    "field": f"_value_flowRate Location_{region_number}",
                    "fixed": "transparent",
                },
                "color": {"fixed": "semi-dark-orange"},
                "text": {"mode": "field"},
                "valign": "middle",
                "width": -1,
            },
            "connections": [],
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {region_number * 10 + 3}",  # Adjust naming as needed
            "placement": {"height": 20, "left": 5, "top": 62, "width": 20},
            "type": "ellipse",
        },
        # Element 34
        {
            "background": {
                "color": {"fixed": "transparent"},
                "image": {
                    "mode": "fixed",
                    "field": "",
                    "fixed": "img/bg/8.png",  # Updated background image URL
                },
                "size": "fill",
            },
            "border": {
                "color": {"fixed": "#ffffff"},  # Updated border color
                "width": 5,  # Updated border width
            },
            "config": {
                "align": "center",
                "color": {"fixed": "#000000"},
                "size": 18,
                "text": {"fixed": "Active Oil Wells (out of 4)"},
                "valign": "middle",
            },
            "constraint": {"horizontal": "left", "vertical": "top"},
            "name": f"Element {region_number * 10 + 4}",  # Adjust naming as needed
            "placement": {"height": 45, "left": 35, "top": 50, "width": 229},
            "type": "text",
        },
    ]

    # Extend the elements list in the panel with the new elements
    panel["options"]["root"]["elements"].extend(new_elements)

    return panel


# Create dashboard with multiple panels for regions 1 to 10
dashboard_title = "Regions Dashboard"
dashboard_definition = {
    "dashboard": {
        "id": None,
        "title": dashboard_title,
        "panels": [],
        "schemaVersion": 22,
        "version": 0,
        "time": {"from": "now-2d", "to": "now"},
    },
    "folderId": 0,
    "overwrite": False,
}

# Generate panels for ten regions and add them to the dashboard definition
for region_number in range(1, 11):
    panel = generate_panel(region_number, datasource_uid)
    dashboard_definition["dashboard"]["panels"].append(panel)

# Send the dashboard definition to Grafana API to create the dashboard
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
response = requests.post(
    f"{grafana_url}/dashboards/db", headers=headers, json=dashboard_definition
)

if response.status_code == 200:
    print("Dashboard created successfully!")
else:
    print("Failed to create the dashboard.")
    print(response.text)
