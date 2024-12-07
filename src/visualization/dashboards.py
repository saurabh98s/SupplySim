import requests
import json

SUPERSET_URL = 'http://superset:8088'
SUPERSET_USERNAME = 'admin'
SUPERSET_PASSWORD = 'admin'

class SupersetAPI:
    def __init__(self):
        self.access_token = None
        self.csrf_token = None
        self.session = requests.Session()

    def authenticate(self):
        auth_url = f"{SUPERSET_URL}/api/v1/security/login"
        login_data = {
            "username": SUPERSET_USERNAME,
            "password": SUPERSET_PASSWORD,
            "provider": "db",
            "refresh": True,
        }
        headers = {"Content-Type": "application/json"}
        response = self.session.post(auth_url, json=login_data, headers=headers)
        if response.ok:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_csrf_token()
        else:
            raise Exception("Authentication failed")

    def refresh_csrf_token(self):
        csrf_url = f"{SUPERSET_URL}/api/v1/security/csrf_token/"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        csrf_response = self.session.get(csrf_url, headers=headers)
        if csrf_response.ok:
            self.csrf_token = csrf_response.json().get("result")
        else:
            raise Exception("Failed to get CSRF token")

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-CSRFToken": self.csrf_token,
            "Content-Type": "application/json",
        }

    def get_datasource_id(self, database_name, schema_name, table_name):
        # Implement logic to get datasource ID based on database, schema, and table name
        # For simplicity, let's assume we know the datasource ID
        datasource_id = 1  # Replace with actual logic
        return datasource_id

    def create_chart(self, chart_data):
        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
        headers = self.get_headers()

        # Convert 'params' to JSON string if it's a dict
        if 'params' in chart_data and isinstance(chart_data['params'], dict):
            chart_data['params'] = json.dumps(chart_data['params'])

        response = self.session.post(chart_url, json=chart_data, headers=headers)
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Failed to create chart: {response.text}")

    def create_dashboard(self, dashboard_data):
        dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/"
        headers = self.get_headers()
        response = self.session.post(dashboard_url, json=dashboard_data, headers=headers)
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Failed to create dashboard: {response.text}")

    def add_chart_to_dashboard(self, dashboard_id, chart_id):
        # Get existing dashboard info
        dashboard_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
        headers = self.get_headers()
        response = self.session.get(dashboard_url, headers=headers)
        if not response.ok:
            raise Exception(f"Failed to get dashboard: {response.text}")

        dashboard_data = response.json()['result']
        position_json = dashboard_data.get('position_json', {})
        
        # Add the chart to the dashboard's layout
        new_chart_uuid = str(chart_id)
        position_json[new_chart_uuid] = {
            'type': 'CHART',
            'meta': {
                'chartId': chart_id
            }
        }
        dashboard_data['position_json'] = position_json

        # Update the dashboard
        update_url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
        payload = {
            'position_json': json.dumps(position_json),
            'dashboard_title': dashboard_data['dashboard_title'],
            'css': dashboard_data.get('css', '')
        }
        response = self.session.put(update_url, json=payload, headers=headers)
        if not response.ok:
            raise Exception(f"Failed to update dashboard: {response.text}")
