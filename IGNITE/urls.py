
from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from . import settings
from django.conf.urls.static import static


urlpatterns = [
    path('index_3_home/',TemplateView.as_view(template_name='products/index_3_home.html'),name='index_3_home'),
    path('admin/', admin.site.urls),
    path('',include('products.urls')),
   
    path('accounts/', include('allauth.urls')),
    

            ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#if settings.DEBUG:
    #urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

