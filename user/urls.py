from .views import JSONWebTokenAuthViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'token', JSONWebTokenAuthViewSet, basename='token')
urlpatterns = router.urls