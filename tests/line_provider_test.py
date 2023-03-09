from enum import Enum
import random

import requests

BASE_URL = 'http://0.0.0.0:8001'
test_event = {
    "name": f"test_event {random.randint(1, 1000000)}",
    "coefficient": random.randint(1, 10),
    "deadline": "2023-05-01T12:00:00"
}


class EventState(str, Enum):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


def test_app_200():
    response = requests.get(BASE_URL + '/docs')
    assert response.status_code == 200


def test_get_method():
    response = requests.get(BASE_URL + '/events')
    assert response.status_code == 200


def test_post_method():
    response = requests.post(BASE_URL + '/events', json=test_event)
    assert response.status_code == 201
    test_event['id'] = response.json()['id']


def test_patch_method():
    response = requests.patch(BASE_URL + f'/events/{test_event["id"]}', json={'state': EventState.close_win})
    assert response.status_code == 200
