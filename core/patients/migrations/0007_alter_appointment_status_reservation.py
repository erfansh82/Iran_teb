# Generated by Django 3.2 on 2022-08-23 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0006_auto_20220822_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status_reservation',
            field=models.CharField(blank=True, choices=[('cancel', 'cancel'), ('reserve', 'reserve'), ('reserved', 'reserved'), ('free', 'free')], max_length=27, null=True),
        ),
    ]
