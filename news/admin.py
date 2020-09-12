from avatar.models import Avatar
from django.contrib import admin
from django.contrib.auth.models import User, Group
import datetime
from multiprocessing import Process
from django.core.mail import send_mail, EmailMessage
from django.template import loader

from .email_queue import new_send_email
from .models import Articles, Profile, Tag, Comments
from .token import account_activation_token
import sys
sys.path.append("..")
from lab3.settings import ALLOWED_HOSTS

def send_letter(modeladmin, request, queryset):
    for q in queryset:
        q.user.profile.verified_token = account_activation_token.make_token(q.user)
        q.user.save()
        VERIFY_URL = (f'http://{ALLOWED_HOSTS[0]}/news/{q.user.profile.verified_token}/verify/')
        date = datetime.datetime.now()
        html_message1 = loader.render_to_string('news/html-message.html', {
            'user': q.user.username,
            'verify_ulr': VERIFY_URL,
            'date': date
        })
        mail = EmailMessage("Письмо подтверждения", html_message1, to=[f'{q.user.email}'])
        new_send_email(mail)

send_letter.short_description = 'Sending mails'


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'verified')
    actions = [send_letter]


admin.site.register(Profile, CustomUserAdmin)
admin.site.register(Articles)
admin.site.register(Tag)
admin.site.register(Comments)
