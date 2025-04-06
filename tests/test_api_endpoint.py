import requests
import pytest
import allure
from helpers.method_generate_new_unic_courier import register_new_courier_and_return_login_password, generate_login_password_firstname

class TestCreateCourier:
    @allure.title("Создание курьера при заполненных всех полях")
    def test_create_new_courier_all_fields_are_filled(self):
        with allure.step("Генерация данных для курьера (логин, пароль, имя)"):
            courier_data = generate_login_password_firstname()

        with allure.step("Отправка запроса на создание курьера"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier', json=courier_data)

            print("\nОтправляемые данные курьера:", courier_data)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            assert response.json() == {"ok": True}

    @allure.title("Попытка повторного создания одинакового курьера")
    def test_create_two_same_courier(self):
        with allure.step("Создание первого курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, password, first_name = courier_data

        with allure.step("Попытка повторной регистрации с теми же данными"):
            payload = {
                "login": login,
                "password": password,
                "firstName": first_name
            }

            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier', json=payload)
            print("\nПопытка создания повторного курьера с данными:", payload)
            print("Ответ от сервера на повторное создание:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 409
            assert response.json()["message"] == "Этот логин уже используется. Попробуйте другой."

    @allure.title("Создание курьера без поля firstName")
    def test_create_new_courier_first_name_is_empty(self):
        with allure.step("Генерация данных без firstName"):
            courier_data = generate_login_password_firstname()
            courier_data.pop("firstName")

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier', json=courier_data)
            print("\nОтправляемые данные без first_name:", courier_data)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            assert response.json() == {"ok": True}

    @allure.title("Создание курьера с уже существующим логином")
    def test_create_new_courier_which_login_have_in_system(self):
        with allure.step("Регистрация первого курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, password, first_name = courier_data

        with allure.step("Попытка регистрации с тем же логином и другими данными"):
            duplicate_payload = {
                "login": login,
                "password": password + "invalid",
                "firstName": first_name + "invalid"
            }

            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier', json=duplicate_payload)
            print("Отправляемые данные:", duplicate_payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 409
            assert response.json()["message"] == "Этот логин уже используется. Попробуйте другой."

class TestLoginCourier:
    @allure.title("Авторизация курьера с получением ID")
    def test_courier_can_login_and_get_id(self):
        with allure.step("Регистрация нового курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, password, _ = courier_data

        with allure.step("Отправка запроса на авторизацию"):
            payload = {
                "login": login,
                "password": password
            }
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Отправляемые данные:", payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка авторизации"):
            assert response.status_code == 200
            assert "id" in response.json()

    @allure.title("Ошибка авторизации без логина")
    def test_login_fails_without_login_field(self):
        with allure.step("Формирование данных без логина"):
            payload = {"password": "password"}

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Отправляемые данные:", payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для входа"

    @allure.title("Ошибка авторизации без пароля")
    def test_login_fails_without_password_field(self):
        with allure.step("Регистрация курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, _, _ = courier_data

        with allure.step("Формирование данных без пароля"):
            payload = {"login": login}

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Отправляемые данные:", payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 400
            assert response.json()["message"] == "Недостаточно данных для входа"

    @allure.title("Ошибка авторизации с неверным логином")
    def test_login_fails_with_invalid_login(self):
        with allure.step("Регистрация курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, password, _ = courier_data

        with allure.step("Формирование данных с неверным логином"):
            payload = {
                "login": login + '_invalid',
                "password": password
            }

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Ответ от сервера:", response.status_code, response.json())
            print("Отправляемые данные:", payload)

        with allure.step("Проверка ошибки"):
            assert response.json()["message"] == "Учетная запись не найдена"
            assert response.status_code == 404

    @allure.title("Ошибка авторизации с неверным паролем")
    def test_login_fails_with_invalid_password(self):
        with allure.step("Регистрация курьера"):
            courier_data = register_new_courier_and_return_login_password()
            login, password, _ = courier_data

        with allure.step("Формирование данных с неверным паролем"):
            payload = {
                "login": login,
                "password": password + '_invalid'
            }

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Отправляемые данные:", payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"

    @allure.title("Ошибка авторизации несуществующего пользователя")
    def test_login_fails_with_nonexistent_user(self):
        with allure.step("Генерация данных для несуществующего пользователя"):
            courier_data = generate_login_password_firstname()
            login = courier_data["login"]
            password = courier_data["password"]

            payload = {
                "login": login,
                "password": password
            }

        with allure.step("Отправка запроса"):
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/courier/login', json=payload)
            print("Отправляемые данные:", payload)
            print("Ответ от сервера:", response.status_code, response.json())

        with allure.step("Проверка ошибки"):
            assert response.status_code == 404
            assert response.json()["message"] == "Учетная запись не найдена"


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
            response = requests.post('https://qa-scooter.praktikum-services.ru/api/v1/orders', json=payload)
            print(f"\nСоздание заказа с цветом: {color}")
            print("Статус:", response.status_code)
            print("Ответ:", response.json())

        with allure.step("Проверка успешного ответа и наличия track"):
            assert response.status_code == 201
            assert "track" in response.json()

class TestListOfOrder:
    @allure.title("Получение списка заказов")
    def test_order_list_is_returned(self):
        with allure.step("Отправка запроса на /orders"):
            response = requests.get('https://qa-scooter.praktikum-services.ru/api/v1/orders')

        with allure.step("Проверка ответа и наличия orders в списке"):
            assert response.status_code == 200
            assert "orders" in response.json()