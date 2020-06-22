from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Model
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from .models import Articles, Profile, Tag
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from .forms import ArticleForm, AuthUserForm, RegisterUserForm, CommentForm, UserForm, ProfileForm, TagForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from multiprocessing import Process
from django.core.mail import send_mail
import datetime
import logging

info_logger = logging.getLogger('authentication_logger')
warning_logger = logging.getLogger('account_logger')


class CustomSuccessMessageMixin:
    @property
    def success_msg(self):
        return False

    def form_valid(self, form):
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)

    def get_success_url(self):
        return '%s?id=%s' % (self.success_url, self.object.id)


class HomeListView(ListView):
    model = Articles
    template_name = 'news/post.html'
    context_object_name = 'list_articles'

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        context.update({
            'tag_list': Tag.objects.order_by('tittle'),
            'articles_list': Articles.objects.order_by("-date")[:20],
        })
        return context

    def get_queryset(self):
        return Articles.objects.order_by("-date")[:20]


class HomeDetailView(CustomSuccessMessageMixin, FormMixin, DetailView):
    model = Articles
    template_name = 'news/post_page.html'
    context_object_name = 'get_article'
    form_class = CommentForm
    success_msg = 'Комментарий добавлен'

    def get_success_url(self):
        return reverse_lazy('detail_page', kwargs={'pk': self.get_object().id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


def post(self, request, *args, **kwargs):
    # form = self.get_form()
    form = ArticleForm(request.POST, request.FILES)
    if form.is_valid():
        return self.form_valid(form)
    else:
        return self.form_invalid(form)


class ArticleCreateView(LoginRequiredMixin, CustomSuccessMessageMixin, CreateView):
    model = Articles
    template_name = 'news/edit_page.html'
    form_class = ArticleForm
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись создана '

    def get_context_data(self, **kwargs):
        kwargs['list_articles'] = Articles.objects.all().order_by("-date")[:20]
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, CustomSuccessMessageMixin, UpdateView):
    model = Articles
    template_name = 'news/edit_page.html'
    form_class = ArticleForm
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись успешно обновлена'

    def get_context_data(self, **kwargs):
        kwargs['update'] = True
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user != kwargs['instance'].author:
            return self.handle_no_permission()
        return kwargs


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Articles
    template_name = 'news/edit_page.html'
    success_url = reverse_lazy('edit_page')
    success_msg = 'Запись удалена'

    def post(self, request, *args, **kwargs):
        messages.success(self.request, self.success_msg)
        return super().post(request)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.author:
            return self.handle_no_permission()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class FishingLoginView(LoginView):
    template_name = 'news/login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('edit_page')

    def get_success_url(self):
        info_logger.info(f'{self.request.user.username} LogIn his account.')
        return self.success_url


class FishingRegisterView(CreateView):
    model = User
    template_name = 'news/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('edit_page')
    success_msg = 'Успешная регистрация, проверьте почту на неё пришло письмо с подтверждением'

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        aut_user = authenticate(username=username, password=password)
        login(self.request, aut_user)
        verify_letter(self.request)
        info_logger.info(f'{self.request.user.username} Register new account.')
        return form_valid


class FishingLogoutView(LogoutView):

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            info_logger.info(f'{self.request.user.username} LogOut his account.')
            self.first_name = request.user.first_name
        return super().dispatch(request, *args, **kwargs)

    next_page = 'news_page'


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            if 'profile_avatar' in request.FILES:
                profile_form.photo = request.FILES['profile_avatar']
            user_form.save()
            profile_form.save()
            messages.success(request, ('Профиль успешно обновлен'))

            return HttpResponseRedirect(reverse_lazy('edit_page'))
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'news/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'news/profile_page.html'
    context_object_name = 'get_profile'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.get_object().id})


def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'news/tag_page.html', context={'tags': tags})


def tag_detail(request, slug):
    tag = Tag.objects.get(slug__iexact=slug)
    return render(request, 'news/tag_detail.html', context={'tag': tag})


class TagCreate(View):

    def get(self, request):
        form = TagForm()
        return render(request, 'news/tag_create.html', context={'form': form})

    def post(self, request):
        bound_form = TagForm(request.POST)
        if bound_form.is_valid():
            new_tag = bound_form.save()
            return redirect(new_tag)
        return render(request, 'news/tag_create.html', context={'form': bound_form})


class TagUpdate(View):

    def get(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        bound_form= TagForm(instance=tag)
        return render(request, 'news/tag_update.html', context={'form': bound_form, 'tag': tag})

    def post(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        bound_form = TagForm(request.POST, instance=tag)

        if bound_form.is_valid():
            new_tag = bound_form.save()
            return redirect(new_tag)
        return render(request, 'news/tag_update.html', context={'form': bound_form, 'tag': tag})


class TagDelete(View):
    def get(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        return render(request, 'news/tag_delete.html', context={'tag': tag})

    def post(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        tag.delete()
        return redirect(reverse('tags_page'))


def verify(request, token):
    request.user.profile.verified = True
    info_logger.info(f'{request.user.username} Verified account.')
    request.user.save()
    return redirect('news_page')


def verify_letter(request):
    VERIFY_URL = (f'http://127.0.0.1:8000/news/{request.user.profile.verified_token}/verify/')
    date = datetime.datetime.now()
    proc = Process(target=send_mail(
        'Письмо подтверждения',
        f'Здравствуйте уважаемый(ая), {request.user.username}! Пожалуйста, перейдите по ссыке, для подтверждения своего аккаунта: {VERIFY_URL}. '
        f'Дата отправки письма: {date}',
        'lilstone1337@gmail.com',
        [f'{request.user.email}'],
        fail_silently=False
    )
    )
    proc.start()
    proc.join()