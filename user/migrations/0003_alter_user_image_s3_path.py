# Generated by Django 4.0.5 on 2022-07-08 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_image_s3_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image_s3_path',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
