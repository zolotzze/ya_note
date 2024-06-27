from django.test import TestCase, Client
from django.contrib.auth.models import User


class BaseTestCase(TestCase):
    """
    Базовый класс для общих настроек тестов.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Создает тестовых пользователей для использования в тестах.
        """
        cls.author = User.objects.create_user(
            username='author', password='password'
        )
        cls.not_author = User.objects.create_user(
            username='not_author', password='password'
        )
        cls.admin_user = User.objects.create_superuser(
            username='admin', password='password'
        )
        cls.another_user = User.objects.create_user(
            username='Другой пользователь', password='password'
        )

    def login_client(self, username, password):
        """
        Вспомогательный метод для логина клиента.
        """
        client = Client()
        client.login(username=username, password=password)
        return client

    def setUp(self):
        """
        Инициализирует клиентов для различных типов пользователей.
        """
        self.client = Client()
        self.admin_client = self.login_client('admin', 'password')
        self.author_client = self.login_client('author', 'password')
        self.not_author_client = self.login_client('not_author', 'password')
        self.another_client = self.login_client(
            'Другой пользователь', 'password'
        )
