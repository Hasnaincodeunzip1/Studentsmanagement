from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('MESSAGE', 'New Message'),
        ('ABSENCE', 'Student Absence'),
        ('TRAINER_ABSENT', 'Trainer Absent'),
        ('COURSE_ENDING', 'Course Ending'),
        ('COURSE_HOLD_REQUEST', 'Course Hold Request'),
        ('COURSE_HOLD_DECISION', 'Course Hold Decision'),
        ('LEAVE_REQUEST', 'Leave Request'),
        ('LEAVE_DECISION', 'Leave Decision'),
        ('NEW_STUDY_MATERIAL', 'New Study Material'),
        ('FEEDBACK_SUBMISSION', 'Feedback Submission'),
        ('TRAINER_ASSIGNMENT', 'Trainer Assignment'),
        ('NEW_NOTICE', 'New Notice'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.created_at + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"