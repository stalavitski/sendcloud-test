from rss.tests import BaseTestCase
from users.serializers import UserSerializer


class UserSerializerTestCase(BaseTestCase):
    # create tests
    def test__create__encrypt_password__on_registration(self) -> None:
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
