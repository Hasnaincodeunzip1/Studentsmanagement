from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import ExternalLead
from .serializers import ExternalLeadSerializer, ConsolidatedTrainerSuggestionSerializer
from courses.utils import find_available_trainers_extended
from rest_framework.permissions import IsAuthenticated, AllowAny


class ExternalLeadViewSet(viewsets.ModelViewSet):
    queryset = ExternalLead.objects.all()
    serializer_class = ExternalLeadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'webhook':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def get_trainer_suggestions(self, request, pk=None):
        external_lead = self.get_object()
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=6)  # Next 7 days

        all_suggestions = {}
        slots = [external_lead.slot_1, external_lead.slot_2, external_lead.slot_3]
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            for slot in slots:
                if slot:
                    available_trainers = find_available_trainers_extended(
                        start_time=slot,
                        duration=timedelta(minutes=external_lead.duration),
                        start_date=current_date
                    )
                    for trainer_info in available_trainers:
                        trainer_id = trainer_info['trainer'].id
                        if trainer_id not in all_suggestions:
                            all_suggestions[trainer_id] = {
                                'trainer': trainer_info['trainer'],
                                'availability': {}
                            }
                        if current_date not in all_suggestions[trainer_id]['availability']:
                            all_suggestions[trainer_id]['availability'][current_date] = []
                        all_suggestions[trainer_id]['availability'][current_date].append(slot.strftime('%H:%M'))

        # Filter out trainers with no availability
        filtered_suggestions = {
            trainer_id: data
            for trainer_id, data in all_suggestions.items()
            if data['availability']
        }

        # Convert the availability dict to a list of dicts for serialization
        for trainer_id, data in filtered_suggestions.items():
            data['availability'] = [
                {'date': date, 'slots': slots}
                for date, slots in data['availability'].items()
            ]

        serializer = ConsolidatedTrainerSuggestionSerializer(filtered_suggestions.values(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def webhook(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)