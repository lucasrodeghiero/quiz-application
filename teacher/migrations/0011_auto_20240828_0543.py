# Generated by Django 3.0.5 on 2024-08-28 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0010_auto_20240828_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='mobile',
            field=models.CharField(max_length=20),
        ),
    ]
