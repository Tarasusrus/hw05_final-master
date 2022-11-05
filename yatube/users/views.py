# Импортируем CreateView, чтобы создать ему наследника
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from .forms import ContactForm, CreationForm

# Импортируем класс формы, чтобы сослаться на неё во view-классе

class SignUp(CreateView):
    form_class = CreationForm  # из какого класса взять форму
    success_url = reverse_lazy('post:index')
    # После успешной регистрации перенаправляем пользователя на главную.
    template_name = 'users/signup.html'


def user_contact(request):
    form = ContactForm()
    return render(request, 'users/contact.html', {'form': form})
