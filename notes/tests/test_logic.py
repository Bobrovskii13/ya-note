from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class BaseNoteTestCase(TestCase):
    """Базовый класс с данными для заметок."""

    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-slug'
    NEW_TITLE = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.reader = User.objects.create_user(username='reader')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')


class TestNoteCreation(BaseNoteTestCase):
    """Тесты создания заметок."""

    def test_anonymous_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(self.add_url, data={
            'title': 'Новая',
            'text': 'Текст',
            'slug': ''
        })
        self.assertEqual(Note.objects.count(), notes_count)

    def test_author_can_create_note(self):
        """Автор может создать заметку."""
        response = self.author_client.post(self.add_url, data={
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': ''
        })
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)

        note = Note.objects.latest('id')
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(BaseNoteTestCase):
    """Тесты редактирования и удаления заметок."""

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data={
            'title': self.NEW_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG,
        })
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)

    def test_reader_cant_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data={
            'title': 'Попытка взлома',
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG,
        })
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)


class TestNoteFormLogic(BaseNoteTestCase):
    """Тесты логики формы."""

    def test_slug_autogeneration(self):
        """Проверка автоматической генерации slug."""
        notes_count = Note.objects.count()
        title = 'Новая заметка'
        data = {'title': title, 'text': 'Текст'}
        self.author_client.post(self.add_url, data=data)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_duplicate_slug_error(self):
        """Ошибка при дублировании slug."""
        data = {
            'title': 'Другой заголовок',
            'text': 'Текст',
            'slug': self.NOTE_SLUG
        }
        response = self.author_client.post(self.add_url, data=data)
        self.assertFormError(
            response.context['form'],
            'slug',
            errors=(self.NOTE_SLUG + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)
