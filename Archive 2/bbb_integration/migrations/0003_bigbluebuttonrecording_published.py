# Generated by Django 5.1.1 on 2024-10-06 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbb_integration', '0002_bigbluebuttonrecording_internal_meeting_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bigbluebuttonrecording',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]