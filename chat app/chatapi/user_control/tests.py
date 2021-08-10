from rest_framework.test import APITestCase
from .views import get_random, get_access_token, get_refresh_token


class TestGenericFunction(APITestCase):

    def test_get_random(self):

        rand1 = get_random(10)
        rand2 = get_random(10)
        rand3 = get_random(15)

        # проверяем что мы получаем результат
        self.assertTrue(rand1)

        # проверяем что rand1 не равен на rand2
        self.assertNotEqual(rand1, rand2)

        # проверяем что длина результата ожидаемый
        self.assertEqual(len(rand1), 10)
        self.assertEqual(len(rand3), 15)

    def test_get_access_token(self):

        payload = {
            'id': 1
        }

        token = get_access_token(payload)

        # проверяем что получаем результат
        self.assertTrue(token)

    def test_get_refresh_token(self):
        token = get_refresh_token()

        # проверяем что получаем результат
        self.assertTrue(token)


class TestAuth(APITestCase):
    login_url = "/user/login"
    register_url = "/user/register"
    refresh_url = "/user/refresh"

    def test_register(self):
        payload = {
            "username": "adefemigreat",
            "password": "ade123",
        }

        response = self.client.post(self.register_url, data=payload)

        # проверяем что получаем статус 201
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        payload = {
            "username": "adefemigreat",
            "password": "ade123",
        }

        # register
        self.client.post(self.register_url, data=payload)

        # login
        response = self.client.post(self.login_url, data=payload)
        result = response.json()

        # проверяем что получаем статус 200
        self.assertEqual(response.status_code, 200)

        # проверяем что получаем оба обновление и доступ токен
        self.assertTrue(result["access"])
        self.assertTrue(result["refresh"])

    def test_refresh(self):
        payload = {
            "username": "adefemigreat",
            "password": "ade123",
        }

        # register
        self.client.post(self.register_url, data=payload)

        # login
        response = self.client.post(self.login_url, data=payload)
        refresh = response.json()["refresh"]

        # обновление
        response = self.client.post(self.refresh_url, data={"refresh": refresh})
        result = response.json()["result"]

        # # проверяем что получаем статус 200
        # self.assertEqual(response.status_code, 200)
        #
        # # проверяем что получаем оба обновление и доступ токен
        # self.assertTrue(result["access"])
        # self.assertTrue(result["refresh"])


class TestUserInfo(APITestCase):
    profile_url = "/user/profile"
    file_upload_url = "/message/file-upload"
    login_url = "/user/login"

    def setUp(self):
        payload = {
            "username": "adefemigreat",
            "password": "ade123",
            "email": "adefemigreat@yahoo.com"
        }

    def test_post_user_profile(self):
        payload = {
            "user_id": self.user.id,
            "first_name": "Adefemi",
            "last_name": "Greate",
            "caption": "Being alive is different from living",
            "about": "I am a passionation lover of ART, graphics and creation"
        }

        response = self.client.post(self.profile_url, data=payload)
        result = response.json()["result"]

        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["first_name"], "Adefemi")
        self.assertEqual(result["last_name"], "Greate")
        self.assertEqual(result["user"]["username"], "adefemigreat")

