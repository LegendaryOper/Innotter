# Generated by Django 4.0.5 on 2022-06-27 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('innotter_functional', '0004_alter_page_follow_requests'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
