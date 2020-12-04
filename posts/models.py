from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Сообщества"""
    title = models.CharField("Имя", max_length=200)
    description = models.TextField("Описание")
    slug = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста",
                            help_text="Введите текст поста")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, help_text="Выберите группу",
                              verbose_name="Сообщество", blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Комментарии"""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name="Текст комментария",
                            help_text="Введите текст комментария")
    created = models.DateTimeField('date creation', auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following")

    def __str__(self):
        return f'Подписан {self.user.username} на {self.author.username}'

    class Meta:
        unique_together = ('user', 'author')
