from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from http import HTTPStatus
from notes.models import Note
from pytils.translit import slugify
from notes.forms import WARNING  
from .base_test_case import BaseTestCase


class TestLogic(BaseTestCase):
    """
    Тесты для проверки логики создания, редактирования и удаления заметок.
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
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'novaya-zametka'
        }

    def test_user_can_create_note(self):
        """
        Проверяет, что авторизованный пользователь может создать заметку.
        """
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title=self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """
        Проверяет, что анонимный пользователь не может создать заметку.
        """
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        """
        Проверяет, что невозможно создать две заметки с одинаковым slug.
        """
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """
        Проверяет, что если при создании заметки не заполнен slug,
        то он формируется автоматически с помощью функции 
        pytils.translit.slugify.
        """
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(title=self.form_data['title'])
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """
        Проверяет, что пользователь может редактировать свои заметки.
        """
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """
        Проверяет, что пользователь не может редактировать чужие заметки.
        """
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.not_author_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_author_can_delete_note(self):
        """
        Проверяет, что пользователь может удалять свои заметки.
        """
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """
        Проверяет, что пользователь не может удалять чужие заметки.
        """
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

if __name__ == '__main__':
    unittest.main()
