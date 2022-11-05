from django.contrib.auth import get_user_model
from django.db import models

from posts.constant import LEN_OF_POSTS

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Слаг'
    )
    description = models.TextField(
        verbose_name="Описание туть")

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Текст нового сообщения'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'

    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Модель группы'
    )

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True)

    class Meta:
        verbose_name = 'Пост'
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:LEN_OF_POSTS]


class Comment(models.Model):
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Текст поста',
                             blank=True,
                             null=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Напишите комментарий')
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:LEN_OF_POSTS]


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='following',
                               on_delete=models.CASCADE)

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Лента автора'
        verbose_name_plural = 'Лента авторов'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_members')]
