# Generated by Django 4.1 on 2023-05-02 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("word_e_back", "0007_remove_데이터셋_모델"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="태그",
            name="모델",
        ),
    ]
