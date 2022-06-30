# Generated by Django 4.0.5 on 2022-06-24 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('innotter_functional', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='follows', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='page',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='pages', to='innotter_functional.tag'),
        ),
        migrations.AlterField(
            model_name='page',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=180)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='innotter_functional.page')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='innotter_functional.post')),
            ],
        ),
    ]
