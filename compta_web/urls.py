from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.urls import include, path

from inventory.views import ServiceAwareLoginView


urlpatterns = [
    path(
        "admin/inventory/physicalinventory/",
        RedirectView.as_view(url="/admin/", permanent=False),
    ),
    path("admin/", admin.site.urls),
    path(
        "login/",
        ServiceAwareLoginView.as_view(),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("inventory.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
