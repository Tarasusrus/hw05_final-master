from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'text': 'Сообщение',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Сообщение писать туть',
            'group': 'Выбрать группу туть',
            'image': 'Изображение'
        }
        fields = ('text', 'group', "image")


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Пост пуст')
        return data
