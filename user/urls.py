from .views import JSONWebTokenAuthViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tokens', JSONWebTokenAuthViewSet, basename='tokens')
router.register(r'', UserViewSet, basename='users')
urlpatterns = router.urls