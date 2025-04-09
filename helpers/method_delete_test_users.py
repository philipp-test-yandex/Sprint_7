import requests
from helpers.constants import COURIER_URL
from helpers.constants import LOGIN_URL
def delete_courier(courier_id):
    del_url = COURIER_URL + '/' + str(courier_id)
    print(del_url)
    return requests.delete(del_url)


def get_courier_id(login, password):
    payload = {"login": login, "password": password}
    response = requests.post(LOGIN_URL, json=payload)
    return response.json().get("id")
