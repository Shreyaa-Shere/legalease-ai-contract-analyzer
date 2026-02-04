from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Contract
from .tasks import process_contract_task  # Import Celery task for async processing
import logging

logger = logging.getLogger(__name__)


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for Contract model."""
    
    # Add computed/read-only fields
    file_size_mb = serializers.ReadOnlyField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id',
            'title',
            'description',
            'file',
            'file_name',
            'file_size',
            'file_size_mb',
            'file_type',
            'status',
            'uploaded_at',
            'analyzed_at',
            'updated_at',
            'uploaded_by',
            'uploaded_by_username',
            'extracted_text',
            'analysis_summary',
            'extracted_clauses',
            'risk_assessment',
            'analysis_metadata',
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'analyzed_at',
            'updated_at',
            'uploaded_by',
            'file_name',
            'file_size',
            'file_type',
            'extracted_text',
            'analysis_summary',
            'extracted_clauses',
            'risk_assessment',
            'analysis_metadata',
        ]
    
    def create(self, validated_data):
        """
        Override create method to set uploaded_by from request user
        and extract file metadata.
        """
        # Get the user from the request context
        user = self.context['request'].user
        
        # Get the uploaded file
        file = validated_data.get('file')
        
        # Create contract instance (don't save yet)
        contract = Contract(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            file=file,
            uploaded_by=user,
        )
        
        # Extract and set file metadata
        if file:
            contract.file_name = file.name
            contract.file_size = file.size
            
            # Determine file type
            file_extension = file.name.lower().split('.')[-1]
            if file_extension == 'pdf':
                contract.file_type = 'pdf'
            elif file_extension == 'docx':
                contract.file_type = 'docx'
        
        contract.status = 'uploaded'
        contract.save()
        
        # Start background task to process the contract asynchronously
        if file and contract.file_type in ['pdf', 'docx']:
            try:
                # Call Celery task asynchronously
                # .delay() sends the task to Celery worker (doesn't wait for result)
                process_contract_task.delay(contract.id)
                logger.info(f"Started background processing task for contract {contract.id}")
            except Exception as e:
                # If Celery is not running, log error but don't crash
                # The contract will remain in 'uploaded' status
                logger.error(f"Failed to start background task for contract {contract.id}: {str(e)}")
                logger.error("Make sure Redis and Celery worker are running!")
                # Optionally, you could fall back to synchronous processing here
                # For now, we'll just log the error
        
        return contract


class ContractListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing contracts (fewer fields for performance).
    """
    file_size_mb = serializers.ReadOnlyField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id',
            'title',
            'description',
            'file_type',
            'status',
            'file_size_mb',
            'uploaded_at',
            'analyzed_at',
            'uploaded_by_username',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates password and creates a new user account.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        """
        Validate that password and password_confirm match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': 'Password fields do not match.',
                'password_confirm': 'Password fields do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user account.
        """
        # Remove password_confirm from validated_data (not needed for user creation)
        validated_data.pop('password_confirm')
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        return user

