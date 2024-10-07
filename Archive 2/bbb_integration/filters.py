from django_filters import rest_framework as filters
from .models import BigBlueButtonRecording

class BigBlueButtonRecordingFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='creation_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='creation_date', lookup_expr='lte')
    room = filters.CharFilter(field_name='room__room_id')
    course = filters.CharFilter(field_name='room__course__name', lookup_expr='icontains')
    student = filters.CharFilter(method='filter_student')
    trainer = filters.CharFilter(method='filter_trainer')

    class Meta:
        model = BigBlueButtonRecording
        fields = ['start_date', 'end_date', 'room', 'course', 'student', 'trainer']

    def filter_student(self, queryset, name, value):
        return queryset.filter(
            room__student_course__student__username__icontains=value
        ) | queryset.filter(
            room__student_course__student__first_name__icontains=value
        ) | queryset.filter(
            room__student_course__student__last_name__icontains=value
        )

    def filter_trainer(self, queryset, name, value):
        return queryset.filter(
            room__student_course__trainer__username__icontains=value
        ) | queryset.filter(
            room__student_course__trainer__first_name__icontains=value
        ) | queryset.filter(
            room__student_course__trainer__last_name__icontains=value
        )