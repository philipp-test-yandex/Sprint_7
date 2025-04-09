import requests
import pytest
import allure
from conftest import courier_data, registered_courier_and_after_delete_courier
from helpers.constants import COURIER_URL, LOGIN_URL, ORDER_URL, ERROR_LOGIN_ALREADY_EXISTS, ERROR_NOT_ENOUGH_DATA, ERROR_ACCOUNT_NOT_FOUND, OK_RESPONSE

class TestCreateCourier:
    @allure.title("Создание курьера при заполненных всех полях")
    def test_create_new_courier_all_fields_are_filled(self, courier_data):
        with allure.step("Отправка запроса на создание курьера"):
            response = requests.post(COURIER_URL, json=courier_data)

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            assert response.json() == OK_RESPONSE


    @allure.title("Попытка повторного создания одинакового курьера")
    def test_create_two_same_courier(self, registered_courier_and_after_delete_courier):
        with allure.step("Попытка повторной регистрации с теми же данными"):
            payload = {
                "login": registered_courier_and_after_delete_courier["login"],
                "password": registered_courier_and_after_delete_courier["password"],
                "firstName": registered_courier_and_after_delete_courier["firstName"]
            }
            response = requests.post(COURIER_URL, json=payload)

        with allure.step("Проверка ошибки"):
            assert response.status_code == 409
            assert response.json()["message"] == ERROR_LOGIN_ALREADY_EXISTS



    @allure.title("Создание курьера без поля firstName")
    def test_create_new_courier_first_name_is_empty(self, courier_data):
        with allure.step("Генерация данных без firstName"):
            courier_data.pop("firstName")

        with allure.step("Отправка запроса"):
            response = requests.post(COURIER_URL, json=courier_data)

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            assert response.json() == OK_RESPONSE


    @allure.title("Создание курьера с уже существующим логином")
    def test_create_new_courier_which_login_have_in_system(self, registered_courier_and_after_delete_courier):
        with allure.step("Попытка регистрации с тем же логином и другими данными"):
            duplicate_payload = {
                "login": registered_courier_and_after_delete_courier["login"],
                "password": registered_courier_and_after_delete_courier["password"] + "invalid",
                "firstName": registered_courier_and_after_delete_courier["firstName"] + "invalid"
            }

            response = requests.post(COURIER_URL, json=duplicate_payload)

        with allure.step("Проверка ошибки"):
            assert response.status_code == 409
            assert response.json()["message"] == ERROR_LOGIN_ALREADY_EXISTS

class TestLoginCourier:
    @allure.title("Авторизация курьера с получением ID")
    def test_courier_can_login_and_get_id(self, registered_courier_and_after_delete_courier):
        with allure.step("Отправка запроса на авторизацию"):
            payload = {
                "login": registered_courier_and_after_delete_courier["login"],
                "password": registered_courier_and_after_delete_courier["password"]
            }
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка авторизации"):
            assert response.status_code == 200
            assert "id" in response.json()


    @allure.title("Ошибка авторизации без логина")
    def test_login_fails_without_login_field(self):
        with allure.step("Формирование данных без логина"):
            payload = {"password": "password"}

        with allure.step("Отправка запроса"):
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка ошибки"):
            assert response.status_code == 400
            assert response.json()["message"] == ERROR_NOT_ENOUGH_DATA

    @allure.title("Ошибка авторизации без пароля")
    def test_login_fails_without_password_field(self, registered_courier_and_after_delete_courier):
        with allure.step("Формирование данных без пароля"):
            login = registered_courier_and_after_delete_courier["login"]
            payload = {"login": login}

        with allure.step("Отправка запроса"):
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка ошибки"):
            assert response.status_code == 400
            assert response.json()["message"] == ERROR_NOT_ENOUGH_DATA


    @allure.title("Ошибка авторизации с неверным логином")
    def test_login_fails_with_invalid_login(self, registered_courier_and_after_delete_courier):
        with allure.step("Формирование данных с неверным логином"):
            login = registered_courier_and_after_delete_courier["login"]
            password = registered_courier_and_after_delete_courier["password"]

            payload = {
                "login": login + '_invalid',
                "password": password
            }

        with allure.step("Отправка запроса на авторизацию пользователя"):
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка ошибки"):
            assert response.json()["message"] == ERROR_ACCOUNT_NOT_FOUND
            assert response.status_code == 404

    @allure.title("Ошибка авторизации с неверным паролем")
    def test_login_fails_with_invalid_password(self, registered_courier_and_after_delete_courier):
        with allure.step("Формирование данных с неверным паролем"):
            login = registered_courier_and_after_delete_courier["login"]
            password = registered_courier_and_after_delete_courier["password"]

            payload = {
                "login": login,
                "password": password + '_invalid'
            }

        with allure.step("Отправка запроса"):
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка ошибки"):
            assert response.status_code == 404
            assert response.json()["message"] == ERROR_ACCOUNT_NOT_FOUND

    @allure.title("Ошибка авторизации несуществующего пользователя")
    def test_login_fails_with_nonexistent_user(self, courier_data):
        with allure.step("Генерация данных для несуществующего пользователя"):
            login = courier_data["login"]
            password = courier_data["password"]

            payload = {
                "login": login,
                "password": password
            }

        with allure.step("Отправка запроса"):
            response = requests.post(LOGIN_URL, json=payload)

        with allure.step("Проверка ошибки"):

            assert response.status_code == 404
            assert response.json()["message"] == ERROR_ACCOUNT_NOT_FOUND


class TestCreateOrder:
    @allure.title("Создание заказа с цветом: {color}")
    @pytest.mark.parametrize("color", [["BLACK"], ["GREY"], ["BLACK", "GREY"], []])
    def test_create_order_with_various_colors(self, color):
        with allure.step("Формирование тела запроса на заказ"):
            payload = {
                "firstName": "Иван",
                "lastName": "Иванов",
                "address": "Москва, ул. Тестовая, д.1",
                "metroStation": 4,
                "phone": "+7 800 555 35 35",
                "rentTime": 5,
                "deliveryDate": "2023-12-31",
                "comment": "Тестовый заказ",
                "color": color
            }

        with allure.step("Отправка запроса на создание заказа"):
            response = requests.post(ORDER_URL, json=payload)

        with allure.step("Проверка успешного ответа и наличия track"):
            assert response.status_code == 201
            assert "track" in response.json()

class TestListOfOrder:
    @allure.title("Получение списка заказов")
    def test_order_list_is_returned(self):
        with allure.step("Отправка запроса на /orders"):
            response = requests.get(ORDER_URL)

        with allure.step("Проверка ответа и наличия orders в списке"):
            assert response.status_code == 200
            assert "orders" in response.json()
