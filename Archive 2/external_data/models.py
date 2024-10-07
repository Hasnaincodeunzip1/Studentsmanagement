# external_data/models.py
from django.db import models

class ExternalLead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20)
    course = models.CharField(max_length=255)
    slot_1 = models.TimeField(null=True, blank=True)
    slot_2 = models.TimeField(null=True, blank=True)
    slot_3 = models.TimeField(null=True, blank=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    remarks = models.TextField(blank=True)
    coordinator_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.course}"