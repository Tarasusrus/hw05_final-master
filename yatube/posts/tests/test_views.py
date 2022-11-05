import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube import settings
from ..constant import M_CONSTANT
from ..forms import forms
from ..models import Group, Post, Comment, Follow

TEST_OF_POST: int = 13
User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Test title',
                                          slug='Test_group')
        for i in range(M_CONSTANT):
            Post.objects.create(
                text='Тестовый пост номер ' + str(i),
                author=self.user,
                group=self.group
            )

    def test_correct_page_context_guest_client(self):
        """Проверка количесва постов на первой и второй страницах"""
        pages: tuple = (reverse('posts:index'),
                        reverse('post:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_posts',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response_1 = self.client.get(page)
            response_2 = self.client.get(page + '?page=2')
            count_posts1 = len(response_1.context['page_obj'])
            count_posts2 = len(response_2.context['page_obj'])
            error_name_1 = (f'Ошибка: {count_posts1} постов,'
                            f'Должно {M_CONSTANT}')
            error_name_2 = (f'Ошибка: {count_posts2} постов,'
                            f'Должно {M_CONSTANT}')
            self.assertEqual(count_posts1,
                             M_CONSTANT,
                             error_name_1)
            self.assertEqual(count_posts2,
                             M_CONSTANT,
                             error_name_2)

    def test_correct_page_context_authorized_client(self):
        '''Проверка контекста страниц авторизованного пользователя'''
        pages = [reverse('posts:index'),
                 reverse('posts:profile',
                         kwargs={'username': f'{self.user.username}'}),
                 reverse('posts:group_posts',
                         kwargs={'slug': f'{self.group.slug}'})]
        for page in pages:
            response1 = self.authorized_client.get(page)
            response2 = self.authorized_client.get(page + '?page=2')
            count_posts1 = len(response1.context['page_obj'])
            count_posts2 = len(response2.context['page_obj'])
            error_name_1 = (f'Ошибка: {count_posts1} постов,'
                            f' должно {M_CONSTANT}')
            error_name_2 = (f'Ошибка: {count_posts2} постов,'
                            f'должно {M_CONSTANT}')
            self.assertEqual(count_posts1,
                             M_CONSTANT,
                             error_name_1)
            self.assertEqual(count_posts2,
                             M_CONSTANT,
                             error_name_2)


class ViewsTest(TestCase):

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.user = User.objects.create_user(username='auth')
        self.user2 = User.objects.create_user(username='auth2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.post = Post.objects.create(text='Тестовый текст',
                                        group=self.group,
                                        author=self.user)

    def test_views_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug':
                                f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                                f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                                self.post.id}): 'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                                self.post.id}): 'posts/create_post.html'}
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост',
                       response.context['post'].group: self.group,
                       response.context['post'].author:
                           self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_create_post_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group,
            image=self.uploaded)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')
        var_group = response_group.context['group']
        var_profile = response_profile.context['author']
        self.assertEqual(post.group, var_group, ' нет переменной группы')
        self.assertEqual(post.author, var_profile, ' нет переменной автора')

    def test_cache_context(self):
        '''Проверка кэширования страницы index'''
        before_create_post = self.authorized_client.get(
            reverse('posts:index'))
        first_item_before = before_create_post.content
        Post.objects.create(
            author=self.user,
            text='Проверка кэша',
            group=self.group)
        after_create_post = self.authorized_client.get(reverse('posts:index'))
        first_item_after = after_create_post.content
        self.assertEqual(first_item_after, first_item_before)
        cache.clear()
        after_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_item_after, after_clear)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.post = Post.objects.create(text='Тестовый текст',
                                        group=self.group,
                                        author=self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с
           правильным контекстом комментария."""
        self.comment = Comment.objects.create(post_id=self.post.id,
                                              author=self.user,
                                              text='Тестовый коммент')
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        comments = {response.context['comments'][0].text: 'Тестовый коммент',
                    response.context['comments'][0].author: self.user.username
                    }
        for value, expected in comments.items():
            self.assertEqual(comments[value], expected)
        self.assertTrue(response.context['form'], 'форма получена')


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.author = User.objects.create_user(username='someauthor')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_user_follower_authors(self):
        '''Посты доступны пользователю, который подписался на автора.
           Увеличение подписок автора'''
        count_follow = Follow.objects.filter(user=FollowViewsTest.user).count()
        data_follow = {'user': FollowViewsTest.user,
                       'author': FollowViewsTest.author}
        url_redirect = reverse(
            'posts:profile',
            kwargs={'username': FollowViewsTest.author.username})
        response = self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={
                'username': FollowViewsTest.author.username}),
            data=data_follow, follow=True)
        new_count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        self.assertTrue(Follow.objects.filter(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author).exists())
        self.assertRedirects(response, url_redirect)
        self.assertEqual(count_follow + 1, new_count_follow)

    def test_user_unfollower_authors(self):
        '''Посты не доступны пользователю, который не подписался на автора.
           Непроисходит увеличение подписок автора'''
        count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        data_follow = {'user': FollowViewsTest.user,
                       'author': FollowViewsTest.author}
        url_redirect = ('/auth/login/?next=/profile/'
                        f'{self.author.username}/unfollow/')
        response = self.guest_client.post(
            reverse('posts:profile_unfollow', kwargs={
                'username': FollowViewsTest.author}),
            data=data_follow, follow=True)
        new_count_follow = Follow.objects.filter(
            user=FollowViewsTest.user).count()
        self.assertFalse(Follow.objects.filter(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author).exists())
        self.assertRedirects(response, url_redirect)
        self.assertEqual(count_follow, new_count_follow)

    def test_follower_see_new_post(self):
        """У подписчика появляется новый пост избранного автора.
           А у не подписчика его нет"""
        new_post_follower = Post.objects.create(
            author=FollowViewsTest.author,
            text='Текстовый текст')
        Follow.objects.create(user=FollowViewsTest.user,
                              author=FollowViewsTest.author)
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        new_posts = response_follower.context['page_obj']
        self.assertIn(new_post_follower, new_posts)

    def test_unfollower_no_see_new_post(self):
        """У не подписчика поста нет"""
        new_post_follower = Post.objects.create(
            author=FollowViewsTest.author,
            text='Текстовый текст')
        Follow.objects.create(user=FollowViewsTest.user,
                              author=FollowViewsTest.author)
        response_unfollower = self.authorized_client2.get(
            reverse('posts:follow_index'))
        new_post_unfollower = response_unfollower.context['page_obj']
        self.assertNotIn(new_post_follower, new_post_unfollower)


