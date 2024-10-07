from .models import Notification
from users.models import User
from django.utils import timezone

def create_notification(recipient, notification_type, message):
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        expires_at=timezone.now() + timezone.timedelta(hours=48)
    )

def notify_admins_and_managers(notification_type, message):
    admins_and_managers = User.objects.filter(role__in=['ADMIN', 'MANAGER'])
    for user in admins_and_managers:
        create_notification(user, notification_type, message)

def notify_course_hold_request(course_hold):
    notify_admins_and_managers('COURSE_HOLD_REQUEST', f"New course hold request from {course_hold.student_course.student.username}")

def notify_course_hold_decision(course_hold):
    create_notification(course_hold.student_course.student, 'COURSE_HOLD_DECISION', f"Your course hold request has been {course_hold.status.lower()}")

def notify_leave_request(leave_request):
    notify_admins_and_managers('LEAVE_REQUEST', f"New leave request from trainer {leave_request.user.username}")

def notify_leave_decision(leave_request):
    create_notification(leave_request.user, 'LEAVE_DECISION', f"Your leave request has been {leave_request.status.lower()}")

def notify_new_study_material(study_material):
    if study_material.course:
        students = User.objects.filter(studentcourse__course=study_material.course)
    elif study_material.student_course:
        students = [study_material.student_course.student]
    
    for student in students:
        create_notification(student, 'NEW_STUDY_MATERIAL', f"New study material available for {study_material.topic}")

def notify_feedback_submission(feedback):
    notify_admins_and_managers('FEEDBACK_SUBMISSION', f"New feedback submitted by {feedback.student.username}")

def notify_trainer_assignment(trainer, course):
    create_notification(trainer, 'TRAINER_ASSIGNMENT', f"You have been assigned to the course: {course.name}")

def notify_new_notice(notice):
    if notice.audience == 'ALL':
        recipients = User.objects.all()
    elif notice.audience == 'STUDENTS':
        recipients = User.objects.filter(role='STUDENT')
    elif notice.audience == 'STUDENTS_TRAINERS':
        recipients = User.objects.filter(role__in=['STUDENT', 'TRAINER'])
    elif notice.audience == 'ADMINS_MANAGERS':
        recipients = User.objects.filter(role__in=['ADMIN', 'MANAGER'])
    
    for recipient in recipients:
        create_notification(recipient, 'NEW_NOTICE', f"New notice: {notice.title}")