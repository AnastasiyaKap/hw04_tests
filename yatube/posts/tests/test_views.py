from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import Group, Post
from django import forms

User = get_user_model()

NUMBERS_PAGES_FIRST = 10

NUMBERS_PAGES_SECOND = 3


class PostPagesTests(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.user_test = User.objects.create_user(username='test-2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-slug №2',
            description='Тестовое описание группы №2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): "posts/create_post.html",
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, PostPagesTests.user)
        self.assertEqual(post_group_0, PostPagesTests.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание группы')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(response.context.get('author'),
                         PostPagesTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').id,
                         PostPagesTests.post.id)
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(response.context.get('user'),
                         PostPagesTests.post.author)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_create_correct(self):
        """Дополнительная проверка при создании поста."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_test)
        create_new_post = Post.objects.create(
            author=PostPagesTests.user_test,
            text='Тест',
            group=PostPagesTests.group2
        )
        # Делаем проверку, что пост
        # попал на index
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_text_0, create_new_post.text)
        self.assertEqual(post_author_0, create_new_post.author)
        self.assertEqual(post_group_0, create_new_post.group)
        # Делаем проверку, что пост
        # попал на страницу группы
        cache.clear()
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group2.slug}
            )
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, create_new_post.text)
        self.assertEqual(post_id_0, create_new_post.id)
        # Делаем проверку, что пост
        # попал на страницу профайла
        cache.clear()
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user_test}
            )
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        self.assertEqual(post_text_0, create_new_post.text)
        self.assertEqual(post_id_0, create_new_post.id)
        # Делаем проверку, что пост
        # не попал в другую группу
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        self.assertFalse('Тестовая группа №2' in
                         str(response.context['group']))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст{i}',
                group=cls.group
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Проверка Paginator на первой страницце."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj')),
                         NUMBERS_PAGES_FIRST)

        response2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response2.context.get('page_obj')),
                         NUMBERS_PAGES_FIRST)

        response3 = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(len(response3.context.get('page_obj')),
                         NUMBERS_PAGES_FIRST)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         NUMBERS_PAGES_SECOND)

        response2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
            + '?page=2'
        )
        self.assertEqual(len(response2.context.get('page_obj')),
                         NUMBERS_PAGES_SECOND)

        response3 = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
            + '?page=2'
        )
        self.assertEqual(len(response3.context.get('page_obj')),
                         NUMBERS_PAGES_SECOND)
