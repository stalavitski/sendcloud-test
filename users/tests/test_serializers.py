from django.test import TestCase

from users.serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    # create tests
    def test__create__encrypts_password__on_registration(self):
        # Arrange
        serializer = UserSerializer()
        password = 'test_password'
        data = {
            'email': 'test@email.com',
            'password': password,
            'username': 'test_username'
        }
        # Act
        user = serializer.create(data)
        # Assert
        self.assertIsNotNone(user.password)
        self.assertNotEqual(user.password, password)
