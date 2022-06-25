from .views import PageViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pages', PageViewSet, basename='pages')
urlpatterns = router.urls