from .views import JSONWebTokenAuthViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'token', JSONWebTokenAuthViewSet, basename='token')
router.register(r'', UserViewSet, basename='user')
urlpatterns = router.urls