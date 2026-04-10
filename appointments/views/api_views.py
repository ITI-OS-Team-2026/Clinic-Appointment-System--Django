from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import DoctorProfile

class DoctorListAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctors = DoctorProfile.objects.select_related('user').all()
        data = []
        for doc in doctors:
            data.append({
                'id': doc.user.id,
                'full_name': f"Dr. {doc.user.get_full_name() or doc.user.username}",
                'specialization': doc.specialization,
                'experience_years': doc.experience_years,
            })
        return Response(data)
