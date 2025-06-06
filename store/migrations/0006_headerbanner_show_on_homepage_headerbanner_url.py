# Generated by Django 5.2.1 on 2025-05-21 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_headerbanner_alter_brand_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerbanner',
            name='show_on_homepage',
            field=models.BooleanField(default=False, verbose_name='Показать только на главной странице'),
        ),
        migrations.AddField(
            model_name='headerbanner',
            name='url',
            field=models.URLField(blank=True, help_text='Куда ведёт баннер (оставьте пустым, если не нужно).', verbose_name='Ссылка'),
        ),
    ]
