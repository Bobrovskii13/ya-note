from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestHomePage(TestCase):
    """Тесты главной страницы."""

    def test_home_page_available(self):
        """Главная страница доступна всем пользователям."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestListPage(TestCase):
    """Тесты страницы списка заметок."""

    @classmethod
    def setUpTestData(cls):
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

    def test_list_only_author_notes(self):
        """В списке только заметки текущего пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))

        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.other_note, object_list)


class TestDetailPage(TestCase):
    """Тесты страницы заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='test-note',
            author=cls.author
        )
        cls.url = reverse('notes:detail', args=(cls.note.slug,))

    def test_author_can_open_detail(self):
        """Автор может открыть свою заметку."""
        self.client.force_login(self.author)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['object'], self.note)

    def test_anonymous_redirect(self):
        """Анонимный пользователь перенаправляется."""
        response = self.client.get(self.url)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={self.url}')


class TestCreateEditPages(TestCase):
    """Тесты страниц создания и редактирования."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='test-note',
            author=cls.user
        )

    def test_create_page_has_form(self):
        """Страница создания содержит форму."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:add'))

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_has_form(self):
        """Страница редактирования содержит форму."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('notes:edit', args=(self.note.slug,))
        )

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_delete_page_confirmation(self):
        """Страница удаления содержит подтверждение."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('notes:delete', args=(self.note.slug,))
        )

        self.assertContains(response, 'Удалить заметку')
