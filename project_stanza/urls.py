from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from link import views


urlpatterns = [
    path('', views.UpcomingListView.as_view(), name='upcoming-list'),
	url(r'^update/(?P<pk>\d+)/$', views.LinkUpdate.as_view(), name='link_update'),
    path('links/', views.LinkListView.as_view(), name='link-list'),
    path('links/add_link.html', views.LinkCreate.as_view(), name='link-create'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

