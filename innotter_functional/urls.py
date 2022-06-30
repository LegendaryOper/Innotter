from .views import PageViewSet, PostViewSet, TagViewSet, SearchUserViewSet, SearchPageViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter

router = ExtendedSimpleRouter()
router.register(r'pages', PageViewSet, basename='pages')\
    .register('posts', PostViewSet, basename='pages-posts', parents_query_lookups=['page_id'])
router.register('tags', TagViewSet, basename='tags',)
router.register('search/users', SearchUserViewSet, basename='search-user')
router.register('search/pages', SearchPageViewSet, basename='search-user')
urlpatterns = router.urls