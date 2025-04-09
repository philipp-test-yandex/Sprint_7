import pytest
from helpers.method_generate_new_unic_courier import generate_login_password_firstname,register_new_courier_and_return_login_password
from helpers.method_delete_test_users import get_courier_id, delete_courier


@pytest.fixture
def courier_data():
    data = generate_login_password_firstname()
    yield data
    courier_id = get_courier_id(data["login"], data["password"])
    if courier_id:
        response = delete_courier(courier_id)
        print(f"\nУдаление курьера: /api/v1/courier/{courier_id}")
        print(f"Статус код удаления: {response.status_code}")
    else:
        print(f"\n Курьер с логином '{data['login']}' не найден — id не получен.")

@pytest.fixture
def registered_courier_and_after_delete_courier():
    login, password, first_name = register_new_courier_and_return_login_password()
    courier =  {
        "login": login,
        "password": password,
        "firstName": first_name
    }

    yield courier

    courier_id = get_courier_id(login, password)
    if courier_id:
        response = delete_courier(courier_id)
        print(f"\nУдаление курьера: /api/v1/courier/{courier_id}")
        print(f"Статус код удаления: {response.status_code}")
    else:
        print(f"\n Курьер с логином '{login}' не найден — id не получен.")

