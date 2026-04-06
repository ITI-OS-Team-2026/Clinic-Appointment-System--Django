from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PatientRegistrationSerializer

class PatientRegistrationView(CreateAPIView):
    serializer_class = PatientRegistrationSerializer
    # TODO
    # Add permissions
    
    def create(self,req):
        serializer=self.get_serializer(data=req.data)
        
        if serializer.is_valid():
            patient=serializer.save()
            
            # dont show the password
            response_data = {
                'id': patient.id,
                'username': patient.user.username,
                'email': patient.user.email,
                'first_name': patient.user.first_name,
                'last_name': patient.user.last_name,
                'date_of_birth': patient.date_of_birth,
                'blood_type': patient.blood_type,
                'gender': patient.gender,
                'contact_number': patient.contact_number,
            }
            
            
            return Response(
                {
                    "message": "Patient registered successfully",
                    "patient": response_data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)