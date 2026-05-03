from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.common_test import (
    BaseTestCase, ADD_URL, SUCCESS_URL
)


class TestNoteCreation(BaseTestCase):
    """Тесты создания заметок."""

    def test_anonymous_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(ADD_URL, data={
            'title': 'Новая',
            'text': 'Текст',
            'slug': 'new-slug'
        })
        self.assertEqual(Note.objects.count(), notes_count)

    def test_author_can_create_note(self):
        """Автор может создать заметку."""
        notes_count = Note.objects.count()
        response = self.author_client.post(ADD_URL, data={
            'title': 'Новая заметка',
            'text': 'Текст',
            'slug': 'unique-slug'
        })
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(BaseTestCase):
    """Тесты редактирования и удаления заметок."""

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        url = self.get_edit_url(self.note)
        notes_count = Note.objects.count()
        new_title = 'Обновлённый заголовок'
        response = self.author_client.post(url, data={
            'title': new_title,
            'text': self.note.text,
            'slug': self.note.slug,
        })
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, new_title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)

    def test_reader_cant_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        url = self.get_edit_url(self.note)
        notes_count = Note.objects.count()
        response = self.not_author_client.post(url, data={
            'title': 'Взлом',
            'text': 'Текст',
            'slug': self.note.slug,
        })
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
        self._assert_note_identity(self.note, self.note)

    def test_author_can_delete_note(self):
        """Автор может удалить заметку."""
        url = self.get_delete_url(self.note)
        notes_count = Note.objects.count()
        response = self.author_client.post(url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        url = self.get_delete_url(self.note)
        notes_count = Note.objects.count()
        response = self.not_author_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
        self._assert_note_identity(self.note, self.note)


class TestNoteFormLogic(BaseTestCase):
    """Тесты логики формы."""

    def test_slug_autogeneration(self):
        """Проверка автоматической генерации slug."""
        title = 'Новая заметка'
        data = {'title': title, 'text': 'Текст'}
        self.author_client.post(ADD_URL, data=data)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_duplicate_slug_error(self):
        """Ошибка при дублировании slug."""
        notes_count = Note.objects.count()
        data = {
            'title': 'Другой заголовок',
            'text': 'Текст',
            'slug': self.note.slug
        }
        response = self.author_client.post(ADD_URL, data=data)
        self.assertFormError(
            response.context['form'],
            'slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), notes_count)
