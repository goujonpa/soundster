from django.conf.urls import include, url
from django.contrib import admin

from home.views import HomeView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomeView.as_view()),
]
