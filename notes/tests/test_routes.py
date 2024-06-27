from http import HTTPStatus
from django.urls import reverse
from notes.models import Note
from .base_test_case import BaseTestCase  # Импортируем базовый класс


class TestRoutes(BaseTestCase):
    """
    Тесты для проверки доступности маршрутов и правильности перенаправлений
    для различных типов пользователей (анонимных, авторизованных и
    администраторов).
    """

    @classmethod
    def setUpTestData(cls):
        """
        Создает тестовых пользователей и заметку для использования в тестах.
        """
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Название заметки', text='Тестзаметки', author=cls.author
        )

    def test_home_availability_for_anonymous_user(self):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Аутентифицированному пользователю доступна страница со списком заметок
        (notes/), страница успешного добавления заметки (done/), и страница
        добавления новой заметки (add/).
        """
        urls = ['notes:list', 'notes:add', 'notes:success']
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.admin_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки доступны
        только автору заметки. Если на эти страницы попытается зайти другой
        пользователь, вернётся ошибка 404.
        """
        urls = ['notes:detail', 'notes:edit', 'notes:delete']
        clients = [
            (self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        ]
        for name in urls:
            for client, expected_status in clients:
                with self.subTest(name=name, client=client):
                    url = reverse(name, args=[self.note.slug])
                    response = client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """
        При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        urls_with_args = [
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]
        login_url = reverse('users:login')
        for name, args in urls_with_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)

    def test_auth_pages_availability_for_all_users(self):
        """
        Страницы регистрации пользователей, входа в учётную запись и выхода
        из неё доступны всем пользователям.
        """
        urls = ['users:login', 'users:signup', 'users:logout']
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


if __name__ == '__main__':
    unittest.main()
