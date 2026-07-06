from django.urls import path

from core import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("kv/<str:key>/", views.KeyValueView.as_view(), name="key-value"),
]
