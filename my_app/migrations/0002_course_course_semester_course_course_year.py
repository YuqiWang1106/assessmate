# Generated by Django 5.1.7 on 2025-03-27 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_semester',
            field=models.CharField(default='Fall', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='course_year',
            field=models.CharField(default='2025', max_length=20),
            preserve_default=False,
        ),
    ]
