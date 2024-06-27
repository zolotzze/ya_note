from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm
from .base_test_case import BaseTestCase  # Импортируем базовый класс


class TestContent(BaseTestCase):
    """
    Тесты для проверки отображения заметок в списке заметок и наличия форм на
    страницах создания и редактирования заметок.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Создает тестовых пользователей и тестовую заметку для использования в
        тестах.
        """
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заметка', text='Текст заметки', author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """
        Проверяет, что отдельная заметка передается на страницу со списком
        заметок в списке object_list в словаре context, и что в список заметок
        одного пользователя не попадают заметки другого пользователя.
        """
        url = reverse('notes:list')
        response_author = self.author_client.get(url)
        response_not_author = self.not_author_client.get(url)

        # Проверяем, что заметка есть в списке для автора
        object_list_author = response_author.context['object_list']
        self.assertIn(self.note, object_list_author)

        # Проверяем, что заметки нет в списке для не автора
        object_list_not_author = response_not_author.context['object_list']
        self.assertNotIn(self.note, object_list_not_author)

    def test_pages_contains_form(self):
        """
        Проверяет, что на страницы создания и редактирования заметки
        передаются формы.
        """
        urls_with_args = [
            ('notes:add', None),
            ('notes:edit', [self.note.slug])
        ]
        for name, args in urls_with_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                # Проверяем, есть ли объект формы в словаре контекста
                self.assertIn('form', response.context)
                # Проверяем, что объект формы относится к нужному классу
                self.assertIsInstance(response.context['form'], NoteForm)


if __name__ == '__main__':
    unittest.main()
