from celery import shared_task
import logging

from django.utils import timezone
from .models import BigBlueButtonRoom, BigBlueButtonRecording
from courses.models import Course, StudentCourse
from .utils import create_meeting, end_meeting, is_meeting_running, get_meeting_info
import uuid
import requests
from django.conf import settings
from django.utils.http import urlencode
import hashlib
import xml.etree.ElementTree as ET
from django.utils import timezone
from datetime import datetime
import pytz
logger = logging.getLogger(__name__)

@shared_task
def create_bbb_rooms():
    # For group classes
    group_courses = Course.objects.filter(is_group_class=True)
    for course in group_courses:
        room, created = BigBlueButtonRoom.objects.get_or_create(
            course=course,
            defaults={'room_id': str(uuid.uuid4())}
        )
        if created:
            create_meeting(room.room_id, course.name, 'ap', 'mp')

    # For personal training
    personal_courses = StudentCourse.objects.filter(course__is_group_class=False)
    for student_course in personal_courses:
        room, created = BigBlueButtonRoom.objects.get_or_create(
            student_course=student_course,
            defaults={
                'room_id': str(uuid.uuid4()),
                'expiration_date': student_course.end_date + timezone.timedelta(days=7)
            }
        )
        if created:
            create_meeting(room.room_id, f"{student_course.course.name} - {student_course.student.username}", 'ap', 'mp')

@shared_task
def delete_expired_recordings():
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    expired_recordings = BigBlueButtonRecording.objects.filter(creation_date__lt=seven_days_ago)
    
    for recording in expired_recordings:
        recording.delete()


@shared_task
def sync_bbb_recordings():
    logger.info("Starting BBB recordings sync")
    
    rooms = {room.room_id: room for room in BigBlueButtonRoom.objects.exclude(room_id='')}
    logger.info(f"Found {len(rooms)} valid rooms in the database")
    logger.info(f"Room IDs in database: {', '.join(rooms.keys())}")

    if not rooms:
        logger.error("No valid BigBlueButtonRooms found. Cannot sync recordings.")
        return {"error": "No valid BigBlueButtonRooms found"}

    first_room = next(iter(rooms.values()))
    response = first_room.send_api_request('getRecordings', {})

    if response is None:
        logger.error("Failed to get recordings from BBB API")
        return {"error": "Failed to get recordings from BBB API"}

    if response.find('returncode').text == 'SUCCESS':
        recordings = response.findall('recordings/recording')
        logger.info(f"Found {len(recordings)} recordings in the API response")
        synced_count = 0
        skipped_count = 0
        unknown_rooms = set()
        
        for recording in recordings:
            record_id = recording.find('recordID').text
            meeting_id = recording.find('meetingID').text
            
            logger.info(f"Processing recording: {record_id} for meeting ID: {meeting_id}")
            
            room = rooms.get(meeting_id)
            if room:
                logger.info(f"Matching room found in database for meeting ID: {meeting_id}")
                
                start_time = int(recording.find('startTime').text) / 1000
                creation_date = datetime.fromtimestamp(start_time).replace(tzinfo=pytz.UTC)
                
                try:
                    recording_obj, created = BigBlueButtonRecording.objects.update_or_create(
                        room=room,
                        recording_id=record_id,
                        defaults={
                            'internal_meeting_id': recording.find('internalMeetingID').text,
                            'creation_date': creation_date,
                            'meta_data': {child.tag: child.text for child in recording},
                            'published': recording.find('published').text.lower() == 'true'
                        }
                    )
                    logger.info(f"Recording {'created' if created else 'updated'}: {record_id}")
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Error saving recording {record_id}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    skipped_count += 1
            else:
                logger.warning(f"Room not found in database for meeting ID: {meeting_id}")
                unknown_rooms.add(meeting_id)
                skipped_count += 1

        logger.info(f"Sync completed. Synced {synced_count} recordings. Skipped {skipped_count} recordings.")
        logger.info(f"Unknown room IDs: {', '.join(unknown_rooms)}")
        return {
            "synced_recordings": synced_count,
            "skipped_recordings": skipped_count,
            "unknown_rooms": list(unknown_rooms),
            "last_sync_time": timezone.now().isoformat()
        }
    else:
        logger.error("API call failed: Unexpected response")
        return {"error": "Unexpected response from BBB server"}
@shared_task
def check_and_end_meetings():
    active_rooms = BigBlueButtonRoom.objects.filter(expiration_date__lte=timezone.now())
    

    for room in active_rooms:
        if is_meeting_running(room.room_id):
            end_meeting(room.room_id, 'mp')

def generate_checksum(api_call, params):
    param_string = urlencode(sorted(params.items()))
    checksum_string = f"{api_call}{param_string}{settings.BBB_SECRET}"
    return hashlib.sha1(checksum_string.encode('utf-8')).hexdigest()