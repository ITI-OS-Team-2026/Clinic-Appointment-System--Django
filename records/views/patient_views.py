from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from appointments.models import Appointment
from records.models import ConsultationRecord
from users.decorators import is_patient

from django.http import HttpResponseForbidden

@user_passes_test(is_patient, login_url='/users/login/')
def patient_consultation_summary(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.patient != request.user:
        return HttpResponseForbidden('Not allowed to view this consultation.')

    if appointment.status != 'COMPLETED':
        return HttpResponseForbidden('Consultation is not completed.')

    consultation = get_object_or_404(ConsultationRecord, appointment=appointment)

    context = {
        'appointment': appointment,
        'consultation': consultation,
        'prescriptions': consultation.prescriptions.all()
    }
    return render(request, 'patient/consultation.html', context)
