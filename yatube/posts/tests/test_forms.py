from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.constant import TEXT_CREATE_POST_FORM
from posts.models import Group, Post, Comment

User = get_user_model()


class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')

    def test_create_post(self):
        '''Проверка создания поста'''
        posts_count = Post.objects.count()
        form_data = {'text': TEXT_CREATE_POST_FORM,
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:create_post'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text=TEXT_CREATE_POST_FORM,
            group=self.group.id,
            author=self.user
        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в базу данных'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)

    def test_can_edit_post(self):
        '''Проверка прав редактирования'''
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_post = self.post
        self.group2 = Group.objects.create(title='Тестовая группа2',
                                           slug='test-group1',)
        form_data = {'text': TEXT_CREATE_POST_FORM,
                     'group': self.group2.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name1 = 'Данные поста не совпадают'
        self.assertTrue(Post.objects.filter(
            id=self.post.id,
            group=self.group2.id,
            author=self.user,
            pub_date=self.post.pub_date,
            text=TEXT_CREATE_POST_FORM
        ).exists(), error_name1)
        error_name1 = 'Пользователь не может изменить содержание поста'
        self.assertNotEqual(old_post.text, form_data['text'], error_name1)
        error_name2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(old_post.group, form_data['group'], error_name2)

class CommentFormTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        self.comment = Comment.objects.create(post_id=self.post.id,
                                              author=self.user,
                                              text='Тестовый коммент')

    def test_create_comment(self):
        '''Проверка создания комментария'''
        comment_count = Comment.objects.count()
        form_data = {'post_id': self.post.id,
                     'text': 'Тестовый коммент2'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        error_name1 = 'Данные комментария не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(
                        text='Тестовый коммент2',
                        post=self.post.id,
                        author=self.user
                        ).exists(), error_name1)
        error_name2 = 'Комментарий не добавлен в базу данных'
        self.assertEqual(Comment.objects.count(),
                         comment_count + 1,
                         error_name2)

    def test_no_edit_comment(self):
        '''Проверка запрета комментирования не авторизованого пользователя'''
        posts_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент2'}
        response = self.guest_client.post(reverse('posts:add_comment',
                                          kwargs={'post_id': self.post.id}),
                                          data=form_data,
                                          follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Комментарий добавлен в базу данных по ошибке'
        self.assertNotEqual(Comment.objects.count(),
                            posts_count + 1,
                            error_name2)

    def test_comment_null(self):
        '''Запрет пустого комментария'''
        posts_count = Comment.objects.count()
        form_data = {'text': ''}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Комментарий добавлен в базу данных по ошибке'
        self.assertNotEqual(Comment.objects.count(),
                            posts_count + 1,
                            error_name2)
