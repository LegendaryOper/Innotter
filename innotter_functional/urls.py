from .views import PageViewSet, PostViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter

router = ExtendedSimpleRouter()
router.register(r'pages', PageViewSet, basename='pages')\
    .register('posts', PostViewSet, basename='pages-posts', parents_query_lookups=['page_id'])
urlpatterns = router.urls