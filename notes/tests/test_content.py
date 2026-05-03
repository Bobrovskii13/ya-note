from http import HTTPStatus

from notes.forms import NoteForm
from notes.tests.common_test import (
    BaseTestCase, HOME_URL, LIST_URL, LOGIN_URL, ADD_URL
)


class TestHomePage(BaseTestCase):
    """Тесты главной страницы."""

    def test_home_page_available(self):
        """Главная страница доступна всем пользователям."""
        response = self.client.get(HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestListPage(BaseTestCase):
    """Тесты страницы списка заметок."""

    def test_list_only_author_notes(self):
        """В списке только заметки текущего пользователя."""
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.other_note, object_list)


class TestDetailPage(BaseTestCase):
    """Тесты страницы заметки."""

    def test_author_can_open_detail(self):
        """Автор может открыть свою заметку."""
        url = self.get_detail_url(self.note)
        response = self.author_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['note'], self.note)

    def test_anonymous_redirect(self):
        """Анонимный пользователь перенаправляется."""
        url = self.get_detail_url(self.note)
        response = self.client.get(url)
        expected_url = f'{LOGIN_URL}?next={url}'
        self.assertRedirects(response, expected_url)


class TestCreateEditPages(BaseTestCase):
    """Тесты страниц создания и редактирования."""

    def test_create_page_has_form(self):
        """Страница создания содержит форму."""
        response = self.author_client.get(ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_has_form(self):
        """Страница редактирования содержит форму."""
        url = self.get_edit_url(self.note)
        response = self.author_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_delete_page_confirmation(self):
        """Страница удаления содержит подтверждение."""
        url = self.get_delete_url(self.note)
        response = self.author_client.get(url)
        self.assertContains(response, 'Удалить заметку')
