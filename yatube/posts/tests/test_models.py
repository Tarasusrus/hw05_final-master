from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constant import LEN_OF_POSTS
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_title_label(self):
        """Проверка заполнения verbose_name в модели Post."""
        field_verboses = {'text': 'Текст сообщения',
                          'pub_date': 'Дата публикации',
                          'author': 'Автор публикации',
                          'group': 'Группа',
                          }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value, error_name)

    def test_title_help_text(self):
        """Проверка заполнения help_text"""
        field_text_helps = {
            'text': 'Текст нового сообщения',
            'group': 'Модель группы'
        }
        for field, expected_value in field_text_helps.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value, error_name
                )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        error_name = f"Вывод не имеет {LEN_OF_POSTS} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:LEN_OF_POSTS],
                         error_name)

    def test_models_have_correct_titlr_names(self):
        """Проверяем, что у моделей gtoup корректно работает __str__."""
        error_name = f'Поле {self.group.title} не соответсвует ожиданиям'
        self.assertEqual(self.group.__str__(),
                         self.group.title,
                         error_name)
