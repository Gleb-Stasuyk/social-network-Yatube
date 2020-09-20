# Generated by Django 2.2.9 on 2020-07-31 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20200731_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='group',
        ),
        migrations.AddField(
            model_name='post',
            name='group',
            field=models.ManyToManyField(blank=True, null=True, to='posts.Group', verbose_name='Сообщества'),
        ),
    ]