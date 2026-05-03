from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')


class BaseTestCase(TestCase):
    """Базовый класс для тестов: создает пользователей и заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка тестовых данных: пользователей, заметок и клиентов."""
        cls.author = User.objects.create_user(username='author')
        cls.other_user = User.objects.create_user(username='other')
        cls.note = Note.objects.create(
            title='Моя заметка',
            text='Текст',
            slug='my-note',
            author=cls.author
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст',
            slug='other-note',
            author=cls.other_user
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.other_user)

    def _assert_note_identity(self, note, original_note):
        """Проверяет, что поля заметки в базе совпадают с исходными."""
        note_from_db = Note.objects.get(pk=note.pk)
        self.assertEqual(note_from_db.title, original_note.title)
        self.assertEqual(note_from_db.text, original_note.text)
        self.assertEqual(note_from_db.slug, original_note.slug)
        self.assertEqual(note_from_db.author, original_note.author)

    def get_detail_url(self, note):
        """Возвращает URL страницы отдельной заметки."""
        return reverse('notes:detail', args=(note.slug,))

    def get_edit_url(self, note):
        """Возвращает URL страницы редактирования заметки."""
        return reverse('notes:edit', args=(note.slug,))

    def get_delete_url(self, note):
        """Возвращает URL страницы удаления заметки."""
        return reverse('notes:delete', args=(note.slug,))
