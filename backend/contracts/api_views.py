from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Contract
from .serializers import ContractSerializer, ContractListSerializer, UserRegistrationSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Contract model - provides CRUD operations via REST API.
    
    ViewSet automatically provides:
    - list() - GET /api/contracts/ (list all)
    - create() - POST /api/contracts/ (create new)
    - retrieve() - GET /api/contracts/{id}/ (get one)
    - update() - PUT /api/contracts/{id}/ (full update)
    - partial_update() - PATCH /api/contracts/{id}/ (partial update)
    - destroy() - DELETE /api/contracts/{id}/ (delete)
    """
    
    permission_classes = [IsAuthenticated]  # Require authentication
    
    def get_queryset(self):
        """
        Filter contracts to show only those uploaded by the current user.
        """
        return Contract.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list, full serializer for detail.
        """
        if self.action == 'list':
            return ContractListSerializer
        return ContractSerializer
    
    def perform_create(self, serializer):
        """
        Override to automatically set uploaded_by to current user.
        The serializer's create method handles this, but we can add extra logic here if needed.
        """
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def mark_analyzed(self, request, pk=None):
        """
        Custom action to mark a contract as analyzed.
        POST /api/contracts/{id}/mark_analyzed/
        """
        contract = self.get_object()
        contract.status = 'analyzed'
        contract.analyzed_at = timezone.now()
        contract.save()
        
        serializer = self.get_serializer(contract)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to register
def register_user(request):
    """
    User registration endpoint.
    
    POST /api/register/
    Body: {
        "username": "newuser",
        "email": "user@example.com",
        "password": "securepassword123",
        "password_confirm": "securepassword123",
        "first_name": "John",  # optional
        "last_name": "Doe"     # optional
    }
    
    Returns: {
        "message": "User registered successfully",
        "user": {
            "id": 1,
            "username": "newuser",
            "email": "user@example.com"
        }
    }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Return success response (don't include password)
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)
    
    # Return validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

