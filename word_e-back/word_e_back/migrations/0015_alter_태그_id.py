# Generated by Django 4.1 on 2023-05-05 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("word_e_back", "0014_alter_태그_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="태그",
            name="ID",
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
