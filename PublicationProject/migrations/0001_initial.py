# Generated by Django 5.1.6 on 2025-04-05 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("project_title", models.CharField(max_length=100)),
                (
                    "project_pic",
                    models.ImageField(blank=True, upload_to="project_pics/"),
                ),
                ("Githuv_url", models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("paper_title", models.CharField(max_length=100)),
                (
                    "publication_pic",
                    models.ImageField(blank=True, upload_to="publication_pics/"),
                ),
                ("publication_url", models.URLField()),
            ],
        ),
    ]
