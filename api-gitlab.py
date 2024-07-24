import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration - replace with your actual GitLab access token
GITLAB_API_URL = "https://gitlab.com/api/v4"
GITLAB_ACCESS_TOKEN = "glpat-ZQsLHiCHyVMZ2J7FU1R7"

def set_role(username, group_or_repo, role):
    role_mapping = {
        "guest": 10,
        "reporter": 20,
        "developer": 30,
        "maintainer": 40,
        "owner": 50
    }

    if role not in role_mapping:
        raise ValueError("Invalid role specified")

    access_level = role_mapping[role]

    headers = {
            "PRIVATE-TOKEN": GITLAB_ACCESS_TOKEN
       
    }

    response = requests.get(f"{GITLAB_API_URL}/users", headers=headers, params={"username": username})
    response.raise_for_status()
    users = response.json()
    if not users:
        raise ValueError("User not found")
    user_id = users[0]['id']

    response = requests.get(f"{GITLAB_API_URL}/groups/{group_or_repo}", headers=headers)
    if response.status_code == 200:
        group_id = response.json()['id']
        url = f"{GITLAB_API_URL}/groups/{group_id}/members"
    else:
        response = requests.get(f"{GITLAB_API_URL}/projects/{group_or_repo}", headers=headers)
        response.raise_for_status()
        project_id = response.json()['id']
        url = f"{GITLAB_API_URL}/projects/{project_id}/members"

    data = {
        "user_id": user_id,
        "access_level": access_level
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()

def get_issues_or_mrs(entity_type, year):
    if entity_type not in ["mr", "issues"]:
        raise ValueError("Invalid entity type specified")

    entity_endpoint = "merge_requests" if entity_type == "mr" else "issues"

    headers = {
        "PRIVATE-TOKEN": GITLAB_ACCESS_TOKEN
    }

    start_date = datetime(year, 1, 1).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = datetime(year, 12, 31, 23, 59, 59).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "created_after": start_date,
        "created_before": end_date
    }

    response = requests.get(f"{GITLAB_API_URL}/{entity_endpoint}", headers=headers, params=params)
    response.raise_for_status()

    return response.json()

@app.route('/set_role', methods=['POST'])
def set_role_endpoint():
    data = request.json
    try:
        result = set_role(data['username'], data['group_or_repo'], data['role'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_issues_or_mrs', methods=['GET'])
def get_issues_or_mrs_endpoint():
    entity_type = request.args.get('entity_type')
    year = int(request.args.get('year'))
    try:
        result = get_issues_or_mrs(entity_type, year)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)