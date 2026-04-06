from datetime import date
import re

from rest_framework import serializers
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class PatientRegistrationSerializer(serializers.ModelSerializer):
    VALID_GENDERS = ['Male', 'Female', 'Other']
    VALID_BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    # i have not added (id,role,created_at) because no need for them in the serializer they will not be sent in the request
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = Patient
        fields = [
            # User fields
            'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name',
            # Patient fields
            'date_of_birth', 'blood_type', 'gender', 'address', 'contact_number',
            'emergency_contact_name', 'emergency_contact_number', 'medical_notes'
        ]
        extra_kwargs = {
            'medical_notes': {'required': False, 'allow_blank': True},
            'emergency_contact_name': {'required': False, 'allow_blank': True},
            'emergency_contact_number': {'required': False, 'allow_blank': True},
        }
        
    def validate_username(self,value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
        
    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
        
    def validate_password(self, value):
        if len(value) < 8 or not any(c.isdigit() for c in value) or not any(c.isupper() for c in value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters, contain a number and an uppercase letter."
            )
        return value
        
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data
        
    def validate_date_of_birth(self, value):
        age = (date.today() - value).days // 365

        if value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past.")

        if age < 1:
            raise serializers.ValidationError("Patient must be at least 1 year old.")

        if age > 150:
            raise serializers.ValidationError("Invalid date of birth.")

        return value

    def validate_blood_type(self, value):
        if value not in self.VALID_BLOOD_TYPES:
            raise serializers.ValidationError(
                f"Invalid blood type. Choose from: {', '.join(self.VALID_BLOOD_TYPES)}"
            )
        return value
        
    def validate_gender(self, value):
        if value not in self.VALID_GENDERS:
            raise serializers.ValidationError(
                f"Invalid gender. Choose from: {', '.join(self.VALID_GENDERS)}"
            )
        return value
        
    def validate_contact_number(self, value):
        cleaned = re.sub(r'[\s\-\+\(\)]', '', value)

        if not cleaned.isdigit():
            raise serializers.ValidationError("Invalid contact number format.")

        if len(cleaned) < 10:
            raise serializers.ValidationError("Contact number must have at least 10 digits.")

        return value
        
    def create(self,validated_data):
        data = validated_data.copy()

        user = User.objects.create_user(
            username=data.pop('username'),
            email=data.pop('email'),
            password=data.pop('password'),
            first_name=data.pop('first_name'),
            last_name=data.pop('last_name')
        )

        data.pop('password_confirm', None)
            
        # TODO
        # i will user Group for built in permission system
            
            
        # Link patient profile to the user
        patient=Patient.objects.create(
            user=user,
            **data
            )
        return patient
            