# Generated by Django 4.0 on 2021-12-27 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0003_tag_remove_job_skills_job_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(max_length=30),
        ),
    ]
