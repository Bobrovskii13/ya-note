from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Проверка доступности страниц приложения notes."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных для всех тестов."""
        cls.author = User.objects.create_user(
            username='author',
            password='authorpassword'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='readerpassword'
        )
        cls.note = Note.objects.create(
            title='Записка',
            text='Текст записки',
            slug='testnote',
            author=cls.author
        )

    def test_pages_available(self):
        """Проверка страниц, доступных любому пользователю."""
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        logout_url = reverse('users:logout')
        response = self.client.post(logout_url)
        self.assertIn(response.status_code, (HTTPStatus.OK, HTTPStatus.FOUND))

    def test_pages_availability_for_auth_user(self):
        """Проверка страниц, доступных любому авторизованному пользователю."""
        self.client.force_login(self.author)
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Проверка доступа к страницам редактирования и удаления заметки."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        """Редирект анонима на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
