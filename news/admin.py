from avatar.models import Avatar
from django.contrib import admin
from django.contrib.auth.models import User, Group
import datetime
from multiprocessing import Process
from django.core.mail import send_mail
from .models import Articles, Profile, Tag, Comments


def send_letter(modeladmin, request, queryset):

    VERIFY_URL = (f'http://127.0.0.1:8000/news/{queryset[0].user.profile.verified_token}/verify/')

    date = datetime.datetime.now()
    proc = Process(target=send_mail(
            'Письмо подтверждения',
            f'Здравствуйте уважаемый(ая), {queryset[0].user.username}! Пожалуйста, перейдите по ссыке, для подтверждения своего аккаунта: {VERIFY_URL}. '
            f'Дата отправки письма: {date}',
            'lilstone1337@gmail.com',
            [f'{queryset[0].user.email}'],
            fail_silently=False
        )
    )
    proc.start()
    proc.join()


send_letter.short_description = 'Sending mails'


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'verified')
    actions = [send_letter]


admin.site.register(Profile, CustomUserAdmin)
admin.site.register(Articles)
admin.site.register(Tag)
admin.site.register(Comments)
