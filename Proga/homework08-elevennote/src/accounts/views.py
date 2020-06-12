from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views import View
from django.views.generic import FormView, TemplateView
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site

from .forms import UserCreationForm
from .models import User
import random


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = '/accounts/verify'

    def form_valid(self, form):
        form.save()

        email = self.request.POST['email']
        password = self.request.POST['password1']

        user = authenticate(email=email, password=password)
        user.is_active = False
        user.activation = str(random.getrandbits(100))
        user.save()
        send_mail('Your verification link', f'Here is your verification link: {str(get_current_site(self.request))}/accounts/verify/{user.activation}', 'noreply@prokhn.ru',
                  [user.email], fail_silently=False)
        # login(self.request, user)

        return super(RegisterView, self).form_valid(form)


def verify(request, activation_code=''):
    context = {'activation_code': activation_code}

    try:
        user = User.objects.get(activation=activation_code)
        context['user'] = user
        user.is_active = True
        user.save()
    except User.DoesNotExist:
        context['user'] = False

    return render(request, 'registration/verify.html', context=context)
