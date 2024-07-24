from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", include("events.urls")),
    # path("case/", include("case_details.urls")),
    path("driver/", include("driver.urls")),
    path("care/", include("customer_care.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
