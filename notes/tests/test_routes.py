from http import HTTPStatus

from notes.tests.common_test import (
    BaseTestCase, HOME_URL, LOGIN_URL, LOGOUT_URL,
    SIGNUP_URL, LIST_URL, ADD_URL, SUCCESS_URL
)


class TestRoutes(BaseTestCase):
    """Проверка доступности страниц приложения notes."""

    def test_pages_availability(self):
        """Проверка доступа: аноним, автор и не-автор."""
        test_data = (
            (self.client, (HOME_URL, LOGIN_URL, SIGNUP_URL), HTTPStatus.OK),
            (
                self.author_client,
                (LIST_URL, ADD_URL, SUCCESS_URL),
                HTTPStatus.OK
            ),
            (
                self.author_client,
                (
                    self.get_detail_url(self.note),
                    self.get_edit_url(self.note),
                    self.get_delete_url(self.note)
                ),
                HTTPStatus.OK
            ),
            (
                self.not_author_client,
                (
                    self.get_detail_url(self.note),
                    self.get_edit_url(self.note),
                    self.get_delete_url(self.note)
                ),
                HTTPStatus.NOT_FOUND
            ),
        )
        for client, urls, status in test_data:
            for url in urls:
                with self.subTest(url=url, client=client):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)
        with self.subTest(url=LOGOUT_URL):
            response = self.client.post(LOGOUT_URL)
            self.assertIn(
                response.status_code,
                (HTTPStatus.OK, HTTPStatus.FOUND)
            )

    def test_redirect_for_anonymous_user(self):
        """Редирект анонима на страницу логина."""
        urls = (
            ADD_URL,
            LIST_URL,
            SUCCESS_URL,
            self.get_detail_url(self.note),
            self.get_edit_url(self.note),
            self.get_delete_url(self.note),
        )
        for url in urls:
            with self.subTest(url=url):
                expected_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
