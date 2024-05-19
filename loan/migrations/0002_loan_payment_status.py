# Generated by Django 5.0.6 on 2024-05-19 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='payment_status',
            field=models.SmallIntegerField(choices=[(0, 'FAILED'), (2, 'PAID'), (1, 'PENDING')], default=1),
        ),
    ]
