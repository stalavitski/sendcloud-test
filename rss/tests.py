from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    def set_user(self):
        self.user = User.objects.create_user(
            email='email@test.com',
            username='username',
            password='password'
        )
