# Generated by Django 2.1.3 on 2019-04-17 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190415_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fullname',
            field=models.CharField(default='Default Name', max_length=50),
        ),
    ]
