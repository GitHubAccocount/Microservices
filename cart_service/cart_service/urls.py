from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from carts.views import CartViewSet


router = DefaultRouter()
router.register(r'carts', CartViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]