from django.urls import path, include

from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register('', views.ApprovalsViewSet)

urlpatterns = [
    path('', views.Home, name= 'home'),
    path('api/', include(router.urls)),
    path('dumify/', views.DumifyData, name= 'dumify'),
    path('status/', views.approvereject),
    #path('formclient/', views.FormClient, name= 'formclient'),
]