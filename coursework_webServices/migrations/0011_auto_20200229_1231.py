# Generated by Django 2.2.5 on 2020-02-29 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coursework_webServices', '0010_auto_20200229_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='professor_code',
        ),
        migrations.AddField(
            model_name='rating',
            name='professor_code',
            field=models.ManyToManyField(to='coursework_webServices.Professor'),
        ),
    ]
