# Generated by Django 4.0.5 on 2022-07-08 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innotter_functional', '0006_post_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='image',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
