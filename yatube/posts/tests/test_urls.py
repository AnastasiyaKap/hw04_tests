from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group"
        )

    def setUp(self):
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_non = User.objects.create_user(username="HasNoPosts")
        self.authorized_client_no_posts = Client()
        self.authorized_client_no_posts.force_login(self.user_non)
        self.post = Post.objects.create(
            text="Тестовый текст",
            author=self.user
        )

    def test_urls_uses_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): "posts/index.html",
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_guest(self):
        """URL-адрес доступен любому пользователю."""
        code_answer_for_users = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.FOUND,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in code_answer_for_users.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_auth_author(self):
        """URL-адрес доступен зарегистрированному пользователю."""
        code_answer_for_users = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in code_answer_for_users.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_auth_edit(self):
        """URL-адрес редактирования доступен автору."""
        code_answer_for_users = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, code in code_answer_for_users.items():
            with self.subTest(address=address):
                cache.clear()
                response = self.authorized_client_no_posts.get(address)
                self.assertEqual(response.status_code, code)
