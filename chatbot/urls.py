from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'chatbot'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)