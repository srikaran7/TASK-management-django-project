from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('api/', include('tasks.urls')),
    path('api/projects/', include('projects.urls')),

    # API Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # OpenAPI schema
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc UI
   
    path('admin/', admin.site.urls),
]