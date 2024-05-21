from django.urls import path, include
from .views import MyObtainTokenPairView, CategoryViewSet, ProductViewSet, GenerateDummyProducts, generate_view
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'category', CategoryViewSet)
router.register(r'product', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('generated-dummy-products/', GenerateDummyProducts.as_view(), name='generated_dummy_products'),
    path('generate/', generate_view, name='generate')
]
