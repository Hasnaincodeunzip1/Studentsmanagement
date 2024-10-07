# Generated by Django 5.1.1 on 2024-09-30 04:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PRESENT', 'Present'), ('ABSENT', 'Absent'), ('TRAINER_ABSENT', 'Trainer Absent'), ('OFF', 'Off'), ('COMP', 'Comp')], max_length=20)),
                ('class_content', models.TextField(blank=True)),
                ('student_feedback', models.CharField(choices=[('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('NO_ACTION', 'No Action')], default='NO_ACTION', max_length=20)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('trainer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trainer_attendances', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.TextField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.attendance')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]