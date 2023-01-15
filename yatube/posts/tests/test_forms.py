from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..forms import PostForm
from ..models import Post, Group
from http import HTTPStatus


User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-form')
        # Создаем запись в базе данных
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group.id,
                author=self.user
            ).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Измененный текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(self.post.id,)
        ))
        edit_object = Post.objects.all().last()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(edit_object.text, 'Измененный текст')
        self.assertEqual(edit_object.author, self.user)
