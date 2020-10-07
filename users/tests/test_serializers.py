from django.test import TestCase

from users.serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    # create tests
    def test__create__encrypt_password__on_registration(self):
        serializer = UserSerializer()
        password = 'test_password'
        data = {
            'email': 'test@email.com',
            'password': password,
            'username': 'test_username'
        }

        user = serializer.create(data)

        self.assertIsNotNone(user.password)
        self.assertNotEqual(user.password, password)
