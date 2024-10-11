from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet, PersonalInfoViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet)
router.register(r'personal-info', PersonalInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
