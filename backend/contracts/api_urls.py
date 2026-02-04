from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .api_views import ContractViewSet, register_user

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')

urlpatterns = [
    # Include all routes from the router
    # This creates: /api/contracts/ (list, create)
    #               /api/contracts/{id}/ (retrieve, update, delete)
    #               /api/contracts/{id}/mark_analyzed/ (custom action)
    path('', include(router.urls)),
    
    # User Registration endpoint
    # POST /api/register/ - Register a new user account
    path('register/', register_user, name='register'),
    
    # JWT Authentication endpoints
    # POST /api/token/ - Get access & refresh tokens (login)
    # POST /api/token/refresh/ - Get new access token using refresh token
    # POST /api/token/verify/ - Verify if token is valid
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

