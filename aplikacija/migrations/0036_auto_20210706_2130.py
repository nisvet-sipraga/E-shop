# Generated by Django 3.1.12 on 2021-07-06 19:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacija', '0035_auto_20210706_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopcart',
            name='kolicina',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='shopcart',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 7, 21, 30, 38, 224329)),
        ),
    ]
