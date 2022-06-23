from .views import JSONWebTokenAuthViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'token', JSONWebTokenAuthViewSet, basename='tokens')
urlpatterns = router.urls