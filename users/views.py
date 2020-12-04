#  функция reverse_lazy позволяет получить URL по параметру "name" функции path()
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # login — это параметр "name" в path()
    success_url = reverse_lazy("login")
    template_name = "signup.html"
