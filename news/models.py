from random import choice
from string import ascii_uppercase

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.template.defaultfilters import slugify as django_slugify



User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    bio = models.TextField(max_length=500, blank=True,verbose_name="Статус", db_index=True)
    location = models.CharField(max_length=30, blank=True, verbose_name="Местоположение", db_index=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата Рождения", db_index=True)
    profile_avatar = models.ImageField(null=True, blank=True, upload_to='media/avatar', default='media/avatar/default_img.png',verbose_name="Аватар Профиля", db_index=True)
    verified = models.BooleanField(default=False)
    verified_token = models.TextField(default='')


    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        try:
            instance.profile.save()
        except ObjectDoesNotExist:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()




class Articles(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор Статьи', blank=True, null=True, db_index=True)
    objects = models.Manager()
    title = models.CharField(max_length=120, verbose_name="Заголовок", db_index=True)
    post = models.TextField(verbose_name="Текст статьи", db_index=True)
    date = models.DateTimeField(auto_now=True, db_index=True)
    image_p = models.ImageField(null=True, blank=True, upload_to='media/articles', verbose_name="Картинка", db_index=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts', db_index=True)

    def __str__(self):
        return self.title


alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e', 'ю': 'yu',
            'я': 'ya', ' ': '_'}


def slugify(s):
    s = s.lower()
    return django_slugify(''.join(alphabet.get(w, w) for w in s))


class Tag(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор Статьи', blank=True, null=True, db_index=True)
    tittle = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    objects = models.Manager()

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('tag_update', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.tittle)

    def save(self, *args, **kwargs):
        self.author_id = 1
        self.slug = slugify(self.tittle)
        super(Tag, self).save(*args, **kwargs)


class Comments(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, verbose_name='Статья', blank=True, null=True, related_name='comments_articles', db_index=True )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария', blank=True, null=True, db_index=True )
    create_date = models.DateTimeField(auto_now=True, db_index=True)
    text = models.TextField(verbose_name='Текст комментария')
    status = models.BooleanField(verbose_name='Видимость статьи', default=False, db_index=True)

