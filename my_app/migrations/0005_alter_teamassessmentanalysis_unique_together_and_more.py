# Generated by Django 5.1.7 on 2025-04-04 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_teamassessmentanalysis'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='teamassessmentanalysis',
            unique_together={('team', 'assessment')},
        ),
        migrations.AlterField(
            model_name='teamassessmentanalysis',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='QuestionAnalysisCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_type', models.CharField(max_length=10)),
                ('summary', models.TextField()),
                ('analysis', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.assessment')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.assessmentquestion')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.team')),
            ],
            options={
                'unique_together': {('team', 'assessment', 'question')},
            },
        ),
    ]
