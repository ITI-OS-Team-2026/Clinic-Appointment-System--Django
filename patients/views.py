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
            
            return Response(
                {
                    "message": "Patient registered successfully",
                    "patient": PatientRegistrationSerializer(patient).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)