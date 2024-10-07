# external_data/services.py
from datetime import datetime, timedelta
from courses.utils import find_available_trainers_extended
from users.models import User

def generate_trainer_suggestions(external_lead):
    suggestions = []
    trainers = User.objects.filter(role='TRAINER')
    start_date = datetime.now().date()
    
    for i in range(7):  # Check for the next 7 days
        date = start_date + timedelta(days=i)
        for slot in [external_lead.slot_1, external_lead.slot_2, external_lead.slot_3]:
            available_trainers = find_available_trainers_extended(
                start_time=slot,
                duration=timedelta(minutes=external_lead.duration),
                start_date=date
            )
            
            for trainer_info in available_trainers:
                if trainer_info['available_today']:
                    suggestions.append({
                        'trainer': trainer_info['trainer'].id,
                        'trainer_name': trainer_info['trainer'].get_full_name(),
                        'date': date.isoformat(),
                        'time': slot.isoformat(),
                        'duration': external_lead.duration
                    })

    return suggestions