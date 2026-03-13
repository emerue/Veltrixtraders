from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

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

if settings.DEBUG == False:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)