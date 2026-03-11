from django.contrib import admin
from django.urls import path, include

# Custom error handlers
handler404 = 'VeltrixApp.views.custom_404'
handler403 = 'VeltrixApp.views.custom_403'
handler500 = 'VeltrixApp.views.custom_500'
handler400 = 'VeltrixApp.views.custom_400'
handler405 = 'VeltrixApp.views.custom_405'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('VeltrixApp.urls')),
]
