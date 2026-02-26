import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    requested_path = "/"

    response = client.get(requested_path, follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_dictionary(client):
    requested_path = "/activities"

    response = client.get(requested_path)
    payload = response.json()

    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_new_participant(client):
    activity_name = "Chess Club"
    encoded_activity_name = quote(activity_name, safe="")
    participant_email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": participant_email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {participant_email} for {activity_name}"
    assert participant_email in activities[activity_name]["participants"]


def test_unregister_removes_existing_participant(client):
    activity_name = "Programming Class"
    encoded_activity_name = quote(activity_name, safe="")
    participant_email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{encoded_activity_name}/signup",
        params={"email": participant_email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]
