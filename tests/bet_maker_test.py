import random
import time
from enum import Enum

import requests

BASE_URL = 'http://0.0.0.0:8000'
LINE_PROVIDER_URL = 'http://0.0.0.0:8001'

test_event = {
    "name": f"test_event {random.randint(1, 1000000)}",
    "coefficient": random.randint(1, 10),
    "deadline": "2023-05-01T12:00:00"
}


class State(str, Enum):
    active = "active"
    close_win = "close_win"
    close_lose = "close_lose"


def test_app_200():
    response = requests.get(BASE_URL + '/docs')
    assert response.status_code == 200


def test_get_method():
    response = requests.get(BASE_URL + '/bets')
    assert response.status_code == 200


def test_post_method():
    response = requests.post(LINE_PROVIDER_URL + '/events', json=test_event)
    test_event['id'] = response.json()['id']
    response = requests.post(BASE_URL + '/bets', json={'event_uuid': str(test_event['id']), 'amount': 123.45})
    assert response.status_code == 201


def test_event_listener():
    response = requests.post(LINE_PROVIDER_URL + '/events', json=test_event)
    assert response.status_code == 201

    event_id = response.json()['id']
    response = requests.post(BASE_URL + '/bets', json={'event_uuid': str(event_id), 'amount': 345.67})
    bet_id = response.json()['id']
    assert response.status_code == 201

    response = requests.patch(LINE_PROVIDER_URL + f'/events/{event_id}', json={'state': State.close_win})
    assert response.status_code == 200

    time.sleep(1)  # wait for event listener

    response = requests.get(BASE_URL + f'/bets/{bet_id}')
    assert response.status_code == 200
    assert response.json()['state'] == State.close_win
