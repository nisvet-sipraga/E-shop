# Generated by Django 3.1.12 on 2021-07-10 15:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacija', '0037_auto_20210706_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopcart',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 11, 17, 53, 48, 373018)),
        ),
    ]
